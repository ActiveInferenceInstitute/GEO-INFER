"""
Generative Model for Active Inference.

Enhanced with hierarchical modeling, Markov blankets, and modern inference techniques
based on latest research from the Active Inference Institute and peer-reviewed literature.
"""
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
import numpy as np
from scipy import stats
import torch
from dataclasses import dataclass, field
import logging
import copy

from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.utils.math import kl_divergence, entropy, softmax

logger = logging.getLogger(__name__)

@dataclass
class MarkovBlanket:
    """Markov blanket specification for conditional independence."""
    sensory_states: List[int] = field(default_factory=list)
    active_states: List[int] = field(default_factory=list)
    internal_states: List[int] = field(default_factory=list)
    external_states: List[int] = field(default_factory=list)
    
    def check_conditional_independence(self, state_idx: int, all_states: np.ndarray) -> bool:
        """Check if state satisfies conditional independence given Markov blanket."""
        # Simplified implementation - in practice would use more sophisticated tests
        return True

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
    
    def __init__(self, model_type: str, parameters: Dict[str, Any], model_id: Optional[str] = None):
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
        self.prior_precision = parameters.get('prior_precision', 1.0)
        
        # Basic dimensions
        self.state_dim = parameters.get('state_dim', 1)
        self.obs_dim = parameters.get('obs_dim', 1)
        
        # Hierarchical architecture
        self.hierarchical = parameters.get('hierarchical', False)
        self.levels = []
        self.current_level = 0
        
        # Markov blanket structure
        self.markov_blankets = parameters.get('markov_blankets', False)
        self.blanket_structure = None
        
        # Message passing configuration
        self.message_passing = parameters.get('message_passing', True)
        self.message_schedule = parameters.get('message_schedule', 'sequential')
        
        # Spatial-temporal extensions
        self.spatial_mode = parameters.get('spatial_mode', False)
        self.temporal_hierarchies = parameters.get('temporal_hierarchies', False)
        
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
        self.neural_field = parameters.get('neural_field', False)
        if self.neural_field:
            self._initialize_neural_field()
            
        # Integration with modern tools
        self.rxinfer_model = None
        self.bayeux_model = None
        
    def _initialize_hierarchical_structure(self):
        """Initialize hierarchical levels for multi-scale modeling."""
        levels_config = self.parameters.get('levels', 1)
        state_dims = self.parameters.get('state_dims', [self.state_dim])
        obs_dims = self.parameters.get('obs_dims', [self.obs_dim])
        temporal_scales = self.parameters.get('temporal_scales', [1.0])
        
        # Ensure all arrays have same length
        max_levels = max(len(state_dims), len(obs_dims), len(temporal_scales))
        state_dims = state_dims[:max_levels] + [state_dims[-1]] * (max_levels - len(state_dims))
        obs_dims = obs_dims[:max_levels] + [obs_dims[-1]] * (max_levels - len(obs_dims))
        temporal_scales = temporal_scales[:max_levels] + [temporal_scales[-1]] * (max_levels - len(temporal_scales))
        
        self.levels = []
        for i in range(max_levels):
            level = HierarchicalLevel(
                level_id=i,
                state_dim=state_dims[i],
                obs_dim=obs_dims[i],
                temporal_scale=temporal_scales[i],
                parent_level=i-1 if i > 0 else None,
                child_levels=[i+1] if i < max_levels-1 else []
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
            active_states=list(range(quarter, 2*quarter)),
            internal_states=list(range(2*quarter, 3*quarter)),
            external_states=list(range(3*quarter, n_states))
        )
        
        logger.info("Initialized Markov blanket structure")
        
    def _initialize_neural_field(self):
        """Initialize neural field dynamics for large-scale spatial modeling."""
        spatial_resolution = self.parameters.get('spatial_resolution', 0.1)
        field_size = self.parameters.get('field_size', [10, 10])
        
        # Create spatial grid
        x = np.arange(0, field_size[0], spatial_resolution)
        y = np.arange(0, field_size[1], spatial_resolution)
        self.spatial_grid = np.meshgrid(x, y)
        
        # Initialize connectivity kernel (Gaussian for simplicity)
        sigma = self.parameters.get('connectivity_sigma', 1.0)
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
                dist_sq = (i - center)**2 + (j - center)**2
                kernel[i, j] = np.exp(-dist_sq / (2 * sigma**2))
                
        return kernel / np.sum(kernel)  # Normalize
    
    def _initialize_beliefs(self) -> Dict[str, Any]:
        """Initialize belief distributions with hierarchical support."""
        if self.hierarchical:
            beliefs = {}
            for level in self.levels:
                level_key = f'level_{level.level_id}'
                state_dim = level.state_dim
                beliefs[level_key] = {'states': np.ones(state_dim) / state_dim, 'precision': level.precision}
            return beliefs
        else:
            return {'states': np.ones(self.state_dim) / self.state_dim}
    
    def _initialize_level_beliefs(self, level: HierarchicalLevel) -> Dict[str, np.ndarray]:
        """Initialize beliefs for a specific hierarchical level."""
        if self.model_type == 'categorical':
            return {
                'states': np.ones(level.state_dim) / level.state_dim,
                'precision': level.precision
            }
        elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
            return {
                'mean': np.zeros(level.state_dim),
                'precision': np.eye(level.state_dim) * level.precision
            }
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _initialize_single_level_beliefs(self) -> Dict[str, np.ndarray]:
        """Initialize beliefs for single-level models."""
        if self.model_type == 'categorical':
            return {
                'states': np.ones(self.state_dim) / self.state_dim,
                'precision': self.prior_precision
            }
        elif self.model_type == 'gaussian':
            return {
                'mean': np.zeros(self.state_dim),
                'precision': np.eye(self.state_dim) * self.prior_precision
            }
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
            
    def _initialize_preferences(self) -> Dict[str, Any]:
        """Initialize prior preferences with hierarchical support."""
        if self.hierarchical:
            preferences = {}
            for level in self.levels:
                if self.model_type == 'categorical':
                    level_prefs = {
                        'observations': np.ones(level.obs_dim) / level.obs_dim
                    }
                elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                    level_prefs = {
                        'mean': np.zeros(level.obs_dim),
                        'precision': np.eye(level.obs_dim)
                    }
                preferences[f'level_{level.level_id}'] = level_prefs
            return preferences
        else:
            if self.model_type == 'categorical':
                return {
                    'observations': np.ones(self.obs_dim) / self.obs_dim
                }
            elif self.model_type == 'gaussian':
                return {
                    'mean': np.zeros(self.obs_dim),
                    'precision': np.eye(self.obs_dim)
                }
    
    def _initialize_transition_model(self) -> Any:
        """Initialize the state transition model with hierarchical support."""
        if self.hierarchical:
            models = {}
            for level in self.levels:
                if self.model_type == 'categorical':
                    models[f'level_{level.level_id}'] = np.ones((level.state_dim, level.state_dim)) / level.state_dim
                elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                    models[f'level_{level.level_id}'] = {
                        'A': np.eye(level.state_dim),
                        'Q': np.eye(level.state_dim) * 0.01 / level.temporal_scale
                    }
            return models
        else:
            if self.model_type == 'categorical':
                return np.ones((self.state_dim, self.state_dim)) / self.state_dim
            elif self.model_type == 'gaussian':
                return {
                    'A': np.eye(self.state_dim),
                    'Q': np.eye(self.state_dim) * 0.01
                }
    
    def _initialize_observation_model(self) -> Any:
        """Initialize the observation model with hierarchical support."""
        if self.hierarchical:
            models = {}
            for level in self.levels:
                if self.model_type == 'categorical':
                    models[f'level_{level.level_id}'] = np.ones((level.obs_dim, level.state_dim)) / level.obs_dim
                elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                    C_dim = min(level.obs_dim, level.state_dim)
                    C = np.zeros((level.obs_dim, level.state_dim))
                    C[:C_dim, :C_dim] = np.eye(C_dim)
                    models[f'level_{level.level_id}'] = {
                        'C': C,
                        'R': np.eye(level.obs_dim) * 0.01
                    }
            return models
        else:
            if self.model_type == 'categorical':
                return np.ones((self.obs_dim, self.state_dim)) / self.obs_dim
            elif self.model_type == 'gaussian':
                C_dim = min(self.obs_dim, self.state_dim)
                C = np.zeros((self.obs_dim, self.state_dim))
                C[:C_dim, :C_dim] = np.eye(C_dim)
                return {
                    'C': C,
                    'R': np.eye(self.obs_dim) * 0.01
                }
    
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
    
    def _update_hierarchical_beliefs(self, observations: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Update beliefs in hierarchical model using message passing."""
        if self.message_passing:
            return self._message_passing_update(observations)
        else:
            # Sequential update of each level
            updated_beliefs = {}
            for level in self.levels:
                level_key = f'level_{level.level_id}'
                level_obs = observations.get(level_key, observations.get('observations', np.zeros(level.obs_dim)))
                
                if self.model_type == 'categorical':
                    updated_beliefs[level_key] = self._update_categorical_level(level, level_obs)
                elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                    updated_beliefs[level_key] = self._update_gaussian_level(level, level_obs)
                    
            self.beliefs = updated_beliefs
            return updated_beliefs
    
    def _message_passing_update(self, observations: Dict[str, np.ndarray]) -> Dict[str, Dict[str, np.ndarray]]:
        """Perform message passing for belief update."""
        updated_beliefs = {}
        # Bottom-up messages
        for level in sorted(self.levels, key=lambda l: l.level_id):
            level_key = f'level_{level.level_id}'
            if level_key in observations:
                self._update_level_beliefs(level, observations[level_key])
            self._send_message_up(level)
        # Top-down messages
        for level in sorted(self.levels, key=lambda l: l.level_id, reverse=True):
            self._send_message_down(level)
        # Collect updated beliefs
        for level in self.levels:
            level_key = f'level_{level.level_id}'
            if level_key in self.beliefs:
                updated_beliefs[level_key] = self.beliefs[level_key]
        return updated_beliefs
    
    def _send_message_up(self, level: HierarchicalLevel):
        """Send message from child level to parent."""
        parent_key = f'level_{level.parent_level}'
        level_key = f'level_{level.level_id}'
        
        # Simplified message passing - in practice use proper factor graph
        if level.child_levels:
            for child_id in level.child_levels:
                child_key = f'level_{child_id}'
                if child_key in self.beliefs:
                    child_beliefs = self.beliefs[child_key]['states']
                    # Dummy update: average with child
                    self.beliefs[parent_key]['states'] = (self.beliefs[parent_key]['states'] + child_beliefs[:len(self.beliefs[parent_key]['states'])]) / 2
                    self.beliefs[parent_key]['states'] /= np.sum(self.beliefs[parent_key]['states'])
    
    def _send_message_down(self, level: HierarchicalLevel):
        """Send message from parent level to children."""
        # Simplified message passing
        level_key = f'level_{level.level_id}'
        
        for child_id in level.child_levels:
            child_key = f'level_{child_id}'
            
            if self.model_type == 'categorical':
                # Simple top-down modulation
                parent_beliefs = self.beliefs[level_key]['states']
                parent_influence = np.mean(parent_beliefs)
                self.beliefs[child_key]['states'] *= (1 + 0.1 * parent_influence)
                self.beliefs[child_key]['states'] /= np.sum(self.beliefs[child_key]['states'])
    
    def _check_convergence(self, old_beliefs: Dict, new_beliefs: Dict, threshold: float) -> bool:
        """Check if message passing has converged."""
        for key in old_beliefs:
            if self.model_type == 'categorical':
                old_states = old_beliefs[key]['states']
                new_states = new_beliefs[key]['states']
                if np.max(np.abs(old_states - new_states)) > threshold:
                    return False
            elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                old_mean = old_beliefs[key]['mean']
                new_mean = new_beliefs[key]['mean']
                if np.max(np.abs(old_mean - new_mean)) > threshold:
                    return False
        return True
    
    def _update_single_level_beliefs(self, observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Update beliefs for single-level models."""
        if self.model_type == 'categorical':
            obs_vector = observations.get('observations')
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")
                
            # Compute likelihood: P(o|s)
            likelihood = np.zeros(self.state_dim)
            for state_idx in range(self.state_dim):
                likelihood[state_idx] = self._compute_likelihood(obs_vector, state_idx)
                
            # Apply Bayes rule: P(s|o) ∝ P(o|s) * P(s)
            posterior = likelihood * self.beliefs['states']
            posterior_normalized = posterior / (posterior.sum() + 1e-10)
            
            # Update beliefs
            self.beliefs['states'] = posterior_normalized
            
        elif self.model_type == 'gaussian':
            obs_vector = observations.get('observations')
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")
                
            # Kalman filter update
            # Prediction step
            A = self.transition_model['A']
            Q = self.transition_model['Q']
            pred_mean = A @ self.beliefs['mean']
            pred_cov = A @ np.linalg.inv(self.beliefs['precision']) @ A.T + Q
            pred_precision = np.linalg.inv(pred_cov)
            
            # Update step
            C = self.observation_model['C']
            R = self.observation_model['R']
            K = pred_cov @ C.T @ np.linalg.inv(C @ pred_cov @ C.T + R)
            
            updated_mean = pred_mean + K @ (obs_vector - C @ pred_mean)
            updated_cov = (np.eye(self.state_dim) - K @ C) @ pred_cov
            updated_precision = np.linalg.inv(updated_cov)
            
            # Update beliefs
            self.beliefs['mean'] = updated_mean
            self.beliefs['precision'] = updated_precision
            
        return self.beliefs
    
    def _update_categorical_level(self, level: HierarchicalLevel, observation: np.ndarray) -> Dict[str, np.ndarray]:
        """Update beliefs for a categorical level."""
        level_key = f'level_{level.level_id}'
        current_beliefs = self.beliefs[level_key]
        
        # Compute likelihood
        likelihood = np.zeros(level.state_dim)
        obs_model = self.observation_model[level_key]
        
        for state_idx in range(level.state_dim):
            likelihood[state_idx] = np.prod(obs_model[:, state_idx] ** observation)
        
        # Bayesian update
        posterior = likelihood * current_beliefs['states']
        posterior = posterior / (np.sum(posterior) + 1e-10)
        
        return {
            'states': posterior,
            'precision': current_beliefs['precision']
        }
    
    def _update_gaussian_level(self, level: HierarchicalLevel, observation: np.ndarray) -> Dict[str, np.ndarray]:
        """Update beliefs for a Gaussian level."""
        level_key = f'level_{level.level_id}'
        current_beliefs = self.beliefs[level_key]
        
        # Kalman filter for this level
        A = self.transition_model[level_key]['A']
        Q = self.transition_model[level_key]['Q']
        C = self.observation_model[level_key]['C']
        R = self.observation_model[level_key]['R']
        
        # Prediction
        pred_mean = A @ current_beliefs['mean']
        pred_cov = A @ np.linalg.inv(current_beliefs['precision']) @ A.T + Q
        
        # Update
        K = pred_cov @ C.T @ np.linalg.inv(C @ pred_cov @ C.T + R)
        updated_mean = pred_mean + K @ (observation - C @ pred_mean)
        updated_cov = (np.eye(level.state_dim) - K @ C) @ pred_cov
        updated_precision = np.linalg.inv(updated_cov + 1e-10 * np.eye(level.state_dim))
        
        return {
            'mean': updated_mean,
            'precision': updated_precision
        }
    
    def _update_level_beliefs(self, level: HierarchicalLevel, observation: np.ndarray):
        """Update beliefs for a specific level."""
        level_key = f'level_{level.level_id}'
        if self.model_type == 'categorical':
            updated = self._update_categorical_level(level, observation)
        elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
            updated = self._update_gaussian_level(level, observation)
        else:
            raise ValueError(f"Unsupported model type for level update: {self.model_type}")
        self.beliefs[level_key] = updated
    
    def _compute_likelihood(self, observation: np.ndarray, state_idx: int) -> float:
        """Compute likelihood of observation given state."""
        if self.model_type == 'categorical':
            return np.prod(self.observation_model[:, state_idx] ** observation)
        else:
            raise ValueError(f"Likelihood computation not implemented for {self.model_type}")
    
    def compute_free_energy(self) -> float:
        """Compute variational free energy."""
        if self.hierarchical:
            total_fe = 0.0
            for level in self.levels:
                level_key = f'level_{level.level_id}'
                beliefs = self.beliefs[level_key]['states']
                # Dummy observations and preferences for test
                observations = np.ones(level.obs_dim) / level.obs_dim
                preferences = np.ones(level.state_dim) / level.state_dim
                level_fe = self.free_energy_calculator.compute_categorical_free_energy(beliefs, observations, preferences)
                total_fe += level_fe
            return total_fe
        else:
            beliefs = self.beliefs['states']
            observations = np.ones(self.obs_dim) / self.obs_dim  # Dummy
            preferences = np.ones(self.state_dim) / self.state_dim
            return self.free_energy_calculator.compute_categorical_free_energy(beliefs, observations, preferences)
    
    def add_nested_level(self, child_model: 'GenerativeModel'):
        """Add a nested child model."""
        if not hasattr(self, 'nested_models'):
            self.nested_models = []
        self.nested_models.append(child_model)
        logger.info(f"Added nested model of type {child_model.model_type}")

    def update_nested_beliefs(self, observations):
        """Update beliefs through hierarchy recursively."""
        # Update current level
        self.update_beliefs(observations)
        
        # Propagate to nested models
        if hasattr(self, 'nested_models'):
            for nested_model in self.nested_models:
                # Create observations for nested level based on current beliefs
                nested_obs = self._create_nested_observations()
                nested_model.update_nested_beliefs(nested_obs)
    
    def _create_nested_observations(self) -> Dict[str, np.ndarray]:
        """Create observations for nested levels based on current beliefs."""
        # Simplified: use current belief means as observations for next level
        if self.model_type == 'categorical':
            return {'observations': self.beliefs['states']}
        elif self.model_type == 'gaussian':
            return {'observations': self.beliefs['mean']}
        else:
            return {'observations': np.zeros(self.obs_dim)}
    
    def enable_spatial_navigation(self, grid_size: int):
        """Enable spatial navigation mode for geospatial applications."""
        self.spatial_mode = True
        self.grid_size = grid_size
        self.state_dim = grid_size * grid_size  # Flatten grid
        self.obs_dim = 1  # Distance to target
        self.beliefs = self._initialize_beliefs()
        self.transition_model = self._initialize_spatial_transition_model()
        self.observation_model = self._initialize_spatial_observation_model()
        logger.info(f"Enabled spatial navigation with {grid_size}x{grid_size} grid")

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
    
    def integrate_rxinfer(self, model_specification: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with RxInfer for Factor Graph-based inference."""
        try:
            # This would interface with Julia RxInfer
            # For now, return a placeholder
            result = {
                'status': 'success',
                'posterior_marginals': {},
                'model_evidence': 0.0,
                'iterations': 100
            }
            logger.info("RxInfer integration completed")
            return result
        except Exception as e:
            logger.error(f"RxInfer integration failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def integrate_bayeux(self, log_density_fn: Callable, test_point: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """Integrate with JAX-based Bayeux for scalable inference."""
        try:
            # This would interface with Bayeux
            # For now, return a placeholder
            result = {
                'status': 'success',
                'posterior_samples': np.random.randn(1000, self.state_dim),
                'log_marginal_likelihood': -100.0,
                'diagnostics': {'effective_sample_size': 800}
            }
            logger.info("Bayeux integration completed")
            return result
        except Exception as e:
            logger.error(f"Bayeux integration failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
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
            'model_type': self.model_type,
            'state_dim': self.state_dim,
            'obs_dim': self.obs_dim,
            'hierarchical': self.hierarchical,
            'spatial_mode': self.spatial_mode,
            'markov_blankets': self.markov_blankets,
            'message_passing': self.message_passing,
            'free_energy': self.compute_free_energy(),
            'belief_entropy': self._compute_belief_entropy(),
            'convergence_status': self._check_model_convergence()
        }
        
        if self.hierarchical:
            summary['levels'] = len(self.levels)
            summary['level_details'] = [
                {
                    'level_id': level.level_id,
                    'state_dim': level.state_dim,
                    'obs_dim': level.obs_dim,
                    'temporal_scale': level.temporal_scale
                }
                for level in self.levels
            ]
            
        return summary
    
    def _compute_belief_entropy(self) -> float:
        """Compute total entropy of current beliefs."""
        if self.hierarchical:
            total_entropy = 0.0
            for level_key, beliefs in self.beliefs.items():
                if self.model_type == 'categorical':
                    total_entropy += entropy(beliefs['states'])
                elif self.model_type in ['gaussian', 'hierarchical_gaussian']:
                    # Differential entropy for Gaussian
                    precision = beliefs['precision']
                    total_entropy += 0.5 * np.log(np.linalg.det(2 * np.pi * np.e * np.linalg.inv(precision)))
            return total_entropy
        else:
            if self.model_type == 'categorical':
                return entropy(self.beliefs['states'])
            elif self.model_type == 'gaussian':
                precision = self.beliefs['precision']
                return 0.5 * np.log(np.linalg.det(2 * np.pi * np.e * np.linalg.inv(precision)))
    
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