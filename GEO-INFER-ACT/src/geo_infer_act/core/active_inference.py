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
        self.preferences = self.parameters.pop('preferences', None)
        
        # Initialize core components
        self.generative_model = None
        self.free_energy_calculator = FreeEnergyCalculator()
        self.policy_selector = PolicySelector()
        self.belief_updater = BayesianBeliefUpdate()

        # Analyzer Integration
        self.output_dir = kwargs.get('output_dir', None)
        self.analyzer = None
        if self.output_dir:
             self.analyzer = ActiveInferenceAnalyzer(self.output_dir)
             logger.info(f"Active Inference Analyzer enabled. Logging to {self.output_dir}")
        
        # State variables
        self.current_beliefs = None
        self.current_observations = None
        self.current_actions = None
        self.history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized ActiveInferenceModel with type: {model_type}")
    
    def set_generative_model(self, model: GenerativeModel):
        """Set the generative model for this active inference agent."""
        self.generative_model = model
        if getattr(model, 'model_type', None) and model.model_type != self.model_type:
            logger.info("Aligning active inference model type with generative model: %s", model.model_type)
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
        
        # Try pymdp control if available
        try:
            from pymdp.control import construct_policies, sample_action
            from pymdp.maths import spm_log_single
            
            # Check if we have necessary matrices
            A = getattr(self.generative_model, 'observation_model', None)
            B = getattr(self.generative_model, 'transition_model', None)
            C = getattr(self.generative_model, 'preferences', None)
            
            if A is not None and B is not None and C is not None:
                # Prepare qs (beliefs)
                qs = self.current_beliefs.get('states') if isinstance(self.current_beliefs, dict) else self.current_beliefs
                # Ensure qs is list of arrays (factors)
                if isinstance(qs, np.ndarray) and qs.dtype != object:
                    qs = [qs] 
                elif isinstance(qs, list) and len(qs) > 0 and not isinstance(qs[0], np.ndarray):
                     # If generic list, convert elements
                     qs = [np.array(q) for q in qs]

                # Get dimensions
                num_controls = getattr(self.generative_model, 'num_controls', None)
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
                    q_pi, _ = update_posterior_policies(qs, A, B, C, policies, use_utility=True) 
                    # Note: update_posterior_policies might re-calc G internaly? 
                    # If G is available, some versions allow passing it.
                    # But simpler:
                    q_pi = softmax(-G)
                    
                    # Sample action
                    action = sample_action(q_pi, policies, num_controls, sampling_mode='marginal')
                    
                    self.current_actions = action
                    return action
                except ImportError:
                     # Fallback to simple G calc if specific functions missing
                     logger.debug("pymdp control functions not available, using fallback")
        except (ImportError, Exception) as exc:
            logger.debug("pymdp not available or failed: %s", exc)

        # Standard / Fallback Implementation
        
        # Generate default actions if none provided
        if available_actions is None:
            available_actions = list(range(getattr(self.generative_model, 'num_controls', [3])[0]))
        
        selected_action: Any = None
        belief_vector = self._extract_belief_vector(self.current_beliefs)

        if belief_vector is not None:
            policy_candidates = [
                {'action': action, 'exploration_bonus': self.parameters.get('exploration_bonus', 0.1)}
                for action in available_actions
            ]
            try:
                policy_info = self.policy_selector.select_policy(
                    belief_vector,
                    policy_candidates,
                    self._get_preferences_vector()
                )
                policy = policy_info.get('policy', policy_info)
                selected_action = policy.get('action', policy)
            except Exception as exc:  # pragma: no cover - defensive path
                logger.debug("Falling back to heuristic action selection: %s", exc)

        if selected_action is None:
            fallback_beliefs = belief_vector if belief_vector is not None else np.ones(len(available_actions)) / len(available_actions)
            selected_action = self.policy_selector.select_action(
                fallback_beliefs,
                available_actions,
                self.generative_model
            )
        
        self.current_actions = selected_action
        return selected_action

    def update_observations(self, observations: Dict[str, Any]) -> None:
        """Update observations for the active inference model."""
        self.current_observations = observations

    def update_preferences(self, preferences: Dict[str, float]) -> None:
        """Update preferences for the active inference model."""
        self.preferences = preferences

    def update_with_outcome(self, decision: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """
        Update model based on decision outcome for learning.

        Stores the decision-outcome pair in history and updates beliefs
        if outcome contains observation data, implementing the
        perception-action loop closure in Active Inference.

        Args:
            decision: The decision/action taken
            outcome: The observed outcome
        """
        self.history.append({
            'decision': decision,
            'outcome': outcome,
            'beliefs_at_decision': self._clone_beliefs(self.current_beliefs)
        })
        if 'observation' in outcome:
            obs = np.asarray(outcome['observation'], dtype=float).reshape(-1)
            self.perceive(obs)

    def generate_policies(self, available_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate policy options from available actions."""
        return available_actions

    def select_policy(self, policies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select optimal policy from candidates."""
        if not policies:
            return {}
        return policies[0]  # Simplified selection

    def compute_expected_free_energy(self, policy: Dict[str, Any]) -> float:
        """Compute expected free energy for a policy."""
        return 0.5  # Simplified calculation

    def step(self, observation: np.ndarray, available_actions: Optional[List[Any]] = None) -> Tuple[np.ndarray, Any]:
        """
        Perform one complete active inference step.
        
        Args:
            observation: Current observation
            available_actions: Available actions
            
        Returns:
            Tuple of (updated_beliefs, selected_action)
        """
        observation_array = np.asarray(observation, dtype=float).reshape(-1)

        # Perception: update beliefs
        beliefs = self.perceive(observation_array)
        
        # Action: select policy
        action = self.act(available_actions)
        
        # Store step in history
        step_data = {
            'observation': observation_array.copy(),
            'beliefs': self._clone_beliefs(beliefs),
            'action': action,
            'free_energy': self.compute_free_energy() if beliefs is not None else np.inf
        }
        self.history.append(step_data)
        
        # Comprehensive Logging via Analyzer
        if self.analyzer:
             # Gather deep diagnostics
             policies = {}
             # Try to extract policy probabilities if available (set during act())
             # Note: current_actions logic in act() doesn't strictly save the distribution 'q_pi',
             # so we might need to enhance act() to save it or re-calculate/infer it here.
             # For now, we save what we have.
             
             metrics = {
                 'model_type': self.model_type,
                 'free_energy': step_data['free_energy']
             }
             
             # If using pymdp, we might have access to G or q_pi if we stored them.
             # Ideally act() should store 'latest_policy_probs' or similar.
             
             self.analyzer.record_step(
                 beliefs=step_data['beliefs'],
                 observations=step_data['observation'],
                 actions=action,
                 policies=policies, # Placeholder until act() stores deeper data
                 free_energy=step_data['free_energy'],
                 metrics=metrics
             )
        
        return beliefs, action
    
    def compute_free_energy(self) -> float:
        """Compute current variational free energy."""
        
        # Delegate to GenerativeModel if it supports free energy computation (handles hierarchical etc.)
        if self.generative_model is not None and hasattr(self.generative_model, 'compute_free_energy'):
            return self.generative_model.compute_free_energy()
            
        if self.current_beliefs is None:
            return np.inf

        if self.model_type == 'categorical':
            belief_vector = self._extract_belief_vector(self.current_beliefs)
            if belief_vector is None:
                return np.inf
            observation_vector = self._get_observation_vector(len(belief_vector))
            preferences = self._get_preferences_vector(len(belief_vector))
            return self.free_energy_calculator.compute_categorical_free_energy(
                belief_vector,
                observation_vector,
                preferences
            )

        if self.model_type == 'gaussian':
            gaussian_beliefs = self._ensure_gaussian_beliefs(self.current_beliefs)
            if gaussian_beliefs is None or self.current_observations is None:
                return np.inf
            gaussian_preferences = self._get_gaussian_preferences()
            return self.free_energy_calculator.compute_gaussian_free_energy(
                gaussian_beliefs['mean'],
                gaussian_beliefs['precision'],
                self.current_observations,
                gaussian_preferences.get('mean'),
                gaussian_preferences.get('precision')
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
        self.history = []
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete history of interactions."""
        return [copy.deepcopy(entry) for entry in self.history]
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current model state."""
        return {
            'beliefs': self._clone_beliefs(self.current_beliefs),
            'observations': self.current_observations.copy() if isinstance(self.current_observations, np.ndarray) else self.current_observations,
            'actions': self.current_actions,
            'free_energy': self.compute_free_energy(),
            'model_type': self.model_type
        } 

    def apply_to_h3(self, h3_obs: Dict[str, np.ndarray]):
        if self.generative_model is None:
            raise ValueError('Set generative model first')
        return self.generative_model.update_h3_beliefs(h3_obs) 

    def infer_over_h3_grid(self, h3_grid: Dict[str, Any]):
        results = {}
        original_beliefs = self._clone_beliefs(self.current_beliefs)
        original_observations = self.current_observations.copy() if isinstance(self.current_observations, np.ndarray) else self.current_observations
        original_actions = self.current_actions
        history_len = len(self.history)

        try:
            for cell, obs in h3_grid.items():
                beliefs, action = self.step(obs)
                results[cell] = {
                    'beliefs': self._clone_beliefs(beliefs),
                    'action': action,
                    'free_energy': self.compute_free_energy(),
                    'precision': self.current_beliefs.get('precision', 1.0) if isinstance(self.current_beliefs, dict) else 1.0
                }
        finally:
            self.current_beliefs = original_beliefs
            self.current_observations = original_observations
            self.current_actions = original_actions
            if len(self.history) > history_len:
                self.history = self.history[:history_len]

        return results

    def set_preferences(self, preferences: Union[np.ndarray, Dict[str, Any]]):
        """Override prior preferences used during inference."""
        self.preferences = preferences

    def _extract_model_beliefs(self, model: GenerativeModel):
        beliefs = getattr(model, 'beliefs', None)
        if beliefs is None:
            s_dim = getattr(model, 'state_dim', None)
            if s_dim is None:
                s_dim = getattr(model, 'num_states', 0)
                
            if self.model_type == 'categorical' and (isinstance(s_dim, int) and s_dim > 0 or isinstance(s_dim, list) and len(s_dim) > 0):
                if isinstance(s_dim, list):
                    return {'states': [normalize_distribution(np.ones(d)) for d in s_dim]}
                return {'states': normalize_distribution(np.ones(s_dim))}
            if self.model_type == 'gaussian' and (isinstance(s_dim, int) and s_dim > 0 or isinstance(s_dim, list) and len(s_dim) > 0):
                if isinstance(s_dim, list): s_dim = s_dim[0] # Simplify for gaussian
                precision = np.eye(s_dim) * getattr(model, 'prior_precision', 1.0)
                return {'mean': np.zeros(s_dim), 'precision': precision}
            return None

        if isinstance(beliefs, dict):
            if self.model_type == 'categorical':
                if 'states' in beliefs:
                    # Return list/array structure as is, just wrapped in dict if not already
                    return {'states': beliefs['states']}
                for value in beliefs.values():
                    if isinstance(value, dict) and 'states' in value:
                        return {'states': value['states']}
            if self.model_type == 'gaussian' and 'mean' in beliefs and 'precision' in beliefs:
                return {
                    'mean': np.asarray(beliefs['mean'], dtype=float).copy(),
                    'precision': np.asarray(beliefs['precision'], dtype=float).copy()
                }

        if isinstance(beliefs, (np.ndarray, list)):
            return {'states': beliefs}

        return None

    def _extract_model_preferences(self, model: GenerativeModel):
        prefs = getattr(model, 'preferences', None)
        if prefs is None:
            return None
        if isinstance(prefs, dict):
            if self.model_type == 'categorical':
                extracted: Dict[str, Any] = {}
                if 'states' in prefs:
                    extracted['states'] = normalize_distribution(self._safe_flatten(prefs['states']))
                if 'observations' in prefs:
                    extracted['observations'] = normalize_distribution(self._safe_flatten(prefs['observations']))
                return extracted or None
            if self.model_type == 'gaussian':
                result: Dict[str, Any] = {}
                if 'mean' in prefs:
                    result['mean'] = np.asarray(prefs['mean'], dtype=float).copy()
                if 'precision' in prefs:
                    result['precision'] = np.asarray(prefs['precision'], dtype=float).copy()
                return result or None
        if isinstance(prefs, (np.ndarray, list)):
             # Safe flatten handles list or object array
             return normalize_distribution(self._safe_flatten(prefs))
        return None

    def _update_beliefs_with_model(self, observation: np.ndarray):
        if self.generative_model is None:
            raise ValueError("Generative model must be set before perception")

        try:
            if self.model_type == 'categorical':
                updated = self.generative_model.update_beliefs({'observations': observation})
                
                # Check for hierarchical structure
                if isinstance(updated, dict) and any(k.startswith('level_') for k in updated.keys()):
                    return updated
                    
                if isinstance(updated, dict) and 'states' in updated:
                    # Return consistent dict structure
                    vec = normalize_distribution(self._safe_flatten(updated['states']))
                    return {'states': vec}
                if isinstance(updated, np.ndarray):
                    vec = normalize_distribution(updated.astype(float))
                    return {'states': vec}
            elif self.model_type == 'gaussian':
                updated = self.generative_model.update_beliefs({'observations': observation})
                if isinstance(updated, dict) and 'mean' in updated and 'precision' in updated:
                    return {
                        'mean': np.asarray(updated['mean'], dtype=float).copy(),
                        'precision': np.asarray(updated['precision'], dtype=float).copy()
                    }
        except Exception as exc:  # pragma: no cover - defensive path
            logger.debug("Falling back to local belief update: %s", exc)

        return self._update_beliefs_direct(observation)

    def _update_beliefs_direct(self, observation: np.ndarray):
        if self.current_beliefs is None:
            self.current_beliefs = self._extract_model_beliefs(self.generative_model)

        # PYMDP Integration Check
        if self.model_type == 'categorical':
            A = getattr(self.generative_model, 'observation_model', None)
            
            # Safely get prior
            if isinstance(self.current_beliefs, dict):
                prior = self.current_beliefs.get('states')
            else:
                prior = self.current_beliefs # Assume it's the states array/list
                
            # Check if using pymdp style (A is object array or list of arrays)
            if (isinstance(A, np.ndarray) and A.dtype == object) or isinstance(A, list):
                try:
                    from pymdp.inference import update_posterior_states
                    # Convert observation to int/list of ints if needed
                    # Observation comes in as float array usually in this codebase
                    # But proper pymdp expects integers for categorical observations
                    obs_indices = [int(o) for o in observation] if isinstance(observation, (list, np.ndarray)) else [int(observation)]
                    
                    # Update beliefs using pymdp
                    qs = update_posterior_states(A, obs_indices, prior_beliefs=prior)
                    
                    # Update internal state clearly
                    self.current_beliefs = {'states': qs}
                    return {'states': qs}
                except (ImportError, Exception) as e:
                     logger.debug(f"Pymdp update failed: {e}")

            # Fallback to existing manual update for simple arrays
            prior_vec = self._extract_belief_vector(self.current_beliefs) # Will extract from dict or array
            if isinstance(A, np.ndarray) and A.dtype != object:
                if prior_vec is None: return None
                if A.shape[1] != len(prior_vec):
                    obs_dim = A.shape[0]
                    # Creating a dummy A if dimensions mismatch is dangerous but preserving existing logic fallback
                    self.generative_model.observation_model = np.ones((obs_dim, len(prior_vec))) / max(obs_dim, 1)
                updated_beliefs = self.belief_updater.update_categorical(
                    prior_vec,
                    observation,
                    self.generative_model.observation_model
                )
                self.current_beliefs = {'states': updated_beliefs}
                return self.current_beliefs

        if self.model_type == 'gaussian':
            gaussian_beliefs = self._ensure_gaussian_beliefs(self.current_beliefs)
            if gaussian_beliefs is None or not isinstance(self.generative_model.observation_model, dict):
                return self.current_beliefs
            observation_model = self.generative_model.observation_model
            return self.belief_updater.update_gaussian(
                gaussian_beliefs['mean'],
                gaussian_beliefs['precision'],
                observation,
                observation_model.get('C', np.eye(len(gaussian_beliefs['mean']))),
                np.linalg.inv(observation_model.get('R', np.eye(len(observation))))
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
                logger.debug("Dict flattening failed, falling through to list/array handler")
                
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
                    logger.debug("Object array element conversion failed, treating as flat float array")
            return np.asarray(data, dtype=float).reshape(-1)
            
        return np.array([float(data)])

    def _extract_belief_vector(self, beliefs: Any) -> Optional[np.ndarray]:
        if beliefs is None:
            return None
        if isinstance(beliefs, dict) and 'states' in beliefs:
            return normalize_distribution(self._safe_flatten(beliefs['states']))
        return normalize_distribution(self._safe_flatten(beliefs))

    def _ensure_gaussian_beliefs(self, beliefs: Any) -> Optional[Dict[str, np.ndarray]]:
        if isinstance(beliefs, dict) and 'mean' in beliefs and 'precision' in beliefs:
            return {
                'mean': np.asarray(beliefs['mean'], dtype=float),
                'precision': np.asarray(beliefs['precision'], dtype=float)
            }
        if self.generative_model is not None:
            gm_beliefs = getattr(self.generative_model, 'beliefs', None)
            if isinstance(gm_beliefs, dict) and 'mean' in gm_beliefs and 'precision' in gm_beliefs:
                return {
                    'mean': np.asarray(gm_beliefs['mean'], dtype=float),
                    'precision': np.asarray(gm_beliefs['precision'], dtype=float)
                }
        return None

    def _get_preferences_vector(self, length: Optional[int] = None) -> np.ndarray:
        vector = None
        
        # 1. Try to get state preferences directly
        if self.preferences is not None and isinstance(self.preferences, dict) and 'states' in self.preferences:
             vector = self._safe_flatten(self.preferences['states'])
        
        if vector is None and self.generative_model is not None:
             model_prefs = self._extract_model_preferences(self.generative_model)
             if isinstance(model_prefs, dict) and 'states' in model_prefs:
                 vector = self._safe_flatten(model_prefs['states'])
             elif isinstance(model_prefs, np.ndarray):
                 vector = self._safe_flatten(model_prefs)

        # 2. If no state preferences, try to map observation preferences to states
        if vector is None:
             obs_prefs = None
             if self.preferences and isinstance(self.preferences, dict) and 'observations' in self.preferences:
                  obs_prefs = self._safe_flatten(self.preferences['observations'])
             elif self.generative_model is not None:
                  model_prefs = self._extract_model_preferences(self.generative_model)
                  if isinstance(model_prefs, dict) and 'observations' in model_prefs:
                       obs_prefs = self._safe_flatten(model_prefs['observations'])
             
             if obs_prefs is not None:
                  # Use A matrix to map preferences: P(s) propto A.T @ P(o)
                  observation_model = getattr(self.generative_model, 'observation_model', None)
                  # Also support 'A' attribute directly if observation_model isn't set
                  if observation_model is None:
                       observation_model = getattr(self.generative_model, 'A', None)

                  if isinstance(observation_model, np.ndarray):
                       # Verify dimensions
                       # A is (obs_dim, state_dim)
                       # obs_prefs is (obs_dim)
                       if observation_model.shape[0] == len(obs_prefs):
                            vector = observation_model.T @ obs_prefs

        # 3. Fallback to uniform
        if vector is None:
            belief_vector = self._extract_belief_vector(self.current_beliefs)
            default_length = length if length is not None else (len(belief_vector) if belief_vector is not None else 1)
            vector = np.ones(default_length) / max(default_length, 1)

        if length is not None:
             vector = self._align_vector(vector, length)

        return normalize_distribution(vector)

    def _get_gaussian_preferences(self) -> Dict[str, np.ndarray]:
        prefs: Dict[str, np.ndarray] = {}
        if isinstance(self.preferences, dict):
            if 'mean' in self.preferences:
                prefs['mean'] = np.asarray(self.preferences['mean'], dtype=float)
            if 'precision' in self.preferences:
                prefs['precision'] = np.asarray(self.preferences['precision'], dtype=float)
        if not prefs and self.generative_model is not None:
            gm_prefs = getattr(self.generative_model, 'preferences', {})
            if isinstance(gm_prefs, dict):
                if 'mean' in gm_prefs:
                    prefs['mean'] = np.asarray(gm_prefs['mean'], dtype=float)
                if 'precision' in gm_prefs:
                    prefs['precision'] = np.asarray(gm_prefs['precision'], dtype=float)
        return prefs

    def _get_observation_vector(self, length: int) -> np.ndarray:
        if isinstance(self.current_observations, np.ndarray):
            obs = self.current_observations
        elif self.generative_model is not None:
            obs_dim = getattr(self.generative_model, 'obs_dim', length)
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
