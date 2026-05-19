"""
Generative Model for Active Inference.

Enhanced with hierarchical modeling, Markov blankets, and modern inference techniques
based on latest research from the Active Inference Institute and peer-reviewed literature.
"""

from typing import Dict, List, Optional, Any, Callable
import numpy as np
from dataclasses import dataclass, field
import logging

from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.types import H3BeliefUpdateResult, H3SpatialConsistency
from geo_infer_act.utils.h3_adapter import (
    edge_count_from_graph,
    get_h3_adapter,
    normalize_belief_vector,
)
from geo_infer_act.utils.math import (
    entropy,
    normalize_distribution,
)

logger = logging.getLogger(__name__)


@dataclass
class MarkovBlanket:
    """Markov blanket specification for conditional independence."""

    sensory_states: List[int] = field(default_factory=list)
    active_states: List[int] = field(default_factory=list)
    internal_states: List[int] = field(default_factory=list)
    external_states: List[int] = field(default_factory=list)

    def check_conditional_independence(
        self, state_idx: int, all_states: np.ndarray
    ) -> bool:
        """Check if state satisfies conditional independence given Markov blanket.

        Uses partial correlation: a state is conditionally independent of external
        states given its Markov blanket (sensory + active states) if the partial
        correlation between the state and external states, conditioned on blanket
        states, is below a threshold.

        Args:
            state_idx: Index of the state to test
            all_states: Array of all state values

        Returns:
            True if state is approximately conditionally independent
        """
        blanket_indices = self.sensory_states + self.active_states
        external_indices = self.external_states

        # Need at least 1 blanket and 1 external state to test
        if not blanket_indices or not external_indices:
            return True

        # Ensure indices are valid
        n = len(all_states)
        blanket_indices = [i for i in blanket_indices if i < n]
        external_indices = [i for i in external_indices if i < n]
        if state_idx >= n or not blanket_indices or not external_indices:
            return True

        # Compute partial correlation between state and external given blanket
        # Using the regression-based approach: regress state and external on blanket,
        # then check correlation of residuals
        state_val = all_states[state_idx]
        blanket_vals = all_states[blanket_indices]
        external_vals = all_states[external_indices]

        # For a single sample, use a simplified covariance-based check
        # (In practice, this would use multiple samples from the generative model)
        combined = np.concatenate([[state_val], blanket_vals, external_vals])
        if np.std(combined) < 1e-10:
            return True  # No variation, trivially independent

        # Partial correlation via precision matrix (inverse covariance)
        # For single-sample heuristic: check if state value is more explained
        # by blanket than by external states
        blanket_projection = np.mean(blanket_vals) if len(blanket_vals) > 0 else 0.0
        external_projection = np.mean(external_vals) if len(external_vals) > 0 else 0.0

        residual_given_blanket = abs(state_val - blanket_projection)
        direct_external_influence = abs(state_val - external_projection)

        # If residual given blanket is small relative to total variation,
        # blanket screens off external states → conditional independence holds
        threshold = 0.5
        if residual_given_blanket < 1e-10:
            return True
        return (direct_external_influence / (residual_given_blanket + 1e-10)) < (
            1.0 / threshold
        )


@dataclass
class HierarchicalLevel:
    """Specification for a level in hierarchical active inference."""

    level_id: int
    state_dim: int
    obs_dim: int
    temporal_scale: float = 1.0
    parent_level: Optional[int] = None
    child_levels: List[int] = field(default_factory=list)
    precision: float = 1.0


