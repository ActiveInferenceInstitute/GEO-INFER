"""
Bayesian Convenience Methods

This module provides convenience methods for Bayesian inference operations,
including posterior helpers, prior builders, and MCMC wrappers.
"""

import numpy as np
from typing import Union, Optional, List, Tuple, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)


def posterior_helper(
    prior: np.ndarray,
    likelihood: Callable,
    data: np.ndarray,
    normalize: bool = True
) -> np.ndarray:
    """
    Helper for calculating posterior distribution.

    Posterior: p(θ|data) ∝ p(data|θ) * p(θ)

    Args:
        prior: Prior distribution p(θ)
        likelihood: Likelihood function p(data|θ)
        data: Observed data
        normalize: Whether to normalize posterior

    Returns:
        Posterior distribution
    """
    prior = np.asarray(prior)
    data = np.asarray(data)
    
    # Normalize prior
    prior = prior / np.sum(prior) if np.sum(prior) > 0 else prior
    
    # Calculate likelihood
    likelihood_vals = likelihood(data, prior)
    likelihood_vals = np.asarray(likelihood_vals)
    likelihood_vals = np.maximum(likelihood_vals, 1e-10)
    
    # Calculate posterior (unnormalized)
    posterior = prior * likelihood_vals
    
    # Normalize if requested
    if normalize:
        posterior = posterior / np.sum(posterior) if np.sum(posterior) > 0 else posterior
    
    return posterior


def prior_builder(
    distribution_type: str = 'uniform',
    parameters: Optional[Dict[str, Any]] = None,
    size: int = 100
) -> np.ndarray:
    """
    Build prior distribution.

    Args:
        distribution_type: Type of prior ('uniform', 'gaussian', 'beta', 'gamma')
        parameters: Distribution parameters
        size: Size of prior distribution

    Returns:
        Prior distribution
    """
    parameters = parameters or {}
    
    if distribution_type == 'uniform':
        prior = np.ones(size) / size
    
    elif distribution_type == 'gaussian':
        mean = parameters.get('mean', 0.0)
        std = parameters.get('std', 1.0)
        x = np.linspace(mean - 3 * std, mean + 3 * std, size)
        prior = np.exp(-0.5 * ((x - mean) / std) ** 2)
        prior = prior / np.sum(prior)
    
    elif distribution_type == 'beta':
        alpha = parameters.get('alpha', 1.0)
        beta = parameters.get('beta', 1.0)
        from scipy.stats import beta as beta_dist
        x = np.linspace(0, 1, size)
        prior = beta_dist.pdf(x, alpha, beta)
        prior = prior / np.sum(prior)
    
    elif distribution_type == 'gamma':
        shape = parameters.get('shape', 1.0)
        scale = parameters.get('scale', 1.0)
        from scipy.stats import gamma as gamma_dist
        x = np.linspace(0, 10, size)
        prior = gamma_dist.pdf(x, shape, scale=scale)
        prior = prior / np.sum(prior)
    
    else:
        raise ValueError(f"Unknown distribution type: {distribution_type}")
    
    return prior


