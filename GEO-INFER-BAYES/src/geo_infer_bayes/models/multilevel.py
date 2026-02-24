"""
Multi-level Bayesian models for geospatial applications.

This module provides multi-level Bayesian models that can handle
complex hierarchical spatial data structures.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
from .base import BayesianModel


class MultilevelModel(BayesianModel):
    """
    Multi-level Bayesian model for complex hierarchical structures.

    This model extends the basic hierarchical model to handle
    more complex multi-level data structures.
    """

    def __init__(self, levels: List[str] = None, **kwargs):
        """
        Initialize the multi-level model.

        Args:
            levels: List of level names in the hierarchy
            **kwargs: Additional model parameters
        """
        super().__init__(name="MultilevelModel", **kwargs)
        self.levels = levels or ['global', 'regional', 'local']
        self.level_structure = {}

    def _setup_model(self, **kwargs) -> None:
        """Set up the multi-level model structure and parameters."""
        # Define parameter distributions for inference
        self.parameters = {
            'global_mean': {'prior': 'normal', 'hyperparams': {'mu': 0.0, 'sigma': 10.0}},
            'global_variance': {'prior': 'half_normal', 'hyperparams': {'sigma': 1.0}},
            'noise': {'prior': 'half_normal', 'hyperparams': {'sigma': 1.0}},
        }

        # Add level-specific parameters
        for i, level in enumerate(self.levels[1:], 1):  # Skip global level
            self.parameters[f'{level}_variance'] = {
                'prior': 'half_normal',
                'hyperparams': {'sigma': 1.0}
            }

    def log_likelihood(self, theta: Dict[str, Any], data: Any) -> float:
        """Compute the log-likelihood for the multi-level model.

        Uses a Gaussian likelihood with global mean pooling and level-specific 
        random effects:
            y_i ~ N(mu_global + sum(level_effects), sigma^2)
        """
        observations = data.get('observations', np.array([]))
        if len(observations) == 0:
            return 0.0

        global_mean = theta.get('global_mean', 0.0)
        noise = theta.get('noise', 1.0)
        
        # Calculate expected values incorporating partial pool level effects
        predictions = np.full_like(observations, global_mean, dtype=float)
        
        # Add random effects from each level if data defines group indices
        for level in self.levels[1:]:  # skip global
            level_idx = data.get(f'{level}_indices')
            level_effects = theta.get(f'{level}_effects')
            if level_idx is not None and level_effects is not None:
                predictions += level_effects[level_idx]

        residuals = observations - predictions
        log_likelihood = -0.5 * np.sum(residuals**2 / noise**2 + np.log(2 * np.pi * noise**2))
        return float(log_likelihood)

    def log_prior(self, theta: Dict[str, Any]) -> float:
        """Compute the log-prior for the multi-level model parameters."""
        log_prior = 0.0

        # Prior for global mean
        if 'global_mean' in theta:
            mu = self.parameters['global_mean']['hyperparams']['mu']
            sigma = self.parameters['global_mean']['hyperparams']['sigma']
            log_prior += -0.5 * ((theta['global_mean'] - mu) / sigma) ** 2 - np.log(sigma * np.sqrt(2 * np.pi))

        # Prior for global variance and noise
        for param in ['global_variance', 'noise']:
            if param in theta:
                sigma = self.parameters[param]['hyperparams']['sigma']
                log_prior += -np.log(theta[param]) - sigma**2 / (2 * theta[param]**2)
                
        # Priors for level-specific variances and associated effects
        for level in self.levels[1:]:
            var_key = f'{level}_variance'
            eff_key = f'{level}_effects'
            
            if var_key in theta:
                sigma = self.parameters[var_key]['hyperparams']['sigma']
                log_prior += -np.log(theta[var_key]) - sigma**2 / (2 * theta[var_key]**2)
                
            if eff_key in theta and var_key in theta:
                # Hierarchical prior: effects ~ N(0, level_variance)
                level_var = theta[var_key]
                effects = theta[eff_key]
                log_prior += np.sum(-0.5 * (effects / level_var)**2 - np.log(level_var * np.sqrt(2 * np.pi)))

        return float(log_prior)

    def predict(
        self,
        X_new: np.ndarray,
        posterior: Any = None,
        samples: int = 100,
        return_std: bool = False,
        level_indices: Optional[Dict[str, np.ndarray]] = None
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Make predictions incorporating partial pooled level effects."""
        n_obs = len(X_new)
        
        if posterior is not None:
            n_samples = min(samples, len(posterior.samples.get('global_mean', [0])))
            predictions = np.full((n_samples, n_obs), posterior.samples.get('global_mean', [0.0])[:n_samples][:, np.newaxis])
            
            # Add level effects if requested
            if level_indices:
                for level, indices in level_indices.items():
                    eff_key = f'{level}_effects'
                    if eff_key in posterior.samples:
                        eff_samples = posterior.samples[eff_key][:n_samples]
                        # eff_samples shape: (n_samples, n_groups)
                        predictions += eff_samples[:, indices]

            mean_pred = np.mean(predictions, axis=0)
            if return_std:
                return mean_pred, np.std(predictions, axis=0)
            return mean_pred
        else:
            global_mean = getattr(self, 'global_mean', 0.0)
            predictions = np.full(n_obs, global_mean)
            
            if level_indices:
                for level, indices in level_indices.items():
                    eff = getattr(self, f'{level}_effects', None)
                    if eff is not None:
                        predictions += np.array(eff)[indices]

            if return_std:
                return predictions, np.full_like(predictions, 1.0)
            return predictions

    def posterior_predictive(
        self,
        posterior: Any,
        X: Optional[np.ndarray] = None,
        samples: int = 100
    ) -> np.ndarray:
        """Generate posterior predictive samples."""
        # Get predictions
        predictions, std = self.predict(X or np.array([]), posterior, samples=samples, return_std=True)

        # Generate samples with noise
        n_samples = min(samples, len(posterior.samples.get('noise', [1.0])))
        all_samples = []

        for i in range(n_samples):
            noise_sample = posterior.samples.get('noise', [1.0])[i]
            sample = np.random.normal(predictions, np.sqrt(noise_sample))
            all_samples.append(sample)

        return np.stack(all_samples)
