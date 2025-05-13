"""
Generative Model for Active Inference.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from scipy import stats
import torch

from geo_infer_act.core.free_energy import FreeEnergy


class GenerativeModel:
    """
    Generative model implementation for active inference.
    
    This class represents a probabilistic generative model of
    environment dynamics, which is used for belief updating and
    policy selection in active inference models.
    """
    
    def __init__(self, model_type: str, parameters: Dict[str, Any]):
        """
        Initialize a generative model.
        
        Args:
            model_type: Type of generative model
            parameters: Model parameters
        """
        self.model_type = model_type
        self.parameters = parameters
        self.prior_precision = parameters.get('prior_precision', 1.0)
        
        # Initialize state and observation spaces
        self.state_dim = parameters.get('state_dim', 1)
        self.obs_dim = parameters.get('obs_dim', 1)
        
        # Initialize beliefs (state estimation)
        self.beliefs = self._initialize_beliefs()
        
        # Initialize preferences
        self.preferences = self._initialize_preferences()
        
        # Initialize transition and observation models
        self.transition_model = self._initialize_transition_model()
        self.observation_model = self._initialize_observation_model()
        
        # Initialize free energy calculator
        self.free_energy_calculator = FreeEnergy()
        
    def _initialize_beliefs(self) -> Dict[str, np.ndarray]:
        """
        Initialize belief distributions.
        
        Returns:
            Initial belief distributions
        """
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
            
    def _initialize_preferences(self) -> Dict[str, np.ndarray]:
        """
        Initialize prior preferences.
        
        Returns:
            Prior preference distributions
        """
        if self.model_type == 'categorical':
            return {
                'observations': np.ones(self.obs_dim) / self.obs_dim
            }
        elif self.model_type == 'gaussian':
            return {
                'mean': np.zeros(self.obs_dim),
                'precision': np.eye(self.obs_dim)
            }
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _initialize_transition_model(self) -> Any:
        """
        Initialize the state transition model.
        
        Returns:
            State transition model
        """
        # This would typically be a matrix or function mapping states to successor states
        if self.model_type == 'categorical':
            # Return a uniform transition probability matrix
            return np.ones((self.state_dim, self.state_dim)) / self.state_dim
        elif self.model_type == 'gaussian':
            # Return a linear transition model: x_{t+1} = A * x_t + noise
            return {
                'A': np.eye(self.state_dim),  # Identity matrix by default
                'Q': np.eye(self.state_dim) * 0.01  # Small process noise
            }
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _initialize_observation_model(self) -> Any:
        """
        Initialize the observation model.
        
        Returns:
            Observation model
        """
        # This would typically be a matrix or function mapping states to observations
        if self.model_type == 'categorical':
            # Return a uniform observation probability matrix
            return np.ones((self.obs_dim, self.state_dim)) / self.obs_dim
        elif self.model_type == 'gaussian':
            # Return a linear observation model: y_t = C * x_t + noise
            return {
                'C': np.eye(min(self.obs_dim, self.state_dim)),  # Identity or rectangular matrix
                'R': np.eye(self.obs_dim) * 0.01  # Small observation noise
            }
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def update_beliefs(self, observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Update beliefs based on observations.
        
        Args:
            observations: Dictionary of observations
            
        Returns:
            Updated belief distributions
        """
        if self.model_type == 'categorical':
            # Categorical belief updating (Bayesian update)
            obs_vector = observations.get('observations')
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")
                
            # Compute likelihood: P(o|s)
            likelihood = np.zeros(self.state_dim)
            for state_idx in range(self.state_dim):
                likelihood[state_idx] = self._compute_likelihood(obs_vector, state_idx)
                
            # Apply Bayes rule: P(s|o) ∝ P(o|s) * P(s)
            posterior = likelihood * self.beliefs['states']
            posterior_normalized = posterior / posterior.sum()
            
            # Update beliefs
            self.beliefs['states'] = posterior_normalized
            
        elif self.model_type == 'gaussian':
            # Gaussian belief updating (Kalman filter)
            obs_vector = observations.get('observations')
            if obs_vector is None:
                raise ValueError("Observations must contain 'observations' key")
                
            # Prediction step
            pred_mean = self.transition_model['A'] @ self.beliefs['mean']
            pred_cov = self.transition_model['A'] @ np.linalg.inv(self.beliefs['precision']) @ \
                       self.transition_model['A'].T + self.transition_model['Q']
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
    
    def _compute_likelihood(self, observation: np.ndarray, state_idx: int) -> float:
        """
        Compute likelihood of observation given state.
        
        Args:
            observation: Observed data
            state_idx: State index
            
        Returns:
            Likelihood value
        """
        # P(o|s) from the observation model
        if self.model_type == 'categorical':
            return np.prod(self.observation_model[:, state_idx] ** observation)
        else:
            raise ValueError(f"Likelihood computation not implemented for {self.model_type}")
            
    def compute_free_energy(self) -> float:
        """
        Compute the variational free energy of the current model.
        
        Returns:
            Free energy value
        """
        return self.free_energy_calculator.compute(
            beliefs=self.beliefs,
            observation_model=self.observation_model,
            transition_model=self.transition_model,
            model_type=self.model_type
        )
    
    def set_preferences(self, preferences: Dict[str, np.ndarray]) -> None:
        """
        Set prior preferences.
        
        Args:
            preferences: Dictionary of preference distributions
        """
        self.preferences.update(preferences) 