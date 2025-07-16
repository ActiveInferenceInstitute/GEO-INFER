"""
Variational inference for active inference models.

This module implements variational inference algorithms for belief updating
in active inference models, including mean-field and structured approximations.
"""
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class VariationalInference:
    """
    Variational inference engine for active inference models.
    
    Implements various variational inference algorithms for efficient
    belief updating in probabilistic models.
    """
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-6):
        """
        Initialize the variational inference engine.
        
        Args:
            max_iterations: Maximum number of iterations for iterative algorithms
            tolerance: Convergence tolerance
        """
        self.max_iterations = max_iterations
        self.tolerance = tolerance
    
    def mean_field_update(self, 
                         prior: Dict[str, np.ndarray],
                         likelihood: Dict[str, np.ndarray],
                         observations: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Perform mean-field variational inference update.
        
        Args:
            prior: Prior distribution parameters
            likelihood: Likelihood function parameters
            observations: Observed data
            
        Returns:
            Updated posterior parameters
        """
        # Simplified mean-field update for categorical distributions
        if 'concentration' in prior:
            # Dirichlet-categorical conjugate update
            posterior_concentration = prior['concentration'] + observations
            
            # Normalize to get mean parameters
            posterior_mean = posterior_concentration / np.sum(posterior_concentration)
            
            return {
                'concentration': posterior_concentration,
                'mean': posterior_mean,
                'precision': 1.0 / (posterior_mean * (1 - posterior_mean) + 1e-8)
            }
        
        elif 'mean' in prior and 'precision' in prior:
            # Gaussian update
            prior_mean = prior['mean']
            prior_precision = prior['precision']
            
            # Likelihood precision (assumed known)
            obs_precision = likelihood.get('precision', np.eye(len(observations)))
            
            # Posterior parameters
            posterior_precision = prior_precision + obs_precision
            posterior_mean = np.linalg.solve(
                posterior_precision,
                prior_precision @ prior_mean + obs_precision @ observations
            )
            
            return {
                'mean': posterior_mean,
                'precision': posterior_precision,
                'covariance': np.linalg.inv(posterior_precision + 1e-6 * np.eye(posterior_precision.shape[0]))
            }
        
        else:
            # Default update
            return prior.copy()

    def mean_field_update_categorical(self, prior: np.ndarray, likelihood: np.ndarray, observations: np.ndarray) -> np.ndarray:
        return self.mean_field_update({'concentration': prior}, {'likelihood_matrix': likelihood}, observations)['mean']

    def mean_field_update_gaussian(self, mean: np.ndarray, cov: np.ndarray, obs: np.ndarray) -> np.ndarray:
        return self.mean_field_update({'mean': mean, 'precision': np.linalg.inv(cov)}, {'precision': np.eye(len(obs))*10}, obs)['mean']
    
    def structured_update(self,
                         factor_graph: Dict[str, Any],
                         observations: Dict[str, np.ndarray],
                         method: str = 'belief_propagation') -> Dict[str, np.ndarray]:
        """
        Perform structured variational inference with factor graphs.
        
        Args:
            factor_graph: Factor graph representation
            observations: Observed variables
            method: Inference method ('belief_propagation', 'mean_field')
            
        Returns:
            Updated beliefs for all variables
        """
        if method == 'belief_propagation':
            return self._belief_propagation(factor_graph, observations)
        elif method == 'mean_field':
            return self._structured_mean_field(factor_graph, observations)
        else:
            raise ValueError(f"Unknown inference method: {method}")
    
    def _belief_propagation(self,
                           factor_graph: Dict[str, Any],
                           observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Implement belief propagation algorithm.
        
        Args:
            factor_graph: Factor graph structure
            observations: Observed variables
            
        Returns:
            Marginal beliefs for all variables
        """
        # Simplified belief propagation implementation
        variables = factor_graph.get('variables', {})
        factors = factor_graph.get('factors', {})
        
        # Initialize messages
        messages = {}
        beliefs = {}
        
        # Initialize uniform beliefs
        for var_name, var_info in variables.items():
            if var_name in observations:
                # Observed variables are clamped
                beliefs[var_name] = observations[var_name]
            else:
                # Initialize with uniform distribution
                dim = var_info.get('dimension', 2)
                beliefs[var_name] = np.ones(dim) / dim
        
        # Iterative message passing
        for iteration in range(self.max_iterations):
            old_beliefs = {k: v.copy() for k, v in beliefs.items()}
            
            # Update messages and beliefs
            for var_name in variables:
                if var_name not in observations:
                    # Collect messages from neighboring factors
                    # Simplified: just normalize current belief
                    beliefs[var_name] = beliefs[var_name] / (np.sum(beliefs[var_name]) + 1e-8)
            
            # Check convergence
            converged = True
            for var_name in beliefs:
                if np.max(np.abs(beliefs[var_name] - old_beliefs[var_name])) > self.tolerance:
                    converged = False
                    break
            
            if converged:
                logger.debug(f"Belief propagation converged in {iteration + 1} iterations")
                break
        
        return beliefs
    
    def _structured_mean_field(self,
                              factor_graph: Dict[str, Any],
                              observations: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Implement structured mean-field variational inference.
        
        Args:
            factor_graph: Factor graph structure
            observations: Observed variables
            
        Returns:
            Variational posterior approximations
        """
        variables = factor_graph.get('variables', {})
        
        # Initialize variational parameters
        q_params = {}
        
        for var_name, var_info in variables.items():
            if var_name in observations:
                q_params[var_name] = observations[var_name]
            else:
                dim = var_info.get('dimension', 2)
                q_params[var_name] = np.ones(dim) / dim
        
        # Coordinate ascent updates
        for iteration in range(self.max_iterations):
            old_params = {k: v.copy() for k, v in q_params.items()}
            
            # Update each variational factor
            for var_name in variables:
                if var_name not in observations:
                    # Compute natural parameter update
                    # Simplified: just smooth towards uniform
                    uniform = np.ones_like(q_params[var_name]) / len(q_params[var_name])
                    q_params[var_name] = 0.9 * q_params[var_name] + 0.1 * uniform
                    q_params[var_name] = q_params[var_name] / (np.sum(q_params[var_name]) + 1e-8)
            
            # Check convergence
            converged = True
            for var_name in q_params:
                if np.max(np.abs(q_params[var_name] - old_params[var_name])) > self.tolerance:
                    converged = False
                    break
            
            if converged:
                logger.debug(f"Structured mean-field converged in {iteration + 1} iterations")
                break
        
        return q_params
    
    def importance_sampling_update(self,
                                  prior: Dict[str, np.ndarray],
                                  likelihood_fn: callable,
                                  observations: np.ndarray,
                                  n_samples: int = 1000) -> Dict[str, np.ndarray]:
        """
        Perform importance sampling for posterior approximation.
        
        Args:
            prior: Prior distribution parameters
            likelihood_fn: Likelihood function
            observations: Observed data
            n_samples: Number of importance samples
            
        Returns:
            Approximate posterior statistics
        """
        # Generate samples from prior
        if 'mean' in prior and 'covariance' in prior:
            # Gaussian prior
            samples = np.random.multivariate_normal(
                prior['mean'], prior['covariance'], n_samples
            )
        else:
            # Uniform prior (fallback)
            dim = len(prior.get('mean', [0, 0]))
            samples = np.random.randn(n_samples, dim)
        
        # Compute importance weights
        weights = np.array([likelihood_fn(sample, observations) for sample in samples])
        weights = weights / (np.sum(weights) + 1e-8)
        
        # Compute weighted statistics
        posterior_mean = np.sum(samples * weights[:, np.newaxis], axis=0)
        
        # Weighted covariance
        centered_samples = samples - posterior_mean
        posterior_cov = np.sum(
            weights[:, np.newaxis, np.newaxis] * 
            centered_samples[:, :, np.newaxis] * 
            centered_samples[:, np.newaxis, :], 
            axis=0
        )
        
        return {
            'mean': posterior_mean,
            'covariance': posterior_cov,
            'precision': np.linalg.inv(posterior_cov + 1e-6 * np.eye(posterior_cov.shape[0])),
            'samples': samples,
            'weights': weights
        }
    
    def compute_elbo(self,
                    posterior: Dict[str, np.ndarray],
                    prior: Dict[str, np.ndarray],
                    likelihood: Dict[str, np.ndarray],
                    observations: np.ndarray) -> float:
        """
        Compute Evidence Lower BOund (ELBO).
        
        Args:
            posterior: Posterior distribution parameters
            prior: Prior distribution parameters
            likelihood: Likelihood parameters
            observations: Observed data
            
        Returns:
            ELBO value
        """
        # Expected log likelihood term
        if 'mean' in posterior:
            # Gaussian case
            residual = observations - posterior['mean']
            precision = likelihood.get('precision', np.eye(len(observations)))
            exp_log_lik = -0.5 * residual.T @ precision @ residual
        else:
            # Categorical case (simplified)
            exp_log_lik = np.sum(posterior.get('mean', posterior.get('concentration', observations)) * np.log(observations + 1e-8))
        
        # KL divergence term
        if 'mean' in posterior and 'mean' in prior:
            # Gaussian KL divergence
            post_mean = posterior['mean']
            post_prec = posterior.get('precision', np.eye(len(post_mean)))
            prior_mean = prior['mean']
            prior_prec = prior.get('precision', np.eye(len(prior_mean)))
            
            try:
                kl_div = 0.5 * (
                    np.trace(np.linalg.solve(prior_prec, post_prec)) +
                    (post_mean - prior_mean).T @ prior_prec @ (post_mean - prior_mean) -
                    len(post_mean) +
                    np.log(np.linalg.det(prior_prec) / np.linalg.det(post_prec))
                )
            except np.linalg.LinAlgError:
                kl_div = 0.5 * np.sum((post_mean - prior_mean)**2)
        else:
            # Categorical KL divergence (simplified)
            post_probs = posterior.get('mean', np.ones(len(observations)) / len(observations))
            prior_probs = prior.get('mean', np.ones_like(post_probs) / len(post_probs))
            kl_div = np.sum(post_probs * np.log(post_probs / (prior_probs + 1e-8) + 1e-8))
        
        elbo = exp_log_lik - kl_div
        return float(elbo) 