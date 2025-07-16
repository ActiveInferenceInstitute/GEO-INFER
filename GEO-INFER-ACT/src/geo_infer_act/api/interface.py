"""
Active Inference API Interface for GEO-INFER-ACT.

This module provides a high-level interface for creating and managing
active inference models, including belief updating and policy selection.
"""
import numpy as np
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path

from geo_infer_act.core.generative_model import GenerativeModel
from geo_infer_act.core.free_energy import FreeEnergyCalculator
from geo_infer_act.core.policy_selection import PolicySelector
from geo_infer_act.core.variational_inference import VariationalInference
from geo_infer_act.utils.config import load_config
from geo_infer_act.utils.math import softmax, normalize_distribution

logger = logging.getLogger(__name__)


class ActiveInferenceInterface:
    """
    High-level interface for active inference models.
    
    This class provides a simplified API for creating, configuring,
    and running active inference models without requiring detailed
    knowledge of the underlying mathematical machinery.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the active inference interface.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path) if config_path else {}
        self.models = {}
        self.free_energy_calculator = FreeEnergyCalculator()
        self.policy_selector = PolicySelector()
        self.variational_inference = VariationalInference()
        
        logger.info("ActiveInferenceInterface initialized")
    
    def create_model(self, 
                    model_id: str, 
                    model_type: str, 
                    parameters: Dict[str, Any]) -> None:
        """
        Create a new active inference model.
        
        Args:
            model_id: Unique identifier for the model
            model_type: Type of model ('categorical', 'gaussian', 'hierarchical_gaussian')
            parameters: Model configuration parameters
        """
        # Enhanced parameters with more dynamic defaults
        enhanced_params = {
            'learning_rate': 0.1,
            'temporal_precision': 1.0,
            'state_transition_noise': 0.1,
            'observation_noise': 0.05,
            'enable_learning': True,
            'enable_adaptation': True,
            **parameters
        }
        
        model = GenerativeModel(
            model_type=model_type,
            parameters=enhanced_params,
            model_id=model_id
        )
        
        # Initialize with more interesting prior beliefs
        if model_type == "categorical":
            state_dim = enhanced_params.get('state_dim', 3)
            obs_dim = enhanced_params.get('obs_dim', 2)
            
            # Create more dynamic initial beliefs with some structure
            if state_dim <= 5:
                # For small state spaces, create structured priors
                initial_beliefs = np.ones(state_dim) / state_dim
                # Add some bias towards middle states for more interesting dynamics
                if state_dim >= 3:
                    initial_beliefs[state_dim//2] *= 2.0
                    initial_beliefs = normalize_distribution(initial_beliefs)
            else:
                # For larger state spaces, create more structured priors
                initial_beliefs = np.random.dirichlet(np.ones(state_dim) * 0.5)
            
            model.beliefs = {
                'states': initial_beliefs,
                'precision': enhanced_params.get('prior_precision', 1.0),
                'temporal_context': np.zeros(state_dim),
                'adaptation_rate': enhanced_params.get('learning_rate', 0.1)
            }
            
            # Initialize observation model with some structure
            A_matrix = np.random.dirichlet(np.ones(state_dim), size=obs_dim)
            model.observation_model = A_matrix
            
            # Initialize transition model with temporal structure
            B_matrix = np.eye(state_dim) * 0.7 + np.random.dirichlet(np.ones(state_dim), size=state_dim) * 0.3
            model.transition_model = B_matrix
            
        elif model_type == "gaussian":
            state_dim = enhanced_params.get('state_dim', 4)
            precision = enhanced_params.get('prior_precision', 1.0)
            
            # Initialize with structured Gaussian beliefs
            initial_mean = np.random.randn(state_dim) * 0.5
            initial_precision = np.eye(state_dim) * precision
            
            model.beliefs = {
                'mean': initial_mean,
                'precision': initial_precision,
                'temporal_context': np.zeros(state_dim),
                'adaptation_rate': enhanced_params.get('learning_rate', 0.1)
            }
            
        elif model_type == "hierarchical_gaussian":
            levels = enhanced_params.get('levels', 2)
            state_dims = enhanced_params.get('state_dims', [4, 2])
            
            model.beliefs = {}
            for level in range(levels):
                level_dim = state_dims[level] if level < len(state_dims) else 2
                level_precision = enhanced_params.get('prior_precision', 1.0) * (level + 1)
                
                model.beliefs[f'level_{level}'] = {
                    'mean': np.random.randn(level_dim) * 0.5,
                    'precision': np.eye(level_dim) * level_precision,
                    'temporal_context': np.zeros(level_dim),
                    'message_up': np.zeros(level_dim),
                    'message_down': np.zeros(level_dim)
                }
        
        self.models[model_id] = model
        logger.info(f"Created {model_type} model: {model_id}")
    
    def update_beliefs(self, 
                      model_id: str, 
                      observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Update model beliefs based on observations with enhanced dynamics.
        
        Args:
            model_id: Model identifier
            observations: Observed data
            
        Returns:
            Updated beliefs
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        if model.model_type == "categorical":
            return self._update_categorical_beliefs(model, observations)
        elif model.model_type == "gaussian":
            return self._update_gaussian_beliefs(model, observations)
        elif model.model_type == "hierarchical_gaussian":
            return self._update_hierarchical_beliefs(model, observations)
        else:
            raise ValueError(f"Unknown model type: {model.model_type}")
    
    def _update_categorical_beliefs(self, 
                                   model: GenerativeModel, 
                                   observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Update categorical beliefs with enhanced dynamics."""
        obs = observations.get('observations', np.array([1, 0]))
        
        # Get current beliefs
        current_beliefs = model.beliefs['states'].copy()
        learning_rate = model.beliefs.get('adaptation_rate', 0.1)
        
        # Simulate observation likelihood for each state
        state_dim = len(current_beliefs)
        obs_dim = len(obs)
        
        # Use observation model if available, otherwise create simple mapping
        if hasattr(model, 'observation_model') and model.observation_model is not None:
            # Observation model should be (obs_dim, state_dim), so we transpose for proper multiplication
            if isinstance(model.observation_model, np.ndarray):
                likelihood = model.observation_model.T @ obs  # Transpose to get (state_dim, obs_dim) @ (obs_dim,)
            else:
                # Handle dictionary format for hierarchical models
                likelihood = np.ones(state_dim) / state_dim
        else:
            # Create dynamic observation model based on observation pattern
            likelihood = np.zeros(state_dim)
            obs_index = np.argmax(obs) if obs.sum() > 0 else 0
            
            # Map observation to states with some uncertainty
            for i in range(state_dim):
                distance = abs(i - (obs_index * state_dim / obs_dim))
                likelihood[i] = np.exp(-distance / (state_dim / 4 + 0.1))
            
            likelihood = normalize_distribution(likelihood)
        
        # Bayesian update with temporal dynamics
        posterior_unnorm = current_beliefs * likelihood
        
        # Add temporal context for more interesting dynamics
        temporal_context = model.beliefs.get('temporal_context', np.zeros(state_dim))
        temporal_weight = 0.2
        posterior_unnorm += temporal_weight * temporal_context
        
        # Normalize
        posterior = normalize_distribution(posterior_unnorm)
        
        # Apply learning with momentum
        momentum = 0.8
        updated_beliefs = momentum * current_beliefs + (1 - momentum) * posterior
        updated_beliefs = normalize_distribution(updated_beliefs)
        
        # Update temporal context (exponential smoothing)
        temporal_decay = 0.9
        model.beliefs['temporal_context'] = temporal_decay * temporal_context + (1 - temporal_decay) * updated_beliefs
        
        # Store updated beliefs
        model.beliefs['states'] = updated_beliefs
        
        return {
            'states': updated_beliefs,
            'likelihood': likelihood,
            'temporal_context': model.beliefs['temporal_context']
        }
    
    def _update_gaussian_beliefs(self, 
                                model: GenerativeModel, 
                                observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Update Gaussian beliefs with enhanced dynamics."""
        obs = observations.get('observations', np.random.randn(model.beliefs['mean'].shape[0]))
        
        # Current belief parameters
        prior_mean = model.beliefs['mean'].copy()
        prior_precision = model.beliefs['precision'].copy()
        learning_rate = model.beliefs.get('adaptation_rate', 0.1)
        
        # Observation precision (inverse noise) - ensure dimensions match
        obs_dim = len(obs)
        state_dim = len(prior_mean)
        
        if obs_dim != state_dim:
            # Create compatible observation precision matrix
            obs_precision = np.eye(state_dim) * 10.0
            # Pad or truncate observation to match state dimension
            if obs_dim < state_dim:
                padded_obs = np.zeros(state_dim)
                padded_obs[:obs_dim] = obs
                obs = padded_obs
            else:
                obs = obs[:state_dim]
        else:
            obs_precision = np.eye(obs_dim) * 10.0
        
        # Bayesian update for Gaussian
        posterior_precision = prior_precision + obs_precision
        posterior_mean = np.linalg.solve(
            posterior_precision,
            prior_precision @ prior_mean + obs_precision @ obs
        )
        
        # Add temporal dynamics
        temporal_context = model.beliefs.get('temporal_context', np.zeros_like(prior_mean))
        temporal_weight = 0.1
        posterior_mean += temporal_weight * temporal_context
        
        # Apply learning with adaptation
        momentum = 0.7
        updated_mean = momentum * prior_mean + (1 - momentum) * posterior_mean
        updated_precision = momentum * prior_precision + (1 - momentum) * posterior_precision
        
        # Update temporal context
        temporal_decay = 0.85
        model.beliefs['temporal_context'] = temporal_decay * temporal_context + (1 - temporal_decay) * updated_mean
        
        # Store updated beliefs
        model.beliefs['mean'] = updated_mean
        model.beliefs['precision'] = updated_precision
        
        return {
            'mean': updated_mean,
            'precision': updated_precision,
            'covariance': np.linalg.inv(updated_precision + 1e-6 * np.eye(updated_precision.shape[0])),
            'temporal_context': model.beliefs['temporal_context']
        }
    
    def _update_hierarchical_beliefs(self, 
                                    model: GenerativeModel, 
                                    observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Update hierarchical beliefs with message passing."""
        updated_beliefs = {}
        
        # Update each level
        levels = [key for key in model.beliefs.keys() if key.startswith('level_')]
        levels.sort()
        
        for level_key in levels:
            level_idx = int(level_key.split('_')[1])
            level_beliefs = model.beliefs[level_key]
            
            # Get observations for this level
            if level_key in observations:
                level_obs = observations[level_key]
            else:
                # Use default or pass message from lower level
                level_obs = np.random.randn(len(level_beliefs['mean'])) * 0.5
            
            # Update similar to Gaussian case but with message passing
            prior_mean = level_beliefs['mean'].copy()
            prior_precision = level_beliefs['precision'].copy()
            
            # Incorporate messages from other levels
            message_up = level_beliefs.get('message_up', np.zeros_like(prior_mean))
            message_down = level_beliefs.get('message_down', np.zeros_like(prior_mean))
            
            # Combined prior with messages
            effective_mean = prior_mean + 0.1 * message_up + 0.1 * message_down
            
            # Observation update - ensure dimensions match
            obs_dim = len(level_obs)
            state_dim = len(prior_mean)
            
            if obs_dim != state_dim:
                # Create compatible observation precision matrix
                obs_precision = np.eye(state_dim) * 5.0
                # Pad or truncate observation to match state dimension
                if obs_dim < state_dim:
                    padded_obs = np.zeros(state_dim)
                    padded_obs[:obs_dim] = level_obs
                    level_obs = padded_obs
                else:
                    level_obs = level_obs[:state_dim]
            else:
                obs_precision = np.eye(obs_dim) * 5.0
            
            posterior_precision = prior_precision + obs_precision
            posterior_mean = np.linalg.solve(
                posterior_precision,
                prior_precision @ effective_mean + obs_precision @ level_obs
            )
            
            # Update with temporal dynamics
            temporal_context = level_beliefs.get('temporal_context', np.zeros_like(prior_mean))
            temporal_weight = 0.05 * (level_idx + 1)  # Higher levels change more slowly
            posterior_mean += temporal_weight * temporal_context
            
            # Store updated beliefs
            updated_beliefs[level_key] = {
                'mean': posterior_mean,
                'precision': posterior_precision,
                'temporal_context': 0.9 * temporal_context + 0.1 * posterior_mean,
                'message_up': level_beliefs.get('message_up', np.zeros_like(prior_mean)),
                'message_down': level_beliefs.get('message_down', np.zeros_like(prior_mean))
            }
            
            # Update model beliefs
            model.beliefs[level_key] = updated_beliefs[level_key]
        
        return updated_beliefs
    
    def select_policy(self, model_id: str) -> Dict[str, Any]:
        """
        Select optimal policy based on current beliefs with enhanced dynamics.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Selected policy information
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        # Create multiple policies with different characteristics
        n_policies = 5
        policies = []
        
        for i in range(n_policies):
            policy = {
                'id': i,
                'exploration_bonus': np.random.uniform(0.1, 0.5),
                'temporal_discount': np.random.uniform(0.8, 0.95),
                'risk_preference': np.random.uniform(-0.2, 0.3)
            }
            policies.append(policy)
        
        # Calculate expected free energy for each policy
        policy_values = []
        for policy in policies:
            if model.model_type == "categorical":
                if model.hierarchical:
                    states = model.beliefs['level_0']['states']
                else:
                    states = model.beliefs['states']
                entropy = -np.sum(states * np.log(states + 1e-8))
                exploration = policy['exploration_bonus'] * entropy
                risk_term = policy['risk_preference'] * np.var(states)
                discount = policy['temporal_discount']
                expected_free_energy = entropy - exploration + risk_term
                expected_free_energy *= discount
            else:
                if model.hierarchical:
                    precision = model.beliefs['level_0']['precision']
                else:
                    precision = model.beliefs.get('precision', np.eye(4))
                covariance = np.linalg.inv(precision + 1e-6 * np.eye(precision.shape[0]))
                uncertainty = np.trace(covariance)
                exploration = policy['exploration_bonus'] * uncertainty
                risk_term = policy['risk_preference'] * uncertainty
                expected_free_energy = uncertainty - exploration + risk_term
                expected_free_energy *= policy['temporal_discount']
            policy_values.append(expected_free_energy)
        
        policy_values = np.array(policy_values)
        policy_probs = softmax(-policy_values * 2.0)
        selected_idx = np.random.choice(len(policies), p=policy_probs)
        selected_policy = policies[selected_idx]
        return {
            'policy': selected_policy,
            'probability': policy_probs[selected_idx],
            'expected_free_energy': policy_values[selected_idx],
            'all_probabilities': policy_probs,
            'all_free_energies': policy_values
        }
    
    def set_preferences(self, model_id: str, preferences: Dict[str, Any]) -> None:
        """
        Set prior preferences for the model.
        
        Args:
            model_id: Model identifier
            preferences: Preference specifications
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        model.preferences = preferences
        
        # Adjust beliefs based on preferences
        if 'observations' in preferences and model.model_type == "categorical":
            pref_obs = preferences['observations']
            current_beliefs = model.beliefs['states']
            
            # Bias beliefs towards preferred observations
            preference_strength = 0.3
            state_dim = len(current_beliefs)
            obs_dim = len(pref_obs)
            
            # Map preferred observations to state preferences
            for i in range(state_dim):
                obs_index = i * obs_dim // state_dim
                if obs_index < len(pref_obs):
                    bias = preference_strength * pref_obs[obs_index]
                    current_beliefs[i] += bias
            
            model.beliefs['states'] = normalize_distribution(current_beliefs)
        
        logger.info(f"Set preferences for model {model_id}")
    
    def get_free_energy(self, model_id: str) -> float:
        """
        Calculate free energy for the current model state.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Free energy value
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        if model.model_type == "categorical":
            states = model.beliefs['states']
            # KL divergence from uniform distribution as simple free energy
            uniform = np.ones_like(states) / len(states)
            free_energy = np.sum(states * np.log(states / uniform + 1e-8))
            
            # Add complexity penalty
            entropy = -np.sum(states * np.log(states + 1e-8))
            free_energy += 0.1 * (1.0 - entropy / np.log(len(states)))
            
        else:
            # For Gaussian models, use trace of precision as simple free energy measure
            precision = model.beliefs.get('precision', np.eye(4))
            free_energy = np.trace(precision) / precision.shape[0]
        
        return float(free_energy) 