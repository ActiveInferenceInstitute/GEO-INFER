"""
Belief updating for Active Inference models.
"""
from typing import Dict, List, Optional, Any
import numpy as np
from scipy import stats

from geo_infer_act.utils.math import kl_divergence, entropy


class BayesianBeliefUpdate:
    """
    Bayesian belief updating for active inference models.
    
    This class implements various methods for updating beliefs
    based on new observations and prior knowledge.
    """
    
    def __init__(self, prior_precision: float = 1.0):
        """
        Initialize the belief updater.
        
        Args:
            prior_precision: Precision of prior beliefs
        """
        self.prior_precision = prior_precision
    
    def update_categorical(self, 
                          prior_beliefs: np.ndarray,
                          observation: np.ndarray,
                          likelihood_matrix: np.ndarray) -> np.ndarray:
        """
        Update categorical beliefs using Bayes' rule.
        
        Args:
            prior_beliefs: Prior belief distribution
            observation: Observed data
            likelihood_matrix: Likelihood of observations given states
            
        Returns:
            Updated posterior beliefs
        """
        # Compute likelihood for each state
        likelihood = np.zeros(len(prior_beliefs))
        for state_idx in range(len(prior_beliefs)):
            likelihood[state_idx] = np.prod(
                likelihood_matrix[:, state_idx] ** observation
            )
        
        # Apply Bayes' rule
        posterior = likelihood * prior_beliefs
        posterior = posterior / (np.sum(posterior) + 1e-10)
        
        return posterior
    
    def update_gaussian(self,
                       prior_mean: np.ndarray,
                       prior_precision: np.ndarray,
                       observation: np.ndarray,
                       observation_matrix: np.ndarray,
                       observation_precision: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Update Gaussian beliefs using Kalman filter equations.
        
        Args:
            prior_mean: Prior mean
            prior_precision: Prior precision matrix
            observation: Observed data
            observation_matrix: Observation matrix (H)
            observation_precision: Observation precision matrix
            
        Returns:
            Updated mean and precision
        """
        # Convert precision to covariance for computation
        prior_cov = np.linalg.inv(prior_precision)
        obs_cov = np.linalg.inv(observation_precision)
        
        # Kalman filter update
        H = observation_matrix
        K = prior_cov @ H.T @ np.linalg.inv(H @ prior_cov @ H.T + obs_cov)
        
        # Updated mean
        posterior_mean = prior_mean + K @ (observation - H @ prior_mean)
        
        # Updated covariance
        posterior_cov = (np.eye(len(prior_mean)) - K @ H) @ prior_cov
        
        # Convert back to precision
        posterior_precision = np.linalg.inv(posterior_cov)
        
        return {
            'mean': posterior_mean,
            'precision': posterior_precision
        }
    
    def compute_prediction_error(self,
                               prediction: np.ndarray,
                               observation: np.ndarray,
                               precision: float = 1.0) -> float:
        """
        Compute precision-weighted prediction error.
        
        Args:
            prediction: Predicted observation
            observation: Actual observation
            precision: Precision weight
            
        Returns:
            Prediction error
        """
        error = observation - prediction
        return precision * np.sum(error ** 2)
    
    def compute_surprise(self,
                        observation: np.ndarray,
                        predicted_distribution: np.ndarray) -> float:
        """
        Compute surprise (negative log probability) of observation.
        
        Args:
            observation: Observed data
            predicted_distribution: Predicted probability distribution
            
        Returns:
            Surprise value
        """
        # For categorical observations
        if observation.ndim == 1 and np.allclose(np.sum(observation), 1.0):
            prob = np.sum(observation * predicted_distribution)
            return -np.log(prob + 1e-10)
        
        # For continuous observations (simplified Gaussian assumption)
        else:
            mean = np.mean(predicted_distribution)
            var = np.var(predicted_distribution)
            return 0.5 * ((observation - mean) ** 2 / var + np.log(2 * np.pi * var)) 

    def update_beliefs(self, prior_beliefs: np.ndarray, observation: np.ndarray, likelihood: np.ndarray) -> np.ndarray:
        """General belief update dispatching to categorical or gaussian."""
        if prior_beliefs.ndim == 1 and observation.ndim == 1 and likelihood.ndim == 2:
            return self.update_categorical(prior_beliefs, observation, likelihood)
        elif prior_beliefs.ndim == 1 and observation.ndim == 1 and likelihood.ndim == 2:
            # Assuming gaussian for now, adjust as needed
            return self.update_gaussian(prior_beliefs, np.eye(len(prior_beliefs)), observation, likelihood, np.eye(len(observation)))['mean']
        else:
            raise ValueError("Unsupported input shapes for update_beliefs") 