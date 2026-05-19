"""
Active Inference model implementation.

This module contains the main ActiveInferenceModel class that orchestrates
all components of active inference including belief updating, policy selection,
and free energy minimization.
"""

import copy
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.belief_updating import BayesianBeliefUpdate
from geo_infer_act.core.types import (
    ActiveInferenceStepResult,
    H3GridInferenceResult,
    H3SpatialConsistency,
    PolicyEvaluation,
)
from geo_infer_act.utils.h3_adapter import (
    edge_count_from_graph,
    get_h3_adapter,
    normalize_belief_vector,
)
from geo_infer_act.utils.math import softmax, normalize_distribution
from geo_infer_act.utils.analysis import ActiveInferenceAnalyzer

logger = logging.getLogger(__name__)


class ActiveInferenceModel:
    """
    Main class for active inference agents with support for nested models.
    """

    def __init__(self, model_type: str = "categorical", **kwargs):
        """
        Initialize an Active Inference model.

        Args:
            model_type: Type of underlying generative model
            **kwargs: Additional parameters
        """
        self.model_type = model_type
        self.parameters = dict(kwargs)
        self.preferences = self.parameters.pop("preferences", None)
        policy_temperature = self.parameters.pop(
            "policy_temperature", self.parameters.pop("temperature", 1.0)
        )
        policy_selection_mode = self.parameters.pop(
            "policy_selection_mode", self.parameters.pop("selection_mode", "sample")
        )
        random_seed = self.parameters.pop("random_seed", None)

        # Initialize core components
        self.generative_model = None
        self.free_energy_calculator = FreeEnergyCalculator()
        self.policy_selector = PolicySelector(
            temperature=policy_temperature,
            selection_mode=policy_selection_mode,
            random_seed=random_seed,
        )
        self.belief_updater = BayesianBeliefUpdate()

        # Analyzer Integration
        self.output_dir = kwargs.get("output_dir", None)
        self.analyzer = None
        if self.output_dir:
            self.analyzer = ActiveInferenceAnalyzer(self.output_dir)
            logger.info(
                f"Active Inference Analyzer enabled. Logging to {self.output_dir}"
            )

        # State variables
        self.current_beliefs = None
        self.current_observations = None
        self.current_actions = None
        self.latest_policy_evaluation: Optional[PolicyEvaluation] = None
        self.latest_policy_selection: Optional[Dict[str, Any]] = None
        self.history: List[Dict[str, Any]] = []

        logger.info(f"Initialized ActiveInferenceModel with type: {model_type}")

    def set_generative_model(self, model: GenerativeModel):
        """Set the generative model for this active inference agent."""
        self.generative_model = model
        if getattr(model, "model_type", None) and model.model_type != self.model_type:
            logger.info(
                "Aligning active inference model type with generative model: %s",
                model.model_type,
            )
            self.model_type = model.model_type
        self.current_beliefs = self._extract_model_beliefs(model)
        if self.preferences is None:
            self.preferences = self._extract_model_preferences(model)

    def perceive(self, observation: np.ndarray) -> np.ndarray:
        """
        Update beliefs based on new observation.

        Args:
            observation: New sensory observation

        Returns:
            Updated beliefs (posterior distribution)
        """
        if self.generative_model is None:
            raise ValueError("Generative model must be set before perception")

        observation = np.asarray(observation, dtype=float).reshape(-1)
        self.current_observations = observation

        updated_beliefs = self._update_beliefs_with_model(observation)
        self.current_beliefs = updated_beliefs

        return self._clone_beliefs(self.current_beliefs)

    def act(self, available_actions: Optional[List[Any]] = None) -> Any:
        """
        Select action based on expected free energy minimization.

        Args:
            available_actions: List of available actions

        Returns:
            Selected action
        """
        if self.generative_model is None:
            raise ValueError("Generative model must be set before action selection")

        # Use pymdp control when the optional backend is installed and the model
        # exposes the full matrix contract expected by pymdp.
        try:
            from pymdp.control import construct_policies, sample_action

            # Check if we have necessary matrices
            A = getattr(self.generative_model, "observation_model", None)
            B = getattr(self.generative_model, "transition_model", None)
            C = getattr(self.generative_model, "preferences", None)

            if A is not None and B is not None and C is not None:
                # Prepare qs (beliefs)
                qs = (
                    self.current_beliefs.get("states")
                    if isinstance(self.current_beliefs, dict)
                    else self.current_beliefs
                )
                # Ensure qs is list of arrays (factors)
                if isinstance(qs, np.ndarray) and qs.dtype != object:
                    qs = [qs]
                elif (
                    isinstance(qs, list)
                    and len(qs) > 0
                    and not isinstance(qs[0], np.ndarray)
                ):
                    # If generic list, convert elements
                    qs = [np.array(q) for q in qs]

                # Get dimensions
                num_controls = getattr(self.generative_model, "num_controls", None)
                if num_controls is None:
                    # Infer from B
                    # B[f] shape is (Ns, Ns, Nu)
                    num_controls = [b.shape[-1] for b in B]

                # Construct policies
                # Use policy_len=1 for simple step, or getattr(self, 'horizon', 1)
                policies = construct_policies(num_controls)

                # Calculate Expected Free Energy (G)
                # We need different G function depending on pymdp version or structure
                # Try inferactively-pymdp common path
                try:
                    from pymdp.control import calculate_G_policies

                    G = calculate_G_policies(A, B, C, qs, policies=policies)

                    # Compute posterior over policies
                    # Q_pi = softmax(-G) basically, or usage of update_posterior_policies
                    from pymdp.inference import update_posterior_policies

                    q_pi, _ = update_posterior_policies(
                        qs, A, B, C, policies, use_utility=True
                    )
                    # Note: update_posterior_policies might re-calc G internaly?
                    # If G is available, some versions allow passing it.
                    # But simpler:
                    q_pi = softmax(-G)

                    # Sample action
                    action = sample_action(
                        q_pi, policies, num_controls, sampling_mode="marginal"
                    )

                    self.current_actions = action
                    return action
                except ImportError:
                    logger.debug(
                        "pymdp control functions not available; using local EFE selector"
                    )
        except (ImportError, Exception) as exc:
            logger.debug("pymdp unavailable for this action selection: %s", exc)

        # Local expected-free-energy implementation.

        # Generate default actions if none provided
        if available_actions is None:
            available_actions = list(
                range(getattr(self.generative_model, "num_controls", [3])[0])
            )

        belief_vector = self._extract_belief_vector(self.current_beliefs)
        if belief_vector is None:
            belief_vector = np.ones(len(available_actions), dtype=float) / len(
                available_actions
            )

        policy_candidates = [
            {
                "action": action,
                "exploration_bonus": self.parameters.get("exploration_bonus", 0.1),
            }
            for action in available_actions
        ]
        policy_info = self.policy_selector.select_policy(
            belief_vector,
            policy_candidates,
            self._get_preferences_vector(len(belief_vector)),
        )
        policy = policy_info.get("policy", policy_info)
        selected_action = policy.get("action", policy)
        self.latest_policy_evaluation = policy_info.get("evaluation")
        self.latest_policy_selection = policy_info

        self.current_actions = selected_action
        return selected_action

    def update_observations(self, observations: Dict[str, Any]) -> None:
        """Update observations for the active inference model."""
        self.current_observations = observations

    def update_preferences(self, preferences: Dict[str, float]) -> None:
        """Update preferences for the active inference model."""
        self.preferences = preferences

    def update_with_outcome(
        self, decision: Dict[str, Any], outcome: Dict[str, Any]
    ) -> None:
        """
        Update model based on decision outcome for learning.

        Stores the decision-outcome pair in history and updates beliefs
        if outcome contains observation data, implementing the
        perception-action loop closure in Active Inference.

        Args:
            decision: The decision/action taken
            outcome: The observed outcome
        """
        self.history.append(
            {
                "decision": decision,
                "outcome": outcome,
                "beliefs_at_decision": self._clone_beliefs(self.current_beliefs),
            }
        )
        if "observation" in outcome:
            obs = np.asarray(outcome["observation"], dtype=float).reshape(-1)
            self.perceive(obs)

    def generate_policies(
        self, available_actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate policy options from available actions."""
        return available_actions

    def select_policy(self, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select optimal policy from candidates."""
        if not policies:
            return {}
        belief_vector = self._extract_belief_vector(self.current_beliefs)
        if belief_vector is None:
            belief_vector = np.ones(len(policies), dtype=float) / len(policies)
        policy_info = self.policy_selector.select_policy(
            belief_vector,
            policies,
            self._get_preferences_vector(len(belief_vector)),
        )
        self.latest_policy_evaluation = policy_info.get("evaluation")
        self.latest_policy_selection = policy_info
        return policy_info.get("policy", {})

    def compute_expected_free_energy(self, policy: Dict[str, Any]) -> float:
        """Compute expected free energy for a given policy.

        Delegates to FreeEnergyCalculator.compute_expected_free_energy using
        the model's current beliefs and preferences. EFE balances epistemic
        value (information gain) and pragmatic value (preference satisfaction).

        Args:
            policy: Policy dict, may contain 'exploration_bonus' and 'risk_preference'

        Returns:
            Expected free energy (float). Lower means the policy is more preferred.
        """
        belief_vector = self._extract_belief_vector(self.current_beliefs)
        if belief_vector is None:
            return float("inf")

        preferences = self._get_preferences_vector(len(belief_vector))

        return self.free_energy_calculator.compute_expected_free_energy(
            belief_vector, policy, preferences
        )

    def step(
        self,
        observation: np.ndarray,
        available_actions: Optional[List[Any]] = None,
        return_result: bool = False,
    ) -> Union[Tuple[np.ndarray, Any], ActiveInferenceStepResult]:
        """
        Perform one complete active inference step.

        Args:
            observation: Current observation
            available_actions: Available actions

        Returns:
            Tuple of (updated_beliefs, selected_action), or an
            ActiveInferenceStepResult when ``return_result`` is true.
        """
        observation_array = np.asarray(observation, dtype=float).reshape(-1)

        # Perception: update beliefs
        beliefs = self.perceive(observation_array)

        # Action: select policy
        action = self.act(available_actions)

        # Store step in history
        step_data = {
            "observation": observation_array.copy(),
            "beliefs": self._clone_beliefs(beliefs),
            "action": action,
            "free_energy": (
                self.compute_free_energy() if beliefs is not None else np.inf
            ),
        }
        self.history.append(step_data)

        # Comprehensive Logging via Analyzer
        if self.analyzer:
            # Gather deep diagnostics
            policies = {
                "selected": (
                    self.latest_policy_evaluation.policy
                    if self.latest_policy_evaluation is not None
                    else action
                ),
                "probability": (
                    self.latest_policy_evaluation.probability
                    if self.latest_policy_evaluation is not None
                    else None
                ),
                "expected_free_energy": (
                    self.latest_policy_evaluation.expected_free_energy
                    if self.latest_policy_evaluation is not None
                    else None
                ),
            }

            metrics = {
                "model_type": self.model_type,
                "free_energy": step_data["free_energy"],
            }

            self.analyzer.record_step(
                beliefs=step_data["beliefs"],
                observations=step_data["observation"],
                actions=action,
                policies=policies,
                free_energy=step_data["free_energy"],
                metrics=metrics,
            )

        if return_result:
            return ActiveInferenceStepResult(
                beliefs=self._clone_beliefs(beliefs),
                action=action,
                free_energy=float(step_data["free_energy"]),
                expected_free_energy=(
                    self.latest_policy_evaluation.expected_free_energy
                    if self.latest_policy_evaluation is not None
                    else None
                ),
                policy_evaluation=self.latest_policy_evaluation,
                observation=observation_array.copy(),
                metadata={
                    "policy_selection": self.latest_policy_selection,
                },
            )

        return beliefs, action

    def compute_free_energy(self) -> float:
        """Compute current variational free energy."""

        # Delegate to GenerativeModel if it supports free energy computation (handles hierarchical etc.)
        if self.generative_model is not None and hasattr(
            self.generative_model, "compute_free_energy"
        ):
            return self.generative_model.compute_free_energy()

        if self.current_beliefs is None:
            return np.inf

        if self.model_type == "categorical":
            belief_vector = self._extract_belief_vector(self.current_beliefs)
            if belief_vector is None:
                return np.inf
            observation_vector = self._get_observation_vector(len(belief_vector))
            preferences = self._get_preferences_vector(len(belief_vector))
            return self.free_energy_calculator.compute_categorical_free_energy(
                belief_vector, observation_vector, preferences
            )

        if self.model_type == "gaussian":
            gaussian_beliefs = self._ensure_gaussian_beliefs(self.current_beliefs)
            if gaussian_beliefs is None or self.current_observations is None:
                return np.inf
            gaussian_preferences = self._get_gaussian_preferences()
            return self.free_energy_calculator.compute_gaussian_free_energy(
                gaussian_beliefs["mean"],
                gaussian_beliefs["precision"],
                self.current_observations,
                gaussian_preferences.get("mean"),
                gaussian_preferences.get("precision"),
            )

        return np.inf

    def reset(self):
        """Reset the model to initial state."""
        if self.generative_model is not None:
            self.current_beliefs = self._extract_model_beliefs(self.generative_model)
        else:
            self.current_beliefs = None

        self.current_observations = None
        self.current_actions = None
        self.latest_policy_evaluation = None
        self.latest_policy_selection = None
        self.history = []

    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete history of interactions."""
        return [copy.deepcopy(entry) for entry in self.history]

    def get_current_state(self) -> Dict[str, Any]:
        """Get current model state."""
        return {
            "beliefs": self._clone_beliefs(self.current_beliefs),
            "observations": (
                self.current_observations.copy()
                if isinstance(self.current_observations, np.ndarray)
                else self.current_observations
            ),
            "actions": self.current_actions,
            "free_energy": self.compute_free_energy(),
            "model_type": self.model_type,
        }

    def apply_to_h3(self, h3_obs: Dict[str, np.ndarray], return_result: bool = False):
        """
        Update a spatial generative model from H3-indexed observations.

        This is the canonical ACT entry point for H3 belief updates. It requires
        a spatially enabled ``GenerativeModel``, validates real H3 v4 cell IDs
        through the model, normalizes per-cell beliefs, and returns finite
        aggregate free-energy and spatial-consistency diagnostics.

        Args:
            h3_obs: Mapping of H3 cell IDs to observation vectors.
            return_result: Return ``H3BeliefUpdateResult`` when true.

        Returns:
            Result returned by ``GenerativeModel.update_h3_beliefs`` containing
            per-cell beliefs, aggregate beliefs, and spatial consistency metrics.
        """
        if self.generative_model is None:
            raise ValueError("Set generative model first")
        return self.generative_model.update_h3_beliefs(
            h3_obs, return_result=return_result
        )

    def infer_over_h3_grid(self, h3_grid: Dict[str, Any], return_result: bool = False):
        """
        Run independent one-step inference across an H3 observation grid.

        The method preserves the agent's current beliefs, observations, action,
        and interaction history after evaluating each cell, so callers can use
        it as read-only spatial scoring.

        Cell identifiers are validated with the ACT H3 adapter, policy
        selection is evaluated via expected free energy for each cell, and typed
        mode returns per-cell ``ActiveInferenceStepResult`` objects plus an
        ``H3SpatialConsistency`` summary.

        Args:
            h3_grid: Mapping of H3 cell IDs to observation vectors.
            return_result: Return ``H3GridInferenceResult`` when true.

        Returns:
            Mapping of each cell to updated beliefs, selected action,
            free-energy value, and precision diagnostic, or a typed grid
            inference result when ``return_result`` is true.
        """
        adapter = get_h3_adapter()
        observations_by_cell = {str(cell): obs for cell, obs in h3_grid.items()}
        observed_cells = adapter.validate_cells(observations_by_cell.keys())
        results = {}
        typed_results: Dict[str, ActiveInferenceStepResult] = {}
        original_beliefs = self._clone_beliefs(self.current_beliefs)
        original_observations = (
            self.current_observations.copy()
            if isinstance(self.current_observations, np.ndarray)
            else self.current_observations
        )
        original_actions = self.current_actions
        original_policy_evaluation = self.latest_policy_evaluation
        original_policy_selection = self.latest_policy_selection
        history_len = len(self.history)

        try:
            for cell in observed_cells:
                obs = observations_by_cell[cell]
                step_result = self.step(obs, return_result=True)
                typed_results[cell] = step_result
                results[cell] = {
                    "beliefs": self._clone_beliefs(step_result.beliefs),
                    "action": step_result.action,
                    "free_energy": step_result.free_energy,
                    "expected_free_energy": step_result.expected_free_energy,
                    "policy_evaluation": step_result.policy_evaluation,
                    "precision": (
                        self.current_beliefs.get("precision", 1.0)
                        if isinstance(self.current_beliefs, dict)
                        else 1.0
                    ),
                }
        finally:
            self.current_beliefs = original_beliefs
            self.current_observations = original_observations
            self.current_actions = original_actions
            self.latest_policy_evaluation = original_policy_evaluation
            self.latest_policy_selection = original_policy_selection
            if len(self.history) > history_len:
                self.history = self.history[:history_len]

        if return_result:
            cell_beliefs = {
                cell: self._extract_belief_vector(result.beliefs)
                for cell, result in typed_results.items()
            }
            spatial_consistency = self._compute_h3_grid_consistency(cell_beliefs)
            aggregate_free_energy = (
                float(
                    np.mean([result.free_energy for result in typed_results.values()])
                )
                if typed_results
                else 0.0
            )
            return H3GridInferenceResult(
                cell_results=typed_results,
                aggregate_free_energy=aggregate_free_energy,
                spatial_consistency=spatial_consistency,
                metadata={
                    "adapter_source": adapter.source,
                    "h3_resolution": (
                        adapter.get_resolution(observed_cells[0])
                        if observed_cells
                        else None
                    ),
                },
            )

        return results

    def _compute_h3_grid_consistency(
        self, cell_beliefs: Dict[str, Optional[np.ndarray]]
    ) -> H3SpatialConsistency:
        """Compute spatial consistency for an H3 grid inference result."""
        valid_beliefs = {
            cell: normalize_belief_vector(belief)
            for cell, belief in cell_beliefs.items()
            if belief is not None
        }
        if not valid_beliefs:
            return H3SpatialConsistency(
                global_coherence=0.0,
                neighbor_correlations=0.0,
                cell_count=0,
                edge_count=0,
            )

        cells = set(valid_beliefs)
        graph = {}
        if self.generative_model is not None and isinstance(
            getattr(self.generative_model, "spatial_graph", None), dict
        ):
            graph = {
                cell: {neighbor for neighbor in neighbors if neighbor in cells}
                for cell, neighbors in self.generative_model.spatial_graph.items()
                if cell in cells
            }
        else:
            adapter = get_h3_adapter()
            graph = {
                cell: {
                    neighbor
                    for neighbor in adapter.grid_ring(cell, 1)
                    if neighbor in cells
                }
                for cell in cells
            }

        belief_matrix = np.vstack(list(valid_beliefs.values()))
        global_coherence = float(
            np.clip(1.0 - np.mean(np.std(belief_matrix, axis=0)), 0.0, 1.0)
        )
        correlations = []
        for cell, neighbors in graph.items():
            source = valid_beliefs[cell]
            for neighbor in neighbors:
                target = valid_beliefs[neighbor]
                if np.std(source) <= 1e-12 or np.std(target) <= 1e-12:
                    correlations.append(1.0 if np.allclose(source, target) else 0.0)
                else:
                    correlations.append(float(np.corrcoef(source, target)[0, 1]))
        neighbor_correlations = (
            float(np.nanmean(correlations)) if correlations else global_coherence
        )
        return H3SpatialConsistency(
            global_coherence=global_coherence,
            neighbor_correlations=neighbor_correlations,
            cell_count=len(valid_beliefs),
            edge_count=edge_count_from_graph(graph),
        )

    def set_preferences(self, preferences: Union[np.ndarray, Dict[str, Any]]):
        """Override prior preferences used during inference."""
        self.preferences = preferences

    def _extract_model_beliefs(self, model: GenerativeModel):
        beliefs = getattr(model, "beliefs", None)
        if beliefs is None:
            s_dim = getattr(model, "state_dim", None)
            if s_dim is None:
                s_dim = getattr(model, "num_states", 0)

            if self.model_type == "categorical" and (
                isinstance(s_dim, int)
                and s_dim > 0
                or isinstance(s_dim, list)
                and len(s_dim) > 0
            ):
                if isinstance(s_dim, list):
                    return {
                        "states": [normalize_distribution(np.ones(d)) for d in s_dim]
                    }
                return {"states": normalize_distribution(np.ones(s_dim))}
            if self.model_type == "gaussian" and (
                isinstance(s_dim, int)
                and s_dim > 0
                or isinstance(s_dim, list)
                and len(s_dim) > 0
            ):
                if isinstance(s_dim, list):
                    s_dim = s_dim[0]  # Simplify for gaussian
                precision = np.eye(s_dim) * getattr(model, "prior_precision", 1.0)
                return {"mean": np.zeros(s_dim), "precision": precision}
            return None

        if isinstance(beliefs, dict):
            if self.model_type == "categorical":
                if "states" in beliefs:
                    # Return list/array structure as is, just wrapped in dict if not already
                    return {"states": beliefs["states"]}
                for value in beliefs.values():
                    if isinstance(value, dict) and "states" in value:
                        return {"states": value["states"]}
            if (
                self.model_type == "gaussian"
                and "mean" in beliefs
                and "precision" in beliefs
            ):
                return {
                    "mean": np.asarray(beliefs["mean"], dtype=float).copy(),
                    "precision": np.asarray(beliefs["precision"], dtype=float).copy(),
                }

        if isinstance(beliefs, (np.ndarray, list)):
            return {"states": beliefs}

        return None

    def _extract_model_preferences(self, model: GenerativeModel):
        prefs = getattr(model, "preferences", None)
        if prefs is None:
            return None
        if isinstance(prefs, dict):
            if self.model_type == "categorical":
                extracted: Dict[str, Any] = {}
                if "states" in prefs:
                    extracted["states"] = normalize_distribution(
                        self._safe_flatten(prefs["states"])
                    )
                if "observations" in prefs:
                    extracted["observations"] = normalize_distribution(
                        self._safe_flatten(prefs["observations"])
                    )
                return extracted or None
            if self.model_type == "gaussian":
                result: Dict[str, Any] = {}
                if "mean" in prefs:
                    result["mean"] = np.asarray(prefs["mean"], dtype=float).copy()
                if "precision" in prefs:
                    result["precision"] = np.asarray(
                        prefs["precision"], dtype=float
                    ).copy()
                return result or None
        if isinstance(prefs, (np.ndarray, list)):
            # Safe flatten handles list or object array
            return normalize_distribution(self._safe_flatten(prefs))
        return None

    def _update_beliefs_with_model(self, observation: np.ndarray):
        if self.generative_model is None:
            raise ValueError("Generative model must be set before perception")

        try:
            if self.model_type == "categorical":
                updated = self.generative_model.update_beliefs(
                    {"observations": observation}
                )

                # Check for hierarchical structure
                if isinstance(updated, dict) and any(
                    k.startswith("level_") for k in updated.keys()
                ):
                    return updated

                if isinstance(updated, dict) and "states" in updated:
                    # Return consistent dict structure
                    vec = normalize_distribution(self._safe_flatten(updated["states"]))
                    return {"states": vec}
                if isinstance(updated, np.ndarray):
                    vec = normalize_distribution(updated.astype(float))
                    return {"states": vec}
            elif self.model_type == "gaussian":
                updated = self.generative_model.update_beliefs(
                    {"observations": observation}
                )
                if (
                    isinstance(updated, dict)
                    and "mean" in updated
                    and "precision" in updated
                ):
                    return {
                        "mean": np.asarray(updated["mean"], dtype=float).copy(),
                        "precision": np.asarray(
                            updated["precision"], dtype=float
                        ).copy(),
                    }
        except Exception as exc:  # pragma: no cover - defensive path
            logger.debug("Falling back to local belief update: %s", exc)

        return self._update_beliefs_direct(observation)

    def _update_beliefs_direct(self, observation: np.ndarray):
        if self.current_beliefs is None:
            self.current_beliefs = self._extract_model_beliefs(self.generative_model)

        # PYMDP Integration Check
        if self.model_type == "categorical":
            A = getattr(self.generative_model, "observation_model", None)

            # Safely get prior
            if isinstance(self.current_beliefs, dict):
                prior = self.current_beliefs.get("states")
            else:
                prior = self.current_beliefs  # Assume it's the states array/list

            # Check if using pymdp style (A is object array or list of arrays)
            if (isinstance(A, np.ndarray) and A.dtype == object) or isinstance(A, list):
                try:
                    from pymdp.inference import update_posterior_states

                    # Convert observation to int/list of ints if needed
                    # Observation comes in as float array usually in this codebase
                    # But proper pymdp expects integers for categorical observations
                    obs_indices = (
                        [int(o) for o in observation]
                        if isinstance(observation, (list, np.ndarray))
                        else [int(observation)]
                    )

                    # Update beliefs using pymdp
                    qs = update_posterior_states(A, obs_indices, prior_beliefs=prior)

                    # Update internal state clearly
                    self.current_beliefs = {"states": qs}
                    return {"states": qs}
                except (ImportError, Exception) as e:
                    logger.debug(f"Pymdp update failed: {e}")

            # Local Bayes update for simple categorical matrices.
            prior_vec = self._extract_belief_vector(
                self.current_beliefs
            )  # Will extract from dict or array
            if isinstance(A, np.ndarray) and A.dtype != object:
                if prior_vec is None:
                    return None
                if A.shape[1] != len(prior_vec):
                    raise ValueError(
                        "Observation model state dimension does not match beliefs: "
                        f"A.shape={A.shape}, beliefs={len(prior_vec)}"
                    )
                updated_beliefs = self.belief_updater.update_categorical(
                    prior_vec, observation, self.generative_model.observation_model
                )
                self.current_beliefs = {"states": updated_beliefs}
                return self.current_beliefs

        if self.model_type == "gaussian":
            gaussian_beliefs = self._ensure_gaussian_beliefs(self.current_beliefs)
            if gaussian_beliefs is None or not isinstance(
                self.generative_model.observation_model, dict
            ):
                return self.current_beliefs
            observation_model = self.generative_model.observation_model
            return self.belief_updater.update_gaussian(
                gaussian_beliefs["mean"],
                gaussian_beliefs["precision"],
                observation,
                observation_model.get("C", np.eye(len(gaussian_beliefs["mean"]))),
                np.linalg.inv(observation_model.get("R", np.eye(len(observation)))),
            )

        return self.current_beliefs

    def _safe_flatten(self, data: Any) -> Optional[np.ndarray]:
        """Safely flatten data that might be a list of arrays or object array."""
        if data is None:
            return None

        if isinstance(data, dict):
            try:
                # Recursively flatten values
                arrays = [self._safe_flatten(v) for v in data.values()]
                return np.concatenate(arrays)
            except Exception:
                logger.debug(
                    "Dict flattening failed, falling through to list/array handler"
                )

        if isinstance(data, (list, tuple)):
            try:
                arrays = [np.asarray(x, dtype=float).reshape(-1) for x in data]
                return np.concatenate(arrays)
            except Exception:
                return np.asarray(data, dtype=float).reshape(-1)

        if isinstance(data, np.ndarray):
            if data.dtype == object:
                try:
                    arrays = [np.asarray(x, dtype=float).reshape(-1) for x in data.flat]
                    return np.concatenate(arrays)
                except Exception:
                    logger.debug(
                        "Object array element conversion failed, treating as flat float array"
                    )
            return np.asarray(data, dtype=float).reshape(-1)

        return np.array([float(data)])

    def _extract_belief_vector(self, beliefs: Any) -> Optional[np.ndarray]:
        if beliefs is None:
            return None
        if isinstance(beliefs, dict) and "states" in beliefs:
            return normalize_distribution(self._safe_flatten(beliefs["states"]))
        return normalize_distribution(self._safe_flatten(beliefs))

    def _ensure_gaussian_beliefs(self, beliefs: Any) -> Optional[Dict[str, np.ndarray]]:
        if isinstance(beliefs, dict) and "mean" in beliefs and "precision" in beliefs:
            return {
                "mean": np.asarray(beliefs["mean"], dtype=float),
                "precision": np.asarray(beliefs["precision"], dtype=float),
            }
        if self.generative_model is not None:
            gm_beliefs = getattr(self.generative_model, "beliefs", None)
            if (
                isinstance(gm_beliefs, dict)
                and "mean" in gm_beliefs
                and "precision" in gm_beliefs
            ):
                return {
                    "mean": np.asarray(gm_beliefs["mean"], dtype=float),
                    "precision": np.asarray(gm_beliefs["precision"], dtype=float),
                }
        return None

    def _get_preferences_vector(self, length: Optional[int] = None) -> np.ndarray:
        vector = None

        # 1. Try to get state preferences directly
        if (
            self.preferences is not None
            and isinstance(self.preferences, dict)
            and "states" in self.preferences
        ):
            vector = self._safe_flatten(self.preferences["states"])

        if vector is None and self.generative_model is not None:
            model_prefs = self._extract_model_preferences(self.generative_model)
            if isinstance(model_prefs, dict) and "states" in model_prefs:
                vector = self._safe_flatten(model_prefs["states"])
            elif isinstance(model_prefs, np.ndarray):
                vector = self._safe_flatten(model_prefs)

        # 2. If no state preferences, try to map observation preferences to states
        if vector is None:
            obs_prefs = None
            if (
                self.preferences
                and isinstance(self.preferences, dict)
                and "observations" in self.preferences
            ):
                obs_prefs = self._safe_flatten(self.preferences["observations"])
            elif self.generative_model is not None:
                model_prefs = self._extract_model_preferences(self.generative_model)
                if isinstance(model_prefs, dict) and "observations" in model_prefs:
                    obs_prefs = self._safe_flatten(model_prefs["observations"])

            if obs_prefs is not None:
                # Use A matrix to map preferences: P(s) propto A.T @ P(o)
                observation_model = getattr(
                    self.generative_model, "observation_model", None
                )
                # Also support 'A' attribute directly if observation_model isn't set
                if observation_model is None:
                    observation_model = getattr(self.generative_model, "A", None)

                if isinstance(observation_model, np.ndarray):
                    # Verify dimensions
                    # A is (obs_dim, state_dim)
                    # obs_prefs is (obs_dim)
                    if observation_model.shape[0] == len(obs_prefs):
                        vector = observation_model.T @ obs_prefs

        # 3. Use a uniform preference vector when no preferences are configured.
        if vector is None:
            belief_vector = self._extract_belief_vector(self.current_beliefs)
            default_length = (
                length
                if length is not None
                else (len(belief_vector) if belief_vector is not None else 1)
            )
            vector = np.ones(default_length) / max(default_length, 1)

        if length is not None:
            vector = self._align_vector(vector, length)

        return normalize_distribution(vector)

    def _get_gaussian_preferences(self) -> Dict[str, np.ndarray]:
        prefs: Dict[str, np.ndarray] = {}
        if isinstance(self.preferences, dict):
            if "mean" in self.preferences:
                prefs["mean"] = np.asarray(self.preferences["mean"], dtype=float)
            if "precision" in self.preferences:
                prefs["precision"] = np.asarray(
                    self.preferences["precision"], dtype=float
                )
        if not prefs and self.generative_model is not None:
            gm_prefs = getattr(self.generative_model, "preferences", {})
            if isinstance(gm_prefs, dict):
                if "mean" in gm_prefs:
                    prefs["mean"] = np.asarray(gm_prefs["mean"], dtype=float)
                if "precision" in gm_prefs:
                    prefs["precision"] = np.asarray(gm_prefs["precision"], dtype=float)
        return prefs

    def _get_observation_vector(self, length: int) -> np.ndarray:
        if isinstance(self.current_observations, np.ndarray):
            obs = self.current_observations
        elif self.generative_model is not None:
            obs_dim = getattr(self.generative_model, "obs_dim", length)
            obs = np.ones(obs_dim) / max(obs_dim, 1)
        else:
            obs = np.ones(length) / max(length, 1)

        obs = np.asarray(obs, dtype=float).reshape(-1)
        if len(obs) != length:
            obs = self._align_vector(obs, length)
        return normalize_distribution(obs)

    def _align_vector(self, vector: np.ndarray, length: int) -> np.ndarray:
        # Ensure input is at least 1D
        vector = np.atleast_1d(vector)

        if len(vector) == length:
            return vector
        if len(vector) < length:
            padding = np.zeros(length - len(vector))
            return np.concatenate([vector, padding])
        return vector[:length]

    def _clone_beliefs(self, beliefs: Any):
        if isinstance(beliefs, np.ndarray):
            return beliefs.copy()
        if isinstance(beliefs, dict):
            return {key: self._clone_beliefs(value) for key, value in beliefs.items()}
        return copy.deepcopy(beliefs)
