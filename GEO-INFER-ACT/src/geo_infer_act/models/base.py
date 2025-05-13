"""
Base models for active inference framework.
"""
from typing import Dict, List, Optional, Any
import numpy as np
from abc import ABC, abstractmethod


class ActiveInferenceModel(ABC):
    """
    Base class for active inference models.
    
    This abstract base class defines the interface for
    all active inference models in the GEO-INFER-ACT module.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config if config is not None else {}
    
    @abstractmethod
    def step(self, actions: Optional[Any] = None) -> Any:
        """
        Advance the model by one step.
        
        Args:
            actions: Optional actions to apply
            
        Returns:
            Updated state or relevant information
        """
        pass
    
    def reset(self) -> Any:
        """
        Reset the model to initial state.
        
        Returns:
            Initial state
        """
        # Default implementation - should be overridden by subclasses
        pass
    
    def __str__(self) -> str:
        """Return string representation of model."""
        return f"{self.__class__.__name__}()"
    
    def __repr__(self) -> str:
        """Return string representation of model."""
        return self.__str__()


class CategoricalModel(ActiveInferenceModel):
    """
    Categorical active inference model.
    
    This model uses categorical distributions to represent
    beliefs and observations in discrete state spaces.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                state_dim: int = 1, obs_dim: int = 1):
        """
        Initialize categorical model.
        
        Args:
            config: Configuration dictionary
            state_dim: Dimension of state space
            obs_dim: Dimension of observation space
        """
        super().__init__(config)
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        
        # Initialize beliefs and preferences as uniform distributions
        self.beliefs = np.ones(state_dim) / state_dim
        self.preferences = np.ones(obs_dim) / obs_dim
        
        # Initialize transition and likelihood matrices
        self.transition_matrix = np.ones((state_dim, state_dim)) / state_dim
        self.likelihood_matrix = np.ones((obs_dim, state_dim)) / obs_dim
    
    def set_preferences(self, preferences: np.ndarray) -> None:
        """
        Set preference distribution.
        
        Args:
            preferences: Preference distribution
        """
        if preferences.shape != (self.obs_dim,):
            raise ValueError(f"Preferences must have shape ({self.obs_dim},)")
        
        # Normalize
        preferences = preferences / np.sum(preferences)
        self.preferences = preferences
    
    def set_transition_matrix(self, transition_matrix: np.ndarray) -> None:
        """
        Set state transition matrix.
        
        Args:
            transition_matrix: Transition probability matrix
        """
        expected_shape = (self.state_dim, self.state_dim)
        if transition_matrix.shape != expected_shape:
            raise ValueError(f"Transition matrix must have shape {expected_shape}")
        
        # Normalize rows
        transition_matrix = transition_matrix / np.sum(transition_matrix, axis=1, keepdims=True)
        self.transition_matrix = transition_matrix
    
    def set_likelihood_matrix(self, likelihood_matrix: np.ndarray) -> None:
        """
        Set observation likelihood matrix.
        
        Args:
            likelihood_matrix: Likelihood matrix
        """
        expected_shape = (self.obs_dim, self.state_dim)
        if likelihood_matrix.shape != expected_shape:
            raise ValueError(f"Likelihood matrix must have shape {expected_shape}")
        
        # Normalize columns
        col_sums = np.sum(likelihood_matrix, axis=0, keepdims=True)
        likelihood_matrix = likelihood_matrix / col_sums
        self.likelihood_matrix = likelihood_matrix
    
    def update_beliefs(self, observation: np.ndarray) -> np.ndarray:
        """
        Update beliefs given observation.
        
        Args:
            observation: Observation vector (one-hot encoded)
            
        Returns:
            Updated belief distribution
        """
        if observation.shape != (self.obs_dim,):
            raise ValueError(f"Observation must have shape ({self.obs_dim},)")
        
        # Likelihood of observation given each state
        likelihood = np.prod(self.likelihood_matrix ** observation[:, np.newaxis], axis=0)
        
        # Posterior (unnormalized)
        posterior = likelihood * self.beliefs
        
        # Normalize
        posterior = posterior / np.sum(posterior)
        
        # Update beliefs
        self.beliefs = posterior
        
        return self.beliefs
    
    def step(self, action: Optional[int] = None) -> np.ndarray:
        """
        Advance the model by one step.
        
        Args:
            action: Optional action index
            
        Returns:
            New belief distribution
        """
        # Apply dynamics (prediction step)
        predicted_belief = self.transition_matrix.T @ self.beliefs
        
        # Update beliefs
        self.beliefs = predicted_belief
        
        return self.beliefs
    
    def reset(self) -> np.ndarray:
        """
        Reset beliefs to uniform distribution.
        
        Returns:
            Initial belief distribution
        """
        self.beliefs = np.ones(self.state_dim) / self.state_dim
        return self.beliefs


