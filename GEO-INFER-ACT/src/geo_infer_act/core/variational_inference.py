"""
Variational Inference for Active Inference Models

This module provides variational inference methods for active inference models,
implementing the free energy principle and variational message passing.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class VariationalConfig:
    """Configuration for variational inference."""
    
    # Optimization parameters
    max_iterations: int = 1000
    learning_rate: float = 0.01
    convergence_tolerance: float = 1e-6
    
    # Prior parameters
    prior_precision: float = 1.0
    prior_mean: float = 0.0
    
    # Variational family parameters
    use_gaussian: bool = True
    use_laplace: bool = False
    
    # Regularization
    regularization_strength: float = 0.01
    
    # Random seed
    random_seed: Optional[int] = None

class VariationalDistribution(ABC):
    """Abstract base class for variational distributions."""
    
    @abstractmethod
    def sample(self, n_samples: int = 1) -> np.ndarray:
        """Generate samples from the distribution."""
        pass
    
    @abstractmethod
    def log_prob(self, x: np.ndarray) -> np.ndarray:
        """Compute log probability density."""
        pass
    
    @abstractmethod
    def entropy(self) -> float:
        """Compute entropy of the distribution."""
        pass
    
    @abstractmethod
    def update_parameters(self, **kwargs):
        """Update distribution parameters."""
        pass

class GaussianVariationalDistribution(VariationalDistribution):
    """Gaussian variational distribution."""
    
    def __init__(self, mean: np.ndarray, log_std: np.ndarray):
        """
        Initialize Gaussian variational distribution.
        
        Args:
            mean: Mean vector
            log_std: Log standard deviation vector
        """
        self.mean = mean.copy()
        self.log_std = log_std.copy()
        self.std = np.exp(log_std)
    
    def sample(self, n_samples: int = 1) -> np.ndarray:
        """Generate samples using reparameterization trick."""
        eps = np.random.randn(n_samples, len(self.mean))
        return self.mean + self.std * eps
    
    def log_prob(self, x: np.ndarray) -> np.ndarray:
        """Compute log probability density."""
        log_prob = -0.5 * ((x - self.mean) / self.std)**2 - self.log_std - 0.5 * np.log(2 * np.pi)
        return log_prob
    
    def entropy(self) -> float:
        """Compute entropy of the Gaussian distribution."""
        return 0.5 * len(self.mean) * (1 + np.log(2 * np.pi)) + np.sum(self.log_std)
    
    def update_parameters(self, mean: np.ndarray, log_std: np.ndarray):
        """Update distribution parameters."""
        self.mean = mean.copy()
        self.log_std = log_std.copy()
        self.std = np.exp(log_std)

class VariationalInference:
    """
    Variational inference engine for active inference models.
    
    Implements the free energy principle and variational message passing
    for approximate Bayesian inference.
    """
    
    def __init__(self, config: Optional[VariationalConfig] = None):
        """
        Initialize variational inference engine.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or VariationalConfig()
        self.variational_dist = None
        self.prior_dist = None
        self.observations = None
        self.is_fitted = False
        
        # Set random seed
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)
    
    def fit(self, 
            observations: np.ndarray,
            prior_mean: Optional[np.ndarray] = None,
            prior_precision: Optional[float] = None,
            **kwargs) -> 'VariationalInference':
        """
        Fit the variational distribution to observations.
        
        Args:
            observations: Observed data
            prior_mean: Prior mean (if None, uses config default)
            prior_precision: Prior precision (if None, uses config default)
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        logger.info("Fitting variational distribution...")
        
        self.observations = observations.copy()
        n_observations = len(observations)
        
        # Initialize prior
        if prior_mean is None:
            prior_mean = np.full(n_observations, self.config.prior_mean)
        if prior_precision is None:
            prior_precision = self.config.prior_precision
        
        self.prior_dist = GaussianVariationalDistribution(
            mean=prior_mean,
            log_std=np.log(1.0 / np.sqrt(prior_precision)) * np.ones(n_observations)
        )
        
        # Initialize variational distribution
        initial_mean = np.mean(observations) * np.ones(n_observations)
        initial_log_std = np.log(np.std(observations)) * np.ones(n_observations)
        
        self.variational_dist = GaussianVariationalDistribution(
            mean=initial_mean,
            log_std=initial_log_std
        )
        
        # Perform variational optimization
        self._optimize_variational()
        
        self.is_fitted = True
        logger.info("Variational inference completed successfully")
        
        return self
    
    def _optimize_variational(self):
        """Optimize the variational distribution."""
        logger.info("Optimizing variational distribution...")
        
        for iteration in range(self.config.max_iterations):
            # Compute gradients
            grad_mean, grad_log_std = self._compute_gradients()
            
            # Update parameters
            self.variational_dist.mean += self.config.learning_rate * grad_mean
            self.variational_dist.log_std += self.config.learning_rate * grad_log_std
            self.variational_dist.std = np.exp(self.variational_dist.log_std)
            
            # Check convergence
            if iteration % 100 == 0:
                elbo = self._compute_elbo()
                logger.debug(f"Iteration {iteration}, ELBO: {elbo:.6f}")
                
                if iteration > 0 and abs(elbo - self._last_elbo) < self.config.convergence_tolerance:
                    logger.info(f"Converged at iteration {iteration}")
                    break
                
                self._last_elbo = elbo
    
    def _compute_gradients(self) -> Tuple[np.ndarray, np.ndarray]:
        """Compute gradients of the ELBO with respect to variational parameters."""
        # Sample from variational distribution
        samples = self.variational_dist.sample(n_samples=100)
        
        # Compute log-likelihood gradients
        log_likelihood_grads = self._compute_log_likelihood_gradients(samples)
        
        # Compute KL divergence gradients
        kl_grads = self._compute_kl_gradients()
        
        # Combine gradients
        grad_mean = log_likelihood_grads[0] - kl_grads[0]
        grad_log_std = log_likelihood_grads[1] - kl_grads[1]
        
        return grad_mean, grad_log_std
    
    def _compute_log_likelihood_gradients(self, samples: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute gradients of log-likelihood with respect to variational parameters."""
        # Simple Gaussian likelihood assumption
        n_samples = samples.shape[0]
        
        # Compute gradients for mean
        grad_mean = np.mean(samples - self.observations, axis=0)
        
        # Compute gradients for log_std
        grad_log_std = np.mean((samples - self.variational_dist.mean)**2 / self.variational_dist.std**2 - 1, axis=0)
        
        return grad_mean, grad_log_std
    
    def _compute_kl_gradients(self) -> Tuple[np.ndarray, np.ndarray]:
        """Compute gradients of KL divergence with respect to variational parameters."""
        # KL divergence between variational and prior
        kl_mean = (self.variational_dist.mean - self.prior_dist.mean) / self.prior_dist.std**2
        kl_log_std = self.variational_dist.std**2 / self.prior_dist.std**2 - 1
        
        return kl_mean, kl_log_std
    
    def _compute_elbo(self) -> float:
        """Compute the Evidence Lower BOund (ELBO)."""
        # Sample from variational distribution
        samples = self.variational_dist.sample(n_samples=1000)
        
        # Compute log-likelihood
        log_likelihood = np.mean(self._compute_log_likelihood(samples))
        
        # Compute KL divergence
        kl_divergence = self._compute_kl_divergence()
        
        # ELBO = E[log p(x|z)] - KL(q(z)||p(z))
        elbo = log_likelihood - kl_divergence
        
        return elbo
    
    def _compute_log_likelihood(self, samples: np.ndarray) -> np.ndarray:
        """Compute log-likelihood of observations given samples."""
        # Simple Gaussian likelihood
        log_likelihood = -0.5 * np.sum((samples - self.observations)**2, axis=1)
        return log_likelihood
    
    def _compute_kl_divergence(self) -> float:
        """Compute KL divergence between variational and prior distributions."""
        # KL divergence between two Gaussians
        var_mean = self.variational_dist.mean
        var_std = self.variational_dist.std
        prior_mean = self.prior_dist.mean
        prior_std = self.prior_dist.std
        
        kl = np.sum(
            np.log(prior_std / var_std) + 
            (var_std**2 + (var_mean - prior_mean)**2) / (2 * prior_std**2) - 0.5
        )
        
        return kl
    
    def predict(self, return_std: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions using the fitted variational distribution.
        
        Args:
            return_std: Whether to return standard deviations
            
        Returns:
            Predictions and optionally standard deviations
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        if return_std:
            return self.variational_dist.mean, self.variational_dist.std
        else:
            return self.variational_dist.mean
    
    def sample_posterior(self, n_samples: int = 1) -> np.ndarray:
        """
        Sample from the posterior distribution.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Array of samples from the posterior
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before sampling")
        
        return self.variational_dist.sample(n_samples)
    
    def get_variational_parameters(self) -> Dict[str, np.ndarray]:
        """Get the fitted variational parameters."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before accessing parameters")
        
        return {
            'mean': self.variational_dist.mean,
            'std': self.variational_dist.std,
            'log_std': self.variational_dist.log_std
        }
    
    def compute_free_energy(self) -> float:
        """
        Compute the free energy (negative ELBO).
        
        Returns:
            Free energy value
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before computing free energy")
        
        return -self._compute_elbo()

class FreeEnergyCalculator:
    """
    Calculator for free energy in active inference models.
    
    Implements various methods for computing and minimizing free energy
    according to the free energy principle.
    """
    
    def __init__(self, config: Optional[VariationalConfig] = None):
        """
        Initialize free energy calculator.
        
        Args:
            config: Configuration parameters
        """
        self.config = config or VariationalConfig()
        self.vi_engine = VariationalInference(config)
    
    def compute_free_energy(self, 
                           observations: np.ndarray,
                           beliefs: np.ndarray,
                           actions: Optional[np.ndarray] = None) -> float:
        """
        Compute free energy for given observations and beliefs.
        
        Args:
            observations: Observed data
            beliefs: Current beliefs about hidden states
            actions: Actions taken (optional)
            
        Returns:
            Free energy value
        """
        # Fit variational distribution
        self.vi_engine.fit(observations)
        
        # Compute free energy
        free_energy = self.vi_engine.compute_free_energy()
        
        # Add action cost if actions provided
        if actions is not None:
            action_cost = self._compute_action_cost(actions)
            free_energy += action_cost
        
        return free_energy
    
    def _compute_action_cost(self, actions: np.ndarray) -> float:
        """Compute cost of actions."""
        # Simple quadratic action cost
        return 0.5 * np.sum(actions**2)
    
    def minimize_free_energy(self, 
                           observations: np.ndarray,
                           initial_beliefs: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Minimize free energy with respect to beliefs.
        
        Args:
            observations: Observed data
            initial_beliefs: Initial beliefs about hidden states
            
        Returns:
            Optimized beliefs and final free energy
        """
        # This is a simplified implementation
        # In practice, this would involve more sophisticated optimization
        
        beliefs = initial_beliefs.copy()
        free_energy = self.compute_free_energy(observations, beliefs)
        
        # Simple gradient descent on beliefs
        for iteration in range(self.config.max_iterations):
            # Compute gradient (simplified)
            gradient = self._compute_belief_gradient(observations, beliefs)
            
            # Update beliefs
            beliefs -= self.config.learning_rate * gradient
            
            # Compute new free energy
            new_free_energy = self.compute_free_energy(observations, beliefs)
            
            # Check convergence
            if abs(new_free_energy - free_energy) < self.config.convergence_tolerance:
                break
            
            free_energy = new_free_energy
        
        return beliefs, free_energy
    
    def _compute_belief_gradient(self, observations: np.ndarray, beliefs: np.ndarray) -> np.ndarray:
        """Compute gradient of free energy with respect to beliefs."""
        # Simplified gradient computation
        return beliefs - observations

# Convenience functions
def create_variational_inference(config: Optional[VariationalConfig] = None) -> VariationalInference:
    """Create a new variational inference engine."""
    return VariationalInference(config)

def create_free_energy_calculator(config: Optional[VariationalConfig] = None) -> FreeEnergyCalculator:
    """Create a new free energy calculator."""
    return FreeEnergyCalculator(config) 