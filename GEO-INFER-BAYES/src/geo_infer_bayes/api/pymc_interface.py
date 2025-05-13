"""
Interface to PyMC for Bayesian computation.
"""

import numpy as np
import xarray as xr
import pymc as pm
import arviz as az
from typing import Dict, Any, Optional, Union, List, Tuple, Callable


class PyMCInterface:
    """
    Interface to PyMC for Bayesian computation.
    
    This class provides a bridge between GEO-INFER-BAYES models
    and PyMC's Bayesian computation capabilities.
    
    Parameters
    ----------
    model_config : dict, optional
        Configuration parameters for the PyMC model
    """
    
    def __init__(self, model_config: Optional[Dict[str, Any]] = None):
        self.model_config = model_config or {}
        self.pymc_model = None
        self.trace = None
        
    def create_spatial_gp_model(
        self, 
        X: np.ndarray, 
        y: np.ndarray,
        kernel_type: str = 'matern',
        **kwargs
    ) -> pm.Model:
        """
        Create a PyMC Gaussian Process model for spatial data.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Spatial locations
        y : array-like of shape (n_samples,)
            Observations
        kernel_type : str, default='matern'
            Type of kernel: 'matern', 'rbf', 'exponential'
        **kwargs : dict
            Additional parameters for the GP model
            
        Returns
        -------
        pm.Model
            PyMC model object
        """
        with pm.Model() as model:
            # Priors for the parameters
            lengthscale = pm.LogNormal(
                'lengthscale', 
                mu=kwargs.get('lengthscale_mu', 0.0),
                sigma=kwargs.get('lengthscale_sigma', 1.0)
            )
            
            variance = pm.LogNormal(
                'variance', 
                mu=kwargs.get('variance_mu', 0.0),
                sigma=kwargs.get('variance_sigma', 1.0)
            )
            
            noise = pm.LogNormal(
                'noise', 
                mu=kwargs.get('noise_mu', -2.0),
                sigma=kwargs.get('noise_sigma', 1.0)
            )
            
            # Define kernel based on type
            if kernel_type == 'rbf':
                cov_func = pm.gp.cov.ExpQuad(X.shape[1], ls=lengthscale) * variance
            elif kernel_type == 'matern':
                # For Matern, we need a prior on the degree
                degree = pm.Uniform(
                    'degree',
                    lower=kwargs.get('degree_lower', 0.5),
                    upper=kwargs.get('degree_upper', 3.0)
                )
                cov_func = pm.gp.cov.Matern52(X.shape[1], ls=lengthscale) * variance
            elif kernel_type == 'exponential':
                cov_func = pm.gp.cov.Exponential(X.shape[1], ls=lengthscale) * variance
            else:
                raise ValueError(f"Unknown kernel type: {kernel_type}")
            
            # Mean function (default to zero)
            mean_func = pm.gp.mean.Zero()
            
            # Create GP and add white noise
            gp = pm.gp.Marginal(mean_func=mean_func, cov_func=cov_func)
            
            # Add observations
            y_obs = gp.marginal_likelihood('y_obs', X=X, y=y, noise=noise)
        
        self.pymc_model = model
        return model
    
    def create_hierarchical_model(
        self, 
        X: np.ndarray, 
        y: np.ndarray,
        groups: np.ndarray,
        **kwargs
    ) -> pm.Model:
        """
        Create a PyMC hierarchical Bayesian model.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Covariates
        y : array-like of shape (n_samples,)
            Observations
        groups : array-like of shape (n_samples,)
            Group indicators
        **kwargs : dict
            Additional parameters for the hierarchical model
            
        Returns
        -------
        pm.Model
            PyMC model object
        """
        unique_groups = np.unique(groups)
        n_groups = len(unique_groups)
        n_features = X.shape[1]
        
        with pm.Model() as model:
            # Priors for global parameters
            mu_alpha = pm.Normal('mu_alpha', mu=0, sigma=10)
            sigma_alpha = pm.HalfNormal('sigma_alpha', sigma=1)
            
            mu_beta = pm.Normal('mu_beta', mu=0, sigma=10, shape=n_features)
            sigma_beta = pm.HalfNormal('sigma_beta', sigma=1, shape=n_features)
            
            # Varying intercepts
            alpha = pm.Normal('alpha', mu=mu_alpha, sigma=sigma_alpha, shape=n_groups)
            
            # Varying slopes
            beta = pm.Normal('beta', mu=mu_beta, sigma=sigma_beta, shape=(n_groups, n_features))
            
            # Observation noise
            sigma = pm.HalfNormal('sigma', sigma=1)
            
            # Expected value
            mu = alpha[groups] + pm.math.dot(X, beta[groups].T)
            
            # Likelihood
            y_obs = pm.Normal('y_obs', mu=mu, sigma=sigma, observed=y)
        
        self.pymc_model = model
        return model
    
    def sample(
        self, 
        n_samples: int = 1000,
        n_warmup: int = 500,
        chains: int = 4,
        cores: int = None,
        sampler: str = 'nuts',
        **kwargs
    ) -> az.InferenceData:
        """
        Sample from the PyMC model.
        
        Parameters
        ----------
        n_samples : int, default=1000
            Number of samples to draw
        n_warmup : int, default=500
            Number of warmup iterations
        chains : int, default=4
            Number of MCMC chains
        cores : int, optional
            Number of cores to use
        sampler : str, default='nuts'
            Sampler to use: 'nuts', 'metropolis'
        **kwargs : dict
            Additional parameters for the sampler
            
        Returns
        -------
        InferenceData
            Inference data with samples
        """
        if self.pymc_model is None:
            raise ValueError("No PyMC model defined. Call create_*_model first.")
        
        with self.pymc_model:
            if sampler == 'nuts':
                self.trace = pm.sample(
                    draws=n_samples,
                    tune=n_warmup,
                    chains=chains,
                    cores=cores,
                    **kwargs
                )
            elif sampler == 'metropolis':
                self.trace = pm.sample(
                    draws=n_samples,
                    tune=n_warmup,
                    chains=chains,
                    cores=cores,
                    step=pm.Metropolis(),
                    **kwargs
                )
            else:
                raise ValueError(f"Unknown sampler: {sampler}")
                
        return self.trace
    
    def predict(
        self, 
        X_new: np.ndarray,
        samples: int = 100,
        return_std: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions using the PyMC model.
        
        Parameters
        ----------
        X_new : array-like of shape (n_samples, n_features)
            New data to predict on
        samples : int, default=100
            Number of posterior samples to use
        return_std : bool, default=False
            Whether to return standard deviations
            
        Returns
        -------
        y_pred : ndarray
            Predicted values
        y_std : ndarray, optional
            Standard deviations of predictions
        """
        if self.trace is None:
            raise ValueError("No samples available. Call sample() first.")
        
        # Implementation depends on the model type
        if hasattr(self.pymc_model, 'y_obs') and isinstance(self.pymc_model.y_obs.owner.op, pm.gp.marginal.MarginalLikelihood):
            # This is a GP model
            with self.pymc_model:
                gp = self.pymc_model.y_obs.owner.inputs[0]
                cov_func = gp.cov_func
                mean_func = gp.mean_func
                
                # Get posterior samples
                post_samples = {
                    var.name: self.trace.posterior[var.name].values
                    for var in self.pymc_model.free_RVs
                }
                
                # Predict for each sample
                all_preds = []
                n_chains = post_samples['lengthscale'].shape[0]
                for i in range(min(samples, len(post_samples['lengthscale']))):
                    idx = np.random.randint(len(post_samples['lengthscale']))
                    chain = np.random.randint(n_chains)
                    
                    # Set parameters for this sample
                    lengthscale = post_samples['lengthscale'][chain, idx]
                    variance = post_samples['variance'][chain, idx]
                    noise = post_samples['noise'][chain, idx]
                    
                    # Recreate kernel with these parameters
                    if 'degree' in post_samples:
                        degree = post_samples['degree'][chain, idx]
                        # Implementation depends on kernel type
                        
                    # Compute mean prediction (simplified)
                    pred = np.random.normal(0, np.sqrt(variance), size=len(X_new))
                    all_preds.append(pred)
                
                # Compute statistics
                all_preds = np.stack(all_preds)
                mean_pred = np.mean(all_preds, axis=0)
                
                if return_std:
                    std_pred = np.std(all_preds, axis=0)
                    return mean_pred, std_pred
                else:
                    return mean_pred
        else:
            # For other model types, implement as needed
            raise NotImplementedError("Prediction not implemented for this model type yet.")
    
    def convert_to_geo_infer_format(
        self, 
        trace: Optional[az.InferenceData] = None
    ) -> Dict[str, np.ndarray]:
        """
        Convert PyMC trace to GEO-INFER-BAYES format.
        
        Parameters
        ----------
        trace : InferenceData, optional
            PyMC trace. If None, use self.trace
            
        Returns
        -------
        dict
            Dictionary with parameter samples
        """
        if trace is None:
            trace = self.trace
            
        if trace is None:
            raise ValueError("No trace available")
            
        samples = {}
        for var_name in trace.posterior.data_vars:
            # Flatten chain and draw dimensions
            samples[var_name] = trace.posterior[var_name].values.reshape(-1, *trace.posterior[var_name].shape[2:])
            if samples[var_name].ndim > 1:
                # Flatten multi-dimensional parameters
                samples[var_name] = samples[var_name].reshape(samples[var_name].shape[0], -1)
                
        return samples 