class GaussianModel(ActiveInferenceModel):
    """
    Gaussian active inference model.
    
    This model uses multivariate Gaussian distributions to represent
    beliefs and observations in continuous state spaces.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None,
                state_dim: int = 1, obs_dim: int = 1):
        """
        Initialize Gaussian model.
        
        Args:
            config: Configuration dictionary
            state_dim: Dimension of state space
            obs_dim: Dimension of observation space
        """
        super().__init__(config)
        self.state_dim = state_dim
        self.obs_dim = obs_dim
        
        # Initialize beliefs
        self.belief_mean = np.zeros(state_dim)
        self.belief_cov = np.eye(state_dim)
        
        # Initialize preferences
        self.preference_mean = np.zeros(obs_dim)
        self.preference_cov = np.eye(obs_dim)
        
        # Initialize transition and observation models
        self.A = np.eye(state_dim)  # State transition matrix
        self.B = np.zeros((state_dim, 1))  # Control input matrix
        self.C = np.eye(min(obs_dim, state_dim))  # Observation matrix
        
        # Initialize noise covariances
        self.Q = np.eye(state_dim) * 0.01  # Process noise
        self.R = np.eye(obs_dim) * 0.01  # Observation noise
    
    def set_preferences(self, mean: np.ndarray, cov: np.ndarray) -> None:
        """
        Set preference distribution.
        
        Args:
            mean: Preference mean
            cov: Preference covariance
        """
        if mean.shape != (self.obs_dim,):
            raise ValueError(f"Preference mean must have shape ({self.obs_dim},)")
        
        if cov.shape != (self.obs_dim, self.obs_dim):
            raise ValueError(f"Preference covariance must have shape ({self.obs_dim}, {self.obs_dim})")
        
        self.preference_mean = mean
        self.preference_cov = cov
    
    def set_transition_model(self, A: np.ndarray, B: Optional[np.ndarray] = None,
                           Q: Optional[np.ndarray] = None) -> None:
        """
        Set transition model parameters.
        
        Args:
            A: State transition matrix
            B: Control input matrix
            Q: Process noise covariance
        """
        expected_A_shape = (self.state_dim, self.state_dim)
        if A.shape != expected_A_shape:
            raise ValueError(f"A matrix must have shape {expected_A_shape}")
        
        self.A = A
        
        if B is not None:
            expected_B_shape = (self.state_dim, 1)
            if B.shape[0] != self.state_dim:
                raise ValueError(f"B matrix must have shape ({self.state_dim}, control_dim)")
            self.B = B
        
        if Q is not None:
            expected_Q_shape = (self.state_dim, self.state_dim)
            if Q.shape != expected_Q_shape:
                raise ValueError(f"Q matrix must have shape {expected_Q_shape}")
            self.Q = Q
    
    def set_observation_model(self, C: np.ndarray, R: Optional[np.ndarray] = None) -> None:
        """
        Set observation model parameters.
        
        Args:
            C: Observation matrix
            R: Observation noise covariance
        """
        expected_C_shape = (self.obs_dim, self.state_dim)
        if C.shape != expected_C_shape:
            raise ValueError(f"C matrix must have shape {expected_C_shape}")
        
        self.C = C
        
        if R is not None:
            expected_R_shape = (self.obs_dim, self.obs_dim)
            if R.shape != expected_R_shape:
                raise ValueError(f"R matrix must have shape {expected_R_shape}")
            self.R = R
    
    def update_beliefs(self, observation: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Update beliefs given observation (Kalman filter).
        
        Args:
            observation: Observation vector
            
        Returns:
            Updated belief distribution (mean and covariance)
        """
        if observation.shape != (self.obs_dim,):
            raise ValueError(f"Observation must have shape ({self.obs_dim},)")
        
        # Prediction step
        predicted_mean = self.A @ self.belief_mean
        predicted_cov = self.A @ self.belief_cov @ self.A.T + self.Q
        
        # Update step (Kalman filter)
        K = predicted_cov @ self.C.T @ np.linalg.inv(self.C @ predicted_cov @ self.C.T + self.R)
        
        updated_mean = predicted_mean + K @ (observation - self.C @ predicted_mean)
        updated_cov = (np.eye(self.state_dim) - K @ self.C) @ predicted_cov
        
        # Update beliefs
        self.belief_mean = updated_mean
        self.belief_cov = updated_cov
        
        return {
            "mean": self.belief_mean,
            "cov": self.belief_cov
        }
    
    def step(self, control: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Advance the model by one step.
        
        Args:
            control: Optional control input
            
        Returns:
            New belief distribution
        """
        # Apply dynamics (prediction step)
        if control is not None:
            predicted_mean = self.A @ self.belief_mean + self.B @ control
        else:
            predicted_mean = self.A @ self.belief_mean
            
        predicted_cov = self.A @ self.belief_cov @ self.A.T + self.Q
        
        # Update beliefs
        self.belief_mean = predicted_mean
        self.belief_cov = predicted_cov
        
        return {
            "mean": self.belief_mean,
            "cov": self.belief_cov
        }
    
    def reset(self) -> Dict[str, np.ndarray]:
        """
        Reset beliefs to initial state.
        
        Returns:
            Initial belief distribution
        """
        self.belief_mean = np.zeros(self.state_dim)
        self.belief_cov = np.eye(self.state_dim)
        
        return {
            "mean": self.belief_mean,
            "cov": self.belief_cov
        } 