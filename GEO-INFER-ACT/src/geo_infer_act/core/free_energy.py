"""
Free energy calculation for active inference models.

This module implements variational free energy calculations for different
types of active inference models, including categorical and Gaussian models.
"""
import numpy as np
from typing import Dict, Any, Optional, Union
import logging

from geo_infer_act.utils.math import softmax

logger = logging.getLogger(__name__)


class FreeEnergyCalculator:
    """
    Calculator for variational free energy in active inference models.
    
    The free energy serves as a cost function that agents minimize through
    perception (belief updating) and action (policy selection).
    """
    
    def __init__(self):
        """Initialize the free energy calculator."""
        pass
    
    def compute_categorical_free_energy(self, 
                                       beliefs: np.ndarray,
                                       observations: np.ndarray,
                                       preferences: Optional[np.ndarray] = None) -> float:
        """
        Compute free energy for categorical models.
        
        Args:
            beliefs: Current belief distribution over states
            observations: Observed data
            preferences: Prior preferences over observations
            
        Returns:
            Free energy value
        """
        # Ensure valid probability distributions
        beliefs = beliefs + 1e-8
        beliefs = beliefs / beliefs.sum()
        
        # Entropy term (uncertainty)
        entropy = -np.sum(beliefs * np.log(beliefs))
        
        # Complexity term (KL divergence from prior)
        if preferences is not None:
            uniform_prior = np.ones_like(beliefs) / len(beliefs)
            complexity = np.sum(beliefs * np.log(beliefs / uniform_prior))
        else:
            complexity = 0.0
        
        # Accuracy term (expected log likelihood)
        # For simplicity, if shapes mismatch, project to same dimension
        if len(observations) != len(beliefs):
            if len(observations) < len(beliefs):
                obs_prob = np.pad(observations, (0, len(beliefs) - len(observations)), mode='constant')
            else:
                obs_prob = observations[:len(beliefs)]
        else:
            obs_prob = observations
        obs_prob = softmax(obs_prob)  # Ensure valid prob
        accuracy = np.sum(beliefs * np.log(obs_prob + 1e-8))
        
        # Free energy = Complexity - Accuracy
        # (We want to minimize complexity while maximizing accuracy)
        free_energy = complexity + accuracy
        
        return float(free_energy)
    
    def compute_gaussian_free_energy(self,
                                    mean: np.ndarray,
                                    precision: np.ndarray,
                                    observations: np.ndarray,
                                    prior_mean: Optional[np.ndarray] = None,
                                    prior_precision: Optional[np.ndarray] = None) -> float:
        """
        Compute free energy for Gaussian models.
        
        Args:
            mean: Current belief mean
            precision: Current belief precision matrix
            observations: Observed data
            prior_mean: Prior mean
            prior_precision: Prior precision matrix
            
        Returns:
            Free energy value
        """
        # Set defaults
        if prior_mean is None:
            prior_mean = np.zeros_like(mean)
        if prior_precision is None:
            prior_precision = np.eye(len(mean))
        
        # Complexity term (KL divergence from prior)
        try:
            complexity = 0.5 * (
                np.trace(np.linalg.solve(prior_precision, precision)) +
                (mean - prior_mean).T @ prior_precision @ (mean - prior_mean) -
                len(mean) +
                np.log(np.linalg.det(prior_precision) / np.linalg.det(precision))
            )
        except np.linalg.LinAlgError:
            # Fallback calculation
            complexity = 0.5 * np.trace(precision)
        
        # Accuracy term (negative log likelihood)
        residual = observations - mean
        accuracy = 0.5 * residual.T @ precision @ residual
        
        free_energy = complexity + accuracy
        
        return float(free_energy)
    
    def compute_expected_free_energy(self,
                                   beliefs: np.ndarray,
                                   policy: Dict[str, Any],
                                   preferences: Optional[np.ndarray] = None) -> float:
        """
        Compute expected free energy for policy evaluation.
        
        Args:
            beliefs: Current beliefs
            policy: Policy to evaluate
            preferences: Prior preferences
            
        Returns:
            Expected free energy value
        """
        # Epistemic value (information gain)
        entropy = -np.sum(beliefs * np.log(beliefs + 1e-8))
        epistemic_value = entropy
        
        # Pragmatic value (preference satisfaction)
        if preferences is not None:
            pragmatic_value = -np.sum(beliefs * np.log(preferences + 1e-8))
        else:
            pragmatic_value = 0.0
        
        # Policy-specific modulation
        exploration_bonus = policy.get('exploration_bonus', 0.1)
        risk_preference = policy.get('risk_preference', 0.0)
        
        # Expected free energy balances exploration and exploitation
        expected_free_energy = (
            pragmatic_value - 
            exploration_bonus * epistemic_value +
            risk_preference * np.var(beliefs)
        )
        
        return float(expected_free_energy) 

    def compute(self, beliefs: Union[np.ndarray, Dict], observations: np.ndarray = None, preferences: np.ndarray = None, model_type: str = 'categorical') -> float:
        """General free energy compute dispatching."""
        if model_type == 'categorical':
            if isinstance(beliefs, dict):
                beliefs = beliefs.get('states', beliefs.get('mean'))
            return self.compute_categorical_free_energy(beliefs, observations or np.ones_like(beliefs)/len(beliefs), preferences)
        elif model_type == 'gaussian':
            mean = beliefs.get('mean', beliefs)
            precision = beliefs.get('precision', np.eye(len(mean)))
            return self.compute_gaussian_free_energy(mean, precision, observations or np.zeros_like(mean), preferences.get('mean') if preferences else None, preferences.get('precision') if preferences else None)
        else:
            raise ValueError(f"Unsupported model type: {model_type}") 