def mcmc_wrapper(
    log_posterior: Callable,
    initial_state: np.ndarray,
    n_samples: int = 1000,
    n_burnin: int = 100,
    step_size: float = 0.1,
    method: str = 'metropolis'
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Wrapper for MCMC sampling.

    Args:
        log_posterior: Log posterior function
        initial_state: Initial state
        n_samples: Number of samples
        n_burnin: Number of burn-in samples
        step_size: Step size for proposals
        method: MCMC method ('metropolis', 'gibbs')

    Returns:
        Tuple of (samples, metadata)
    """
    initial_state = np.asarray(initial_state)
    n_params = len(initial_state)
    
    samples = np.zeros((n_samples, n_params))
    current_state = initial_state.copy()
    current_log_prob = log_posterior(current_state)
    
    accepted = 0
    
    for i in range(n_samples + n_burnin):
        # Propose new state
        if method == 'metropolis':
            # Metropolis-Hastings
            proposal = current_state + np.random.normal(0, step_size, n_params)
            proposal_log_prob = log_posterior(proposal)
            
            # Acceptance probability
            accept_prob = min(1.0, np.exp(proposal_log_prob - current_log_prob))
            
            if np.random.rand() < accept_prob:
                current_state = proposal
                current_log_prob = proposal_log_prob
                accepted += 1
        
        elif method == 'gibbs':
            # Gibbs sampling (simplified - updates one parameter at a time)
            param_idx = i % n_params
            proposal = current_state.copy()
            proposal[param_idx] += np.random.normal(0, step_size)
            proposal_log_prob = log_posterior(proposal)
            
            accept_prob = min(1.0, np.exp(proposal_log_prob - current_log_prob))
            
            if np.random.rand() < accept_prob:
                current_state = proposal
                current_log_prob = proposal_log_prob
                accepted += 1
        
        # Store sample (after burn-in)
        if i >= n_burnin:
            samples[i - n_burnin] = current_state
    
    acceptance_rate = accepted / (n_samples + n_burnin)
    
    metadata = {
        'n_samples': n_samples,
        'n_burnin': n_burnin,
        'acceptance_rate': acceptance_rate,
        'method': method
    }
    
    return samples, metadata


def bayesian_optimization_helper(
    objective: Callable,
    prior: np.ndarray,
    n_iterations: int = 10,
    acquisition: str = 'expected_improvement'
) -> Tuple[np.ndarray, float, Dict[str, Any]]:
    """
    Helper for Bayesian optimization.

    Args:
        objective: Objective function to optimize
        prior: Prior over parameter space
        n_iterations: Number of optimization iterations
        acquisition: Acquisition function type

    Returns:
        Tuple of (optimal_parameters, optimal_value, metadata)
    """
    # Simplified Bayesian optimization
    # Real implementation would use Gaussian processes
    
    best_params = None
    best_value = -np.inf
    
    for iteration in range(n_iterations):
        # Sample from prior
        params = np.random.choice(len(prior), p=prior)
        value = objective(params)
        
        if value > best_value:
            best_value = value
            best_params = params
        
        # Update prior (simplified - would use GP in real implementation)
        # This is a placeholder
    
    metadata = {
        'n_iterations': n_iterations,
        'acquisition': acquisition
    }
    
    return np.array([best_params]), best_value, metadata


class BayesianConvenience:
    """
    Convenience class for Bayesian inference operations.
    
    Provides high-level methods for common Bayesian tasks.
    """
    
    def __init__(self):
        """Initialize Bayesian convenience class."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._posterior_cache: Dict[str, np.ndarray] = {}
        self.logger.debug("BayesianConvenience initialized")
    
    def calculate_posterior(
        self,
        prior: np.ndarray,
        likelihood: Callable,
        data: np.ndarray,
        **kwargs
    ) -> np.ndarray:
        """
        Calculate posterior distribution.
        
        Args:
            prior: Prior distribution
            likelihood: Likelihood function
            data: Observed data
            **kwargs: Additional parameters
        
        Returns:
            Posterior distribution
        """
        return posterior_helper(prior, likelihood, data, **kwargs)
    
    def build_prior(
        self,
        distribution_type: str = 'uniform',
        **kwargs
    ) -> np.ndarray:
        """
        Build prior distribution.
        
        Args:
            distribution_type: Type of prior
            **kwargs: Distribution parameters
        
        Returns:
            Prior distribution
        """
        return prior_builder(distribution_type, kwargs)
    
    def mcmc_sample(
        self,
        log_posterior: Callable,
        initial_state: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Perform MCMC sampling.
        
        Args:
            log_posterior: Log posterior function
            initial_state: Initial state
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (samples, metadata)
        """
        return mcmc_wrapper(log_posterior, initial_state, **kwargs)
    
    def optimize(
        self,
        objective: Callable,
        prior: np.ndarray,
        **kwargs
    ) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        Perform Bayesian optimization.
        
        Args:
            objective: Objective function
            prior: Prior over parameters
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (optimal_parameters, optimal_value, metadata)
        """
        return bayesian_optimization_helper(objective, prior, **kwargs)