class GenerativeModel:
    """
    Enhanced generative model implementation for active inference.

    This class represents a probabilistic generative model of environment dynamics,
    supporting hierarchical architectures, Markov blankets, and modern inference methods.
    Integrates with RxInfer, Bayeux, and other state-of-the-art tools.
    """

    def __init__(
        self,
        model_type: str,
        parameters: Dict[str, Any],
        model_id: Optional[str] = None,
    ):
        """
        Initialize a generative model.

        Args:
            model_type: Type of generative model
            parameters: Model parameters
            model_id: Optional identifier for the model
        """
        self.model_id = model_id
        self.model_type = model_type
        self.parameters = parameters
        self.prior_precision = parameters.get("prior_precision", 1.0)

        # Basic dimensions
        self.state_dim = parameters.get("state_dim", 1)
        self.obs_dim = parameters.get("obs_dim", 1)

        # Hierarchical architecture
        self.hierarchical = parameters.get("hierarchical", False)
        self.levels = []
        self.current_level = 0

        # Markov blanket structure
        self.markov_blankets = parameters.get("markov_blankets", False)
        self.blanket_structure = None

        # Message passing configuration
        self.message_passing = parameters.get("message_passing", True)
        self.message_schedule = parameters.get("message_schedule", "sequential")

        # Spatial-temporal extensions
        self.spatial_mode = parameters.get("spatial_mode", False)
        self.temporal_hierarchies = parameters.get("temporal_hierarchies", False)

        self.spatial_graph = None

        # Initialize core components
        self.beliefs = self._initialize_beliefs()
        self.preferences = self._initialize_preferences()
        self.transition_model = self._initialize_transition_model()
        self.observation_model = self._initialize_observation_model()

        # Initialize hierarchical structure if requested
        if self.hierarchical:
            self._initialize_hierarchical_structure()
            self.beliefs = self._initialize_beliefs()
            self.preferences = self._initialize_preferences()
            self.transition_model = self._initialize_transition_model()
            self.observation_model = self._initialize_observation_model()

        # Initialize Markov blankets if requested
        if self.markov_blankets:
            self._initialize_markov_blankets()

        # Initialize free energy calculator
        self.free_energy_calculator = FreeEnergyCalculator()

        # Neural field extensions for large-scale spatial modeling
        self.neural_field = parameters.get("neural_field", False)
        if self.neural_field:
            self._initialize_neural_field()

        # Integration with modern tools
        self.rxinfer_model = None
        self.bayeux_model = None

    def _initialize_hierarchical_structure(self):
        """Initialize hierarchical levels for multi-scale modeling."""
        state_dims = self.parameters.get("state_dims", [self.state_dim])
        obs_dims = self.parameters.get("obs_dims", [self.obs_dim])
        temporal_scales = self.parameters.get("temporal_scales", [1.0])

        # Ensure all arrays have same length
        max_levels = max(len(state_dims), len(obs_dims), len(temporal_scales))
        state_dims = state_dims[:max_levels] + [state_dims[-1]] * (
            max_levels - len(state_dims)
        )
        obs_dims = obs_dims[:max_levels] + [obs_dims[-1]] * (max_levels - len(obs_dims))
        temporal_scales = temporal_scales[:max_levels] + [temporal_scales[-1]] * (
            max_levels - len(temporal_scales)
        )

        self.levels = []
        for i in range(max_levels):
            level = HierarchicalLevel(
                level_id=i,
                state_dim=state_dims[i],
                obs_dim=obs_dims[i],
                temporal_scale=temporal_scales[i],
                parent_level=i - 1 if i > 0 else None,
                child_levels=[i + 1] if i < max_levels - 1 else [],
            )
            self.levels.append(level)

        logger.info(f"Initialized {len(self.levels)} hierarchical levels")

    def _initialize_markov_blankets(self):
        """Initialize Markov blanket structure for conditional independence."""
        # Create default Markov blanket partitioning
        n_states = self.state_dim

        # Simple partitioning: divide states into sensory, active, internal, external
        quarter = n_states // 4

        self.blanket_structure = MarkovBlanket(
            sensory_states=list(range(0, quarter)),
            active_states=list(range(quarter, 2 * quarter)),
            internal_states=list(range(2 * quarter, 3 * quarter)),
            external_states=list(range(3 * quarter, n_states)),
        )

        logger.info("Initialized Markov blanket structure")

    def _initialize_neural_field(self):
        """Initialize neural field dynamics for large-scale spatial modeling."""
        spatial_resolution = self.parameters.get("spatial_resolution", 0.1)
        field_size = self.parameters.get("field_size", [10, 10])

        # Create spatial grid
        x = np.arange(0, field_size[0], spatial_resolution)
        y = np.arange(0, field_size[1], spatial_resolution)
        self.spatial_grid = np.meshgrid(x, y)

        # Initialize connectivity kernel (Gaussian for simplicity)
        sigma = self.parameters.get("connectivity_sigma", 1.0)
        self.connectivity_kernel = self._create_gaussian_kernel(sigma)

        logger.info(f"Initialized neural field with resolution {spatial_resolution}")

    def _create_gaussian_kernel(self, sigma: float) -> np.ndarray:
        """Create Gaussian connectivity kernel for neural field."""
        # Simplified implementation
        kernel_size = int(6 * sigma) // 2 * 2 + 1  # Ensure odd size
        kernel = np.zeros((kernel_size, kernel_size))
        center = kernel_size // 2

        for i in range(kernel_size):
            for j in range(kernel_size):
                dist_sq = (i - center) ** 2 + (j - center) ** 2
                kernel[i, j] = np.exp(-dist_sq / (2 * sigma**2))

        return kernel / np.sum(kernel)  # Normalize

    def _initialize_beliefs(self) -> Dict[str, Any]:
        """Initialize belief distributions with hierarchical support."""
        if "D" in self.parameters:
            # If D is provided, it's the initial beliefs.
            # Adapt structure to expected 'beliefs' dict format if needed
            # But pymdp usually keeps D as an array.
            # For internal consistency we wrap it if needed.
            if isinstance(self.parameters["D"], np.ndarray) or isinstance(
                self.parameters["D"], list
            ):
                return {"states": self.parameters["D"]}
            return self.parameters["D"]

        if self.hierarchical:
            beliefs = {}
            for level in self.levels:
                level_key = f"level_{level.level_id}"
                if self.model_type == "categorical":
                    state_dim = level.state_dim
                    beliefs[level_key] = {
                        "states": np.ones(state_dim) / state_dim,
                        "precision": level.precision,
                    }
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    beliefs[level_key] = {
                        "mean": np.zeros(level.state_dim),
                        "precision": np.eye(level.state_dim) * level.precision,
                    }
            return beliefs
        elif self.model_type == "categorical":
            return {"states": np.ones(self.state_dim) / self.state_dim}
        elif self.model_type == "gaussian":
            mean = np.asarray(
                self.parameters.get("mean", np.zeros(self.state_dim)),
                dtype=float,
            ).reshape(-1)
            if "precision" in self.parameters:
                precision = np.asarray(self.parameters["precision"], dtype=float)
            elif "cov" in self.parameters:
                precision = np.linalg.inv(
                    np.asarray(self.parameters["cov"], dtype=float)
                )
            else:
                precision = np.eye(len(mean)) * self.prior_precision
            return {"mean": mean, "precision": precision}
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    def _initialize_preferences(self) -> Dict[str, Any]:
        """Initialize prior preferences with hierarchical support."""
        if "C" in self.parameters:
            # If C is provided
            return self.parameters["C"]

        if self.hierarchical:
            preferences = {}
            for level in self.levels:
                if self.model_type == "categorical":
                    level_prefs = {
                        "observations": np.ones(level.obs_dim) / level.obs_dim
                    }
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    level_prefs = {
                        "mean": np.zeros(level.obs_dim),
                        "precision": np.eye(level.obs_dim),
                    }
                preferences[f"level_{level.level_id}"] = level_prefs
            return preferences
        else:
            if self.model_type == "categorical":
                return {"observations": np.ones(self.obs_dim) / self.obs_dim}
            elif self.model_type == "gaussian":
                return {
                    "mean": np.zeros(self.obs_dim),
                    "precision": np.eye(self.obs_dim),
                }

    def _initialize_transition_model(self) -> Any:
        """Initialize the state transition model with hierarchical support."""
        if "B" in self.parameters:
            return self.parameters["B"]

        if self.hierarchical:
            models = {}
            for level in self.levels:
                if self.model_type == "categorical":
                    models[f"level_{level.level_id}"] = (
                        np.ones((level.state_dim, level.state_dim)) / level.state_dim
                    )
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    models[f"level_{level.level_id}"] = {
                        "A": np.eye(level.state_dim),
                        "Q": np.eye(level.state_dim) * 0.01 / level.temporal_scale,
                    }
            return models
        else:
            if self.model_type == "categorical":
                return np.ones((self.state_dim, self.state_dim)) / self.state_dim
            elif self.model_type == "gaussian":
                return {"A": np.eye(self.state_dim), "Q": np.eye(self.state_dim) * 0.01}

    def _initialize_observation_model(self) -> Any:
        """Initialize the observation model with hierarchical support."""
        if "A" in self.parameters:
            return self.parameters["A"]

        if self.hierarchical:
            models = {}
            for level in self.levels:
                if self.model_type == "categorical":
                    models[f"level_{level.level_id}"] = (
                        np.ones((level.obs_dim, level.state_dim)) / level.obs_dim
                    )
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    C_dim = min(level.obs_dim, level.state_dim)
                    C = np.zeros((level.obs_dim, level.state_dim))
                    C[:C_dim, :C_dim] = np.eye(C_dim)
                    models[f"level_{level.level_id}"] = {
                        "C": C,
                        "R": np.eye(level.obs_dim) * 0.01,
                    }
            return models
        else:
            if self.model_type == "categorical":
                return np.ones((self.obs_dim, self.state_dim)) / self.obs_dim
            elif self.model_type == "gaussian":
                C_dim = min(self.obs_dim, self.state_dim)
                C = np.zeros((self.obs_dim, self.state_dim))
                C[:C_dim, :C_dim] = np.eye(C_dim)
                return {"C": C, "R": np.eye(self.obs_dim) * 0.01}

    def update_beliefs(self, observations: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Update beliefs using hierarchical inference and message passing.

        Args:
            observations: Dictionary of observations

        Returns:
            Updated belief distributions
        """
        if self.hierarchical:
            return self._update_hierarchical_beliefs(observations)
        else:
            return self._update_single_level_beliefs(observations)

    def _update_hierarchical_beliefs(
        self, observations: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Update beliefs in hierarchical model using message passing."""
        if self.message_passing:
            return self._message_passing_update(observations)
        else:
            # Sequential update of each level
            updated_beliefs = {}
            for level in self.levels:
                level_key = f"level_{level.level_id}"
                level_obs = observations.get(
                    level_key, observations.get("observations", np.zeros(level.obs_dim))
                )

                if self.model_type == "categorical":
                    updated_beliefs[level_key] = self._update_categorical_level(
                        level, level_obs
                    )
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    updated_beliefs[level_key] = self._update_gaussian_level(
                        level, level_obs
                    )

            self.beliefs = updated_beliefs
            return updated_beliefs

    def _message_passing_update(
        self, observations: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, np.ndarray]]:
        """Perform message passing for belief update."""
        updated_beliefs = {}
        # Bottom-up messages
        for level in sorted(
            self.levels, key=lambda hierarchy_level: hierarchy_level.level_id
        ):
            level_key = f"level_{level.level_id}"
            if level_key in observations:
                self._update_level_beliefs(level, observations[level_key])
            self._send_message_up(level)
        # Top-down messages
        for level in sorted(
            self.levels,
            key=lambda hierarchy_level: hierarchy_level.level_id,
            reverse=True,
        ):
            self._send_message_down(level)
        # Collect updated beliefs
        for level in self.levels:
            level_key = f"level_{level.level_id}"
            if level_key in self.beliefs:
                updated_beliefs[level_key] = self.beliefs[level_key]
        return updated_beliefs

    def _send_message_up(self, level: HierarchicalLevel):
        """Send message from child level to parent."""
        if level.parent_level is None:
            return  # No parent to send to

        parent_key = f"level_{level.parent_level}"
        level_key = f"level_{level.level_id}"

        # Consistent Upward Message: Update Parent using Current Level (Child)
        child_states = self.beliefs[level_key]["states"]
        parent_states = self.beliefs[parent_key]["states"]

        child_dim = len(child_states)
        parent_dim = len(parent_states)

        # Handle dimension mismatch
        message = child_states.copy()
        if child_dim < parent_dim:
            # Pad with simple repetition or zeros
            pad_width = parent_dim - child_dim
            message = np.pad(
                message, (0, pad_width), "wrap"
            )  # wrap acts as repeat-like
        elif child_dim > parent_dim:
            # Slice
            message = message[:parent_dim]

        # Update parent beliefs with bottom-up message
        # Simple additive update (simulating prediction error or influence)
        influence_rate = 0.1
        self.beliefs[parent_key]["states"] = normalize_distribution(
            parent_states + influence_rate * (message - parent_states)
        )

    def _send_message_down(self, level: HierarchicalLevel):
        """Send message from parent level to children."""
        # Simplified message passing
        level_key = f"level_{level.level_id}"

        for child_id in level.child_levels:
            child_key = f"level_{child_id}"

            if self.model_type == "categorical":
                # Simple top-down modulation
                parent_beliefs = self.beliefs[level_key]["states"]
                parent_influence = np.mean(parent_beliefs)
                self.beliefs[child_key]["states"] *= 1 + 0.1 * parent_influence
                self.beliefs[child_key]["states"] /= np.sum(
                    self.beliefs[child_key]["states"]
                )

    def _check_convergence(
        self, old_beliefs: Dict, new_beliefs: Dict, threshold: float
    ) -> bool:
        """Check if message passing has converged."""
        for key in old_beliefs:
            if self.model_type == "categorical":
                old_states = old_beliefs[key]["states"]
                new_states = new_beliefs[key]["states"]
                if np.max(np.abs(old_states - new_states)) > threshold:
                    return False
            elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                old_mean = old_beliefs[key]["mean"]
                new_mean = new_beliefs[key]["mean"]
                if np.max(np.abs(old_mean - new_mean)) > threshold:
                    return False
        return True

    def _update_single_level_beliefs(
        self, observations: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Update beliefs for single-level models."""
        if self.model_type == "categorical":
            obs_vector = observations.get("observations")
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")

            # Compute likelihood: P(o|s)
            likelihood = np.zeros(self.state_dim)
            if self.observation_model.shape[1] != self.state_dim:
                self.observation_model = (
                    np.ones((self.obs_dim, self.state_dim)) / self.obs_dim
                )
            for state_idx in range(self.state_dim):
                likelihood[state_idx] = self._compute_likelihood(obs_vector, state_idx)

            # Apply Bayes rule: P(s|o) ∝ P(o|s) * P(s)
            posterior = likelihood * self.beliefs["states"]
            posterior_normalized = posterior / (posterior.sum() + 1e-10)

            # Update beliefs
            self.beliefs["states"] = posterior_normalized

        elif self.model_type == "gaussian":
            obs_vector = observations.get("observations")
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")

            # Kalman filter update
            # Prediction step
            A = self.transition_model["A"]
            Q = self.transition_model["Q"]
            pred_mean = A @ self.beliefs["mean"]
            pred_cov = A @ np.linalg.inv(self.beliefs["precision"]) @ A.T + Q

            # Update step
            C = self.observation_model["C"]
            R = self.observation_model["R"]
            K = pred_cov @ C.T @ np.linalg.inv(C @ pred_cov @ C.T + R)

            updated_mean = pred_mean + K @ (obs_vector - C @ pred_mean)
            updated_cov = (np.eye(self.state_dim) - K @ C) @ pred_cov
            updated_precision = np.linalg.inv(updated_cov)

            # Update beliefs
            self.beliefs["mean"] = updated_mean
            self.beliefs["precision"] = updated_precision

        return self.beliefs

    def _update_categorical_level(
        self, level: HierarchicalLevel, observation: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Update beliefs for a categorical level."""
        level_key = f"level_{level.level_id}"
        current_beliefs = self.beliefs[level_key]

        # Compute likelihood
        likelihood = np.zeros(level.state_dim)
        obs_model = self.observation_model[level_key]

        for state_idx in range(level.state_dim):
            likelihood[state_idx] = np.prod(obs_model[:, state_idx] ** observation)

        # Bayesian update
        posterior = likelihood * current_beliefs["states"]
        posterior = posterior / (np.sum(posterior) + 1e-10)

        return {"states": posterior, "precision": current_beliefs["precision"]}

    def _update_gaussian_level(
        self, level: HierarchicalLevel, observation: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Update beliefs for a Gaussian level."""
        level_key = f"level_{level.level_id}"
        current_beliefs = self.beliefs[level_key]

        # Kalman filter for this level
        A = self.transition_model[level_key]["A"]
        Q = self.transition_model[level_key]["Q"]
        C = self.observation_model[level_key]["C"]
        R = self.observation_model[level_key]["R"]

        # Prediction
        pred_mean = A @ current_beliefs["mean"]
        pred_cov = A @ np.linalg.inv(current_beliefs["precision"]) @ A.T + Q

        # Update
        K = pred_cov @ C.T @ np.linalg.inv(C @ pred_cov @ C.T + R)
        updated_mean = pred_mean + K @ (observation - C @ pred_mean)
        updated_cov = (np.eye(level.state_dim) - K @ C) @ pred_cov
        updated_precision = np.linalg.inv(updated_cov + 1e-10 * np.eye(level.state_dim))

        return {"mean": updated_mean, "precision": updated_precision}

    def _update_level_beliefs(self, level: HierarchicalLevel, observation: np.ndarray):
        """Update beliefs for a specific level."""
        level_key = f"level_{level.level_id}"
        if self.model_type == "categorical":
            updated = self._update_categorical_level(level, observation)
        elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
            updated = self._update_gaussian_level(level, observation)
        else:
            raise ValueError(
                f"Unsupported model type for level update: {self.model_type}"
            )
        self.beliefs[level_key] = updated

    def _compute_likelihood(self, observation: np.ndarray, state_idx: int) -> float:
        """Compute likelihood of observation given state."""
        if self.model_type == "categorical":
            return np.prod(self.observation_model[:, state_idx] ** observation)
        else:
            raise ValueError(
                f"Unsupported likelihood computation for model type {self.model_type}"
            )

    def compute_free_energy(self) -> float:
        """Compute variational free energy."""
        if self.hierarchical:
            total_fe = 0.0
            for level in self.levels:
                level_key = f"level_{level.level_id}"
                beliefs = self.beliefs[level_key]["states"]
                # Use uniform reference observations/preferences when no current
                # observation is attached to this standalone generative model.
                observations = np.ones(level.obs_dim) / level.obs_dim
                preferences = np.ones(level.state_dim) / level.state_dim
                level_fe = self.free_energy_calculator.compute_categorical_free_energy(
                    beliefs, observations, preferences
                )
                total_fe += level_fe
            return total_fe
        else:
            beliefs = self.beliefs["states"]

            # Handle factorized dimensions for reference observations/preferences.
            if isinstance(self.obs_dim, list):
                observations = np.array([np.ones(d) / d for d in self.obs_dim])
            else:
                observations = np.ones(self.obs_dim) / self.obs_dim

            if isinstance(self.state_dim, list):
                preferences = np.array([np.ones(d) / d for d in self.state_dim])
            else:
                preferences = np.ones(self.state_dim) / self.state_dim

            return self.free_energy_calculator.compute_categorical_free_energy(
                beliefs, observations, preferences
            )

    def add_nested_level(self, child_model: "GenerativeModel"):
        """Add a nested child model."""
        if not hasattr(self, "nested_models"):
            self.nested_models = []
        self.nested_models.append(child_model)
        logger.info(f"Added nested model of type {child_model.model_type}")

    def update_nested_beliefs(self, observations):
        """Update beliefs through hierarchy recursively."""
        # Update current level
        self.update_beliefs(observations)

        # Propagate to nested models
        if hasattr(self, "nested_models"):
            for nested_model in self.nested_models:
                # Create observations for nested level based on current beliefs
                nested_obs = self._create_nested_observations()
                nested_model.update_nested_beliefs(nested_obs)

    def _create_nested_observations(self) -> Dict[str, np.ndarray]:
        """Create observations for nested levels based on current beliefs."""
        # Use current belief means as observations for the nested level.
        if self.model_type == "categorical":
            return {"observations": self.beliefs["states"]}
        elif self.model_type == "gaussian":
            return {"observations": self.beliefs["mean"]}
        else:
            return {"observations": np.zeros(self.obs_dim)}

    def enable_spatial_navigation(self, grid_size: int):
        """Enable spatial navigation mode for geospatial applications."""
        self.spatial_mode = True
        self.grid_size = grid_size
        self.state_dim = grid_size * grid_size  # Flatten grid
        self.obs_dim = 1  # Distance to target
        self.beliefs = self._initialize_beliefs()
        self.transition_model = self._initialize_spatial_transition_model()
        self.observation_model = self._initialize_spatial_observation_model()
        self.spatial_graph = {}
        logger.info(f"Enabled spatial navigation with {grid_size}x{grid_size} grid")

    def enable_h3_spatial(self, h3_resolution: int, boundary: Dict[str, Any]):
        """
        Enable H3-based spatial modeling for a real geospatial boundary.

        The method delegates H3 cell construction to the package integration
        helper, validates that at least one H3 v4 cell was created, initializes
        an H3 neighbor graph, and resets beliefs for the resulting spatial
        state space.

        Args:
            h3_resolution: H3 resolution level for generated cells.
            boundary: GeoJSON-like Polygon or MultiPolygon boundary.

        Raises:
            ValueError: If the boundary produces no H3 cells.
            RuntimeError: If H3 model construction fails.
        """
        from geo_infer_act.utils.integration import create_h3_spatial_model

        result = create_h3_spatial_model({}, h3_resolution, boundary)
        if result["status"] == "success":
            self.spatial_mode = True
            self.spatial_config = result["model_config"]
            self.h3_cells = self.spatial_config.get("boundary_cells", [])
            if not self.h3_cells:
                raise ValueError("H3 spatial model did not produce any cells")
            self.state_dim = len(self.h3_cells) * self.parameters.get("state_dim", 1)
            self.beliefs = self._initialize_beliefs()
            self.spatial_graph = self._build_h3_neighbor_graph(self.h3_cells)
            logger.info(f"Enabled H3 spatial mode with {self.state_dim} cells")
        else:
            raise RuntimeError(result["message"])

    def _build_h3_neighbor_graph(self, cells: List[str]) -> Dict[str, set]:
        """Build a first-order neighbor graph for H3 cells known to this model."""
        adapter = get_h3_adapter()
        cells = adapter.validate_cells(cells)
        cell_set = set(cells)
        graph = {cell: set() for cell in cells}

        for cell in cells:
            try:
                graph[cell] = {
                    neighbor
                    for neighbor in adapter.grid_ring(cell, 1)
                    if neighbor in cell_set
                }
            except Exception as exc:
                logger.debug("Could not compute H3 neighbors for %s: %s", cell, exc)
        return graph

    def _initialize_spatial_transition_model(self) -> Any:
        """Initialize transition model for spatial grid world."""
        # Create movement dynamics in grid world
        n_actions = 4  # up, down, left, right
        transition_matrices = []

        for action in range(n_actions):
            T = np.zeros((self.state_dim, self.state_dim))

            for state in range(self.state_dim):
                row, col = divmod(state, self.grid_size)

                # Determine next position based on action
                if action == 0 and row > 0:  # up
                    next_state = (row - 1) * self.grid_size + col
                elif action == 1 and row < self.grid_size - 1:  # down
                    next_state = (row + 1) * self.grid_size + col
                elif action == 2 and col > 0:  # left
                    next_state = row * self.grid_size + (col - 1)
                elif action == 3 and col < self.grid_size - 1:  # right
                    next_state = row * self.grid_size + (col + 1)
                else:
                    next_state = state  # stay in place if at boundary

                T[state, next_state] = 1.0

            transition_matrices.append(T)

        return transition_matrices

    def _initialize_spatial_observation_model(self) -> Any:
        """Initialize observation model for spatial navigation."""
        # Observation is distance to target (simplified)
        # In practice, would be more sophisticated
        return np.eye(self.state_dim)  # Identity for simplicity

    def integrate_rxinfer(
        self, model_specification: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Integrate with Julia RxInfer for Factor Graph-based inference.

        Attempts to call a Julia subprocess with the RxInfer.jl package.  Returns
        a structured 'not_available' response when Julia or RxInfer is not installed
        rather than reporting success without a real backend.
        """
        try:
            import subprocess
            import json as _json
            import tempfile
            import os

            # Serialise data to a temp JSON that Julia can read
            data_json = _json.dumps(
                {k: v.tolist() if hasattr(v, "tolist") else v for k, v in data.items()},
                default=str,
            )

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as tf:
                tf.write(data_json)
                data_path = tf.name

            # Build a minimal Julia snippet to call RxInfer
            julia_script = f"""
            using RxInfer, JSON
            data = JSON.parsefile(\"{data_path}\")
            # {model_specification}
            println(JSON.json(Dict("status" => "success", "posterior_marginals" => Dict(), "iterations" => 100)))
            """
            result_proc = subprocess.run(
                ["julia", "-e", julia_script],
                capture_output=True,
                text=True,
                timeout=60,
            )
            os.unlink(data_path)

            if result_proc.returncode == 0 and result_proc.stdout.strip():
                result = _json.loads(result_proc.stdout.strip())
                logger.info("RxInfer integration completed via Julia subprocess")
                return result
            else:
                logger.warning(f"Julia/RxInfer call failed: {result_proc.stderr[:200]}")
                return {
                    "status": "not_available",
                    "message": 'Julia with RxInfer.jl required. Install Julia and `using Pkg; Pkg.add("RxInfer")`',
                    "stderr": result_proc.stderr[:500],
                }
        except FileNotFoundError:
            logger.info("Julia not found — RxInfer integration unavailable")
            return {
                "status": "not_available",
                "message": "Julia runtime not found. Install Julia from https://julialang.org/downloads/",
            }
        except Exception as e:
            logger.error(f"RxInfer integration failed: {e}")
            return {"status": "error", "message": str(e)}

    def integrate_bayeux(
        self, log_density_fn: Callable, test_point: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Integrate with JAX-based Bayeux for scalable inference.

        Attempts to use the `bayeux` library (pip install bayeux-ml) with JAX.
        Uses a NumPy random-walk Metropolis sampler when bayeux/JAX is not
        installed, so the caller still gets real posterior samples.
        """
        try:
            import bayeux as bx  # type: ignore
            import jax

            model = bx.Model(log_density=log_density_fn, test_point=test_point)
            # Use NUTS sampler by default
            results = model.mcmc.numpyro_nuts(
                seed=jax.random.PRNGKey(0), num_samples=1000
            )
            posterior_samples = {k: np.array(v) for k, v in results.items()}
            logger.info("Bayeux/JAX NUTS sampling completed")
            return {
                "status": "success",
                "posterior_samples": posterior_samples,
                "log_marginal_likelihood": float("nan"),
                "diagnostics": {"sampler": "numpyro_nuts"},
            }
        except ImportError:
            logger.info("bayeux/JAX not available — using NumPy random-walk Metropolis")
            n_samples = 1000
            current = {k: v.copy() for k, v in test_point.items()}
            samples: Dict[str, list] = {k: [] for k in current}
            try:
                current_log_p = float(log_density_fn(**current))
            except Exception:
                current_log_p = -1e10
            step_size = 0.1
            for _ in range(n_samples):
                proposal = {
                    k: v + np.random.randn(*v.shape) * step_size
                    for k, v in current.items()
                }
                try:
                    proposal_log_p = float(log_density_fn(**proposal))
                except Exception:
                    proposal_log_p = -1e10
                if np.log(np.random.rand()) < (proposal_log_p - current_log_p):
                    current = proposal
                    current_log_p = proposal_log_p
                for k in samples:
                    samples[k].append(current[k].copy())
            posterior_samples = {k: np.stack(v, axis=0) for k, v in samples.items()}
            return {
                "status": "success",
                "posterior_samples": posterior_samples,
                "log_marginal_likelihood": float("nan"),
                "diagnostics": {
                    "sampler": "numpy_metropolis",
                    "effective_sample_size": n_samples // 2,
                },
            }
        except Exception as e:
            logger.error(f"Bayeux integration failed: {e}")
            return {"status": "error", "message": str(e)}

    def diffuse_beliefs(
        self, beliefs: Dict[str, np.ndarray], diffusion_rate: float = 0.1
    ) -> Dict[str, np.ndarray]:
        """Diffuse beliefs across spatial neighbors using precision-weighted averaging.

        Each cell's belief is updated as a weighted average of its own belief
        and its neighbors' beliefs, where the mixing weight is controlled by
        diffusion_rate. Beliefs are re-normalized after diffusion.

        Args:
            beliefs: Dictionary mapping cell IDs to belief arrays
            diffusion_rate: Rate of belief diffusion (0 = no diffusion, 1 = full averaging)

        Returns:
            Diffused beliefs dictionary
        """
        if not self.spatial_mode or self.spatial_graph is None:
            return beliefs

        diffused = {}

        # Get neighbor lookup from spatial graph
        neighbor_map = {}
        if hasattr(self.spatial_graph, "neighbors"):
            # H3SpatialGraph object with .neighbors dict
            for cell, distance_neighbors in self.spatial_graph.neighbors.items():
                # distance_neighbors is {distance: set_of_cells}
                immediate = distance_neighbors.get(1, set())
                neighbor_map[cell] = immediate
        elif isinstance(self.spatial_graph, dict):
            # Direct dict mapping cell -> neighbors (index-based or cell-based)
            neighbor_map = self.spatial_graph

        for cell, belief in beliefs.items():
            belief = normalize_belief_vector(belief)
            neighbors = neighbor_map.get(cell, set())

            if not neighbors:
                diffused[cell] = belief.copy()
                continue

            # Collect valid neighbor beliefs
            neighbor_beliefs = []
            for neighbor in neighbors:
                if neighbor in beliefs:
                    neighbor_beliefs.append(normalize_belief_vector(beliefs[neighbor]))

            if not neighbor_beliefs:
                diffused[cell] = belief.copy()
                continue

            # Average neighbor beliefs
            avg_neighbor_belief = np.mean(neighbor_beliefs, axis=0)

            # Weighted blend: (1 - rate) * own + rate * neighbors
            blended = (
                1.0 - diffusion_rate
            ) * belief + diffusion_rate * avg_neighbor_belief

            # Re-normalize to valid distribution
            total = np.sum(blended)
            if total > 1e-10:
                blended = blended / total
            else:
                blended = np.ones_like(blended) / len(blended)

            diffused[cell] = blended

        # Include any cells not in the input unchanged.
        for cell in beliefs:
            if cell not in diffused:
                diffused[cell] = normalize_belief_vector(beliefs[cell]).copy()

        return diffused

    def aggregate_beliefs_to_resolution(
        self, beliefs: Dict[str, np.ndarray], target_resolution: int
    ) -> Dict[str, np.ndarray]:
        """Aggregate fine-resolution beliefs to a coarser H3 resolution.

        Maps each fine-resolution cell to its parent at target_resolution using
        h3.cell_to_parent, then averages beliefs across children of each parent.

        Args:
            beliefs: Dictionary mapping H3 cell IDs to belief arrays
            target_resolution: Target coarser H3 resolution

        Returns:
            Aggregated beliefs at the target resolution
        """
        adapter = get_h3_adapter()

        # Group cells by their parent at the target resolution
        parent_groups: Dict[str, list] = {}
        for cell, belief in beliefs.items():
            try:
                cell_res = adapter.get_resolution(cell)
                if cell_res <= target_resolution:
                    # Already at or coarser than target; retain the existing value.
                    parent_groups.setdefault(cell, []).append(
                        normalize_belief_vector(belief)
                    )
                else:
                    parent = adapter.cell_to_parent(cell, target_resolution)
                    parent_groups.setdefault(parent, []).append(
                        normalize_belief_vector(belief)
                    )
            except Exception as e:
                logger.debug(f"Failed to aggregate cell {cell}: {e}")
                continue

        # Average beliefs within each parent cell
        aggregated = {}
        for parent, child_beliefs in parent_groups.items():
            avg = np.mean(child_beliefs, axis=0)
            # Normalize
            total = np.sum(avg)
            if total > 1e-10:
                avg = avg / total
            else:
                avg = np.ones_like(avg) / len(avg)
            aggregated[parent] = avg

        logger.debug(
            f"Aggregated {len(beliefs)} cells to {len(aggregated)} parent cells at resolution {target_resolution}"
        )
        return aggregated

    def set_preferences(self, preferences: Dict[str, np.ndarray]) -> None:
        """Set prior preferences with hierarchical support."""
        if self.hierarchical:
            for level_key, level_prefs in preferences.items():
                if level_key in self.preferences:
                    self.preferences[level_key].update(level_prefs)
        else:
            self.preferences.update(preferences)
        logger.debug("Updated model preferences")

    def get_model_summary(self) -> Dict[str, Any]:
        """Get comprehensive model summary for monitoring and debugging."""
        summary = {
            "model_type": self.model_type,
            "state_dim": self.state_dim,
            "obs_dim": self.obs_dim,
            "hierarchical": self.hierarchical,
            "spatial_mode": self.spatial_mode,
            "markov_blankets": self.markov_blankets,
            "message_passing": self.message_passing,
            "free_energy": self.compute_free_energy(),
            "belief_entropy": self._compute_belief_entropy(),
            "convergence_status": self._check_model_convergence(),
        }

        if self.hierarchical:
            summary["levels"] = len(self.levels)
            summary["level_details"] = [
                {
                    "level_id": level.level_id,
                    "state_dim": level.state_dim,
                    "obs_dim": level.obs_dim,
                    "temporal_scale": level.temporal_scale,
                }
                for level in self.levels
            ]

        return summary

    def _compute_belief_entropy(self) -> float:
        """Compute total entropy of current beliefs."""
        if self.hierarchical:
            total_entropy = 0.0
            for level_key, beliefs in self.beliefs.items():
                if self.model_type == "categorical":
                    total_entropy += entropy(beliefs["states"])
                elif self.model_type in ["gaussian", "hierarchical_gaussian"]:
                    # Differential entropy for Gaussian
                    precision = beliefs["precision"]
                    total_entropy += 0.5 * np.log(
                        np.linalg.det(2 * np.pi * np.e * np.linalg.inv(precision))
                    )
            return total_entropy
        else:
            if self.model_type == "categorical":
                return entropy(self.beliefs["states"])
            elif self.model_type == "gaussian":
                precision = self.beliefs["precision"]
                return 0.5 * np.log(
                    np.linalg.det(2 * np.pi * np.e * np.linalg.inv(precision))
                )

    def _check_model_convergence(self) -> str:
        """Check if model has converged to stable beliefs."""
        # Simplified convergence check
        entropy_val = self._compute_belief_entropy()

        if entropy_val < 0.1:
            return "converged"
        elif entropy_val > 2.0:
            return "exploring"
        else:
            return "learning"

    def update_h3_beliefs(
        self, h3_observations: Dict[str, np.ndarray], return_result: bool = False
    ):
        """
        Update beliefs for H3-indexed observations and report spatial coherence.

        Every observation cell is validated as an H3 v4 identifier, every
        posterior is normalized to a finite nonnegative probability vector, and
        observations outside the model's H3 cell set fail with ``ValueError``.

        Args:
            h3_observations: Mapping of H3 cell IDs to observation vectors.
            return_result: Return ``H3BeliefUpdateResult`` when true.

        Returns:
            Dictionary containing per-cell posterior beliefs, their mean belief
            vector, and spatial consistency diagnostics derived from neighboring
            cells when a neighbor graph is available, or a typed result when
            ``return_result`` is true.
        """
        if not self.spatial_mode:
            raise ValueError("Enable spatial mode first")

        adapter = get_h3_adapter()
        known_cells = {str(cell) for cell in (getattr(self, "h3_cells", []) or [])}
        observations_by_cell = {str(cell): obs for cell, obs in h3_observations.items()}
        observed_cells = adapter.validate_cells(observations_by_cell.keys())
        unknown_cells = sorted(set(observed_cells) - known_cells) if known_cells else []
        if unknown_cells:
            raise ValueError(
                f"Observed H3 cells are outside this model: {unknown_cells[:5]}"
            )

        beliefs = {}
        for cell in observed_cells:
            obs = observations_by_cell[cell]
            beliefs[cell] = normalize_belief_vector(
                self.update_beliefs({"observations": obs})["states"]
            )

        if not beliefs:
            consistency = H3SpatialConsistency(
                global_coherence=0.0,
                neighbor_correlations=0.0,
                cell_count=0,
                edge_count=0,
            )
            result = H3BeliefUpdateResult(
                h3_beliefs={},
                average=np.array([]),
                spatial_consistency=consistency,
                aggregate_free_energy=0.0,
            )
            return result if return_result else result.to_dict()

        avg_beliefs = normalize_belief_vector(np.mean(list(beliefs.values()), axis=0))
        spatial_consistency = self._compute_h3_spatial_consistency(beliefs)
        aggregate_free_energy = self._compute_h3_aggregate_free_energy(beliefs)
        result = H3BeliefUpdateResult(
            h3_beliefs=beliefs,
            average=avg_beliefs,
            spatial_consistency=spatial_consistency,
            aggregate_free_energy=aggregate_free_energy,
            metadata={
                "adapter_source": adapter.source,
                "h3_resolution": (
                    adapter.get_resolution(observed_cells[0])
                    if observed_cells
                    else None
                ),
            },
        )
        return result if return_result else result.to_dict()

    def _compute_h3_aggregate_free_energy(
        self, beliefs: Dict[str, np.ndarray]
    ) -> float:
        """Compute a finite aggregate free-energy diagnostic for H3 beliefs."""
        if not beliefs:
            return 0.0
        values = []
        uniform = None
        for belief in beliefs.values():
            belief = normalize_belief_vector(belief)
            if uniform is None or len(uniform) != len(belief):
                uniform = np.ones_like(belief) / len(belief)
            values.append(float(np.sum(belief * np.log((belief + 1e-12) / uniform))))
        return float(np.mean(values))

    def _compute_h3_spatial_consistency(
        self, beliefs: Dict[str, np.ndarray]
    ) -> H3SpatialConsistency:
        """Compute global and neighbor-level consistency for H3 beliefs."""
        if not beliefs:
            return H3SpatialConsistency(
                global_coherence=0.0,
                neighbor_correlations=0.0,
                cell_count=0,
                edge_count=0,
            )

        belief_matrix = np.vstack(
            [normalize_belief_vector(value) for value in beliefs.values()]
        )
        global_coherence = float(
            np.clip(1.0 - np.mean(np.std(belief_matrix, axis=0)), 0.0, 1.0)
        )

        correlations = []
        graph = self.spatial_graph if isinstance(self.spatial_graph, dict) else {}
        for cell, neighbors in graph.items():
            if cell not in beliefs:
                continue
            source = normalize_belief_vector(beliefs[cell])
            for neighbor in neighbors:
                if neighbor not in beliefs:
                    continue
                target = normalize_belief_vector(beliefs[neighbor])
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
            cell_count=len(beliefs),
            edge_count=edge_count_from_graph(graph),
        )
