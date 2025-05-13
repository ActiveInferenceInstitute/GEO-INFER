"""
Gaussian Process model for spatial data.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional, Union, List, Tuple, Callable
from scipy.spatial.distance import cdist
from scipy.linalg import cholesky, solve_triangular

from .base import BayesianModel


class SpatialGP(BayesianModel):
    """
    Gaussian Process model for spatial data.
    
    This class implements a Gaussian Process regression model
    for spatial interpolation and prediction.
    
    Parameters
    ----------
    kernel : str, default='matern'
        Covariance kernel: 'matern', 'rbf', 'exponential'
    lengthscale : float, default=1.0
        Length scale parameter for the kernel
    variance : float, default=1.0
        Variance parameter for the kernel
    noise : float, default=0.1
        Observation noise variance
    degree : float, default=1.5
        Degree parameter for the Matern kernel
    mean_function : callable, optional
        Mean function for the GP
    jitter : float, default=1e-6
        Small value added to the diagonal for numerical stability
    """
    
    def __init__(
        self,
        kernel: str = 'matern',
        lengthscale: float = 1.0,
        variance: float = 1.0,
        noise: float = 0.1,
        degree: float = 1.5,
        mean_function: Optional[Callable] = None,
        jitter: float = 1e-6,
        **kwargs
    ):
        super().__init__(name="SpatialGP", **kwargs)
        self.kernel_type = kernel.lower()
        self.lengthscale = lengthscale
        self.variance = variance
        self.noise = noise
        self.degree = degree
        self.mean_function = mean_function or (lambda x: np.zeros(len(x)))
        self.jitter = jitter
        self.X_train = None
        self.y_train = None
        self.L = None  # Cholesky factor of the covariance matrix
        
    def _setup_model(self, **kwargs) -> None:
        """Set up the Gaussian Process model."""
        # Define parameter distributions for inference
        self.parameters = {
            'lengthscale': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'variance': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'noise': {'prior': 'log_normal', 'hyperparams': {'mu': -2.0, 'sigma': 1.0}},
        }
        
        if self.kernel_type == 'matern':
            self.parameters['degree'] = {'prior': 'uniform', 'hyperparams': {'low': 0.5, 'high': 3.0}}
            
        # Initialize kernels based on type
        self.kernel_fn = self._get_kernel_function()
    
    def _get_kernel_function(self) -> Callable:
        """Get the appropriate kernel function based on the kernel type."""
        if self.kernel_type == 'rbf':
            return self._rbf_kernel
        elif self.kernel_type == 'matern':
            return self._matern_kernel
        elif self.kernel_type == 'exponential':
            return self._exponential_kernel
        else:
            raise ValueError(f"Unknown kernel type: {self.kernel_type}")
    
    def _rbf_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """RBF (squared exponential) kernel."""
        dist = cdist(X1, X2)
        return self.variance * np.exp(-0.5 * (dist / self.lengthscale) ** 2)
    
    def _matern_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Matern kernel with adjustable degree."""
        dist = cdist(X1, X2)
        
        if self.degree == 0.5:
            # Exponential kernel
            return self.variance * np.exp(-dist / self.lengthscale)
        elif self.degree == 1.5:
            # Matern 3/2
            scaled_dist = np.sqrt(3) * dist / self.lengthscale
            return self.variance * (1 + scaled_dist) * np.exp(-scaled_dist)
        elif self.degree == 2.5:
            # Matern 5/2
            scaled_dist = np.sqrt(5) * dist / self.lengthscale
            return self.variance * (1 + scaled_dist + scaled_dist**2/3) * np.exp(-scaled_dist)
        else:
            # For other degrees, use a simpler approximation
            scaled_dist = dist / self.lengthscale
            return self.variance * np.exp(-(scaled_dist ** self.degree))
    
    def _exponential_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Exponential kernel."""
        dist = cdist(X1, X2)
        return self.variance * np.exp(-dist / self.lengthscale)
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'SpatialGP':
        """
        Fit the GP to training data.
        
        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training input samples
        y : array-like of shape (n_samples,)
            Target values
            
        Returns
        -------
        self : object
            Returns self
        """
        self.X_train = np.asarray(X)
        self.y_train = np.asarray(y)
        
        # Compute covariance matrix
        K = self.kernel_fn(self.X_train, self.X_train)
        K += np.eye(len(self.X_train)) * (self.noise + self.jitter)
        
        # Cache Cholesky factor for predictions
        self.L = cholesky(K, lower=True)
        
        return self
    
    def predict(
        self, 
        X_new: np.ndarray, 
        posterior: Any = None, 
        samples: int = 100,
        return_std: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions at new locations.
        
        Parameters
        ----------
        X_new : array-like
            New locations to predict at
        posterior : PosteriorAnalysis, optional
            Posterior analysis object. If None, use current GP parameters.
        samples : int, default=100
            Number of posterior samples to use if posterior is provided
        return_std : bool, default=False
            Whether to return standard deviations
            
        Returns
        -------
        y_pred : ndarray
            Predicted mean
        y_std : ndarray, optional
            Predicted standard deviation
        """
        X_new = np.asarray(X_new)
        
        if posterior is not None:
            # Use posterior samples
            all_preds = []
            
            # Extract samples for relevant parameters
            for i in range(min(samples, len(posterior.samples))):
                param_sample = {
                    'lengthscale': posterior.samples['lengthscale'][i],
                    'variance': posterior.samples['variance'][i],
                    'noise': posterior.samples['noise'][i]
                }
                if self.kernel_type == 'matern':
                    param_sample['degree'] = posterior.samples['degree'][i]
                    
                # Create a GP with these parameters and predict
                temp_gp = SpatialGP(
                    kernel=self.kernel_type,
                    lengthscale=param_sample['lengthscale'],
                    variance=param_sample['variance'],
                    noise=param_sample['noise'],
                    degree=param_sample.get('degree', self.degree),
                    mean_function=self.mean_function,
                    jitter=self.jitter
                )
                
                # Fit to the same data
                temp_gp.fit(self.X_train, self.y_train)
                
                # Get prediction
                if return_std:
                    mean, _ = temp_gp._predict(X_new, return_std=True)
                else:
                    mean = temp_gp._predict(X_new, return_std=False)
                    
                all_preds.append(mean)
                
            # Compute statistics across samples
            all_preds = np.stack(all_preds)
            mean_pred = np.mean(all_preds, axis=0)
            
            if return_std:
                std_pred = np.std(all_preds, axis=0)
                return mean_pred, std_pred
            else:
                return mean_pred
        else:
            # Use current parameters
            return self._predict(X_new, return_std=return_std)
    
    def _predict(
        self, 
        X_new: np.ndarray, 
        return_std: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """Internal prediction method using current parameter values."""
        if self.X_train is None or self.y_train is None:
            raise ValueError("Model has not been fitted. Call fit() first.")
        
        # Compute prior mean
        mean = self.mean_function(X_new)
        
        # Compute cross-covariance
        K_s = self.kernel_fn(self.X_train, X_new)
        
        # Compute posterior mean
        alpha = solve_triangular(self.L, self.y_train - self.mean_function(self.X_train), lower=True)
        alpha = solve_triangular(self.L.T, alpha, lower=False)
        mean = mean + K_s.T @ alpha
        
        if return_std:
            # Compute posterior variance
            v = solve_triangular(self.L, K_s, lower=True)
            K_ss = self.kernel_fn(X_new, X_new)
            var = K_ss - v.T @ v
            var = np.clip(np.diag(var), self.jitter, np.inf)
            std = np.sqrt(var)
            return mean, std
        else:
            return mean
    
    def posterior_predictive(
        self, 
        posterior: Any,
        X: Optional[np.ndarray] = None,
        samples: int = 100
    ) -> np.ndarray:
        """
        Generate posterior predictive samples.
        
        Parameters
        ----------
        posterior : PosteriorAnalysis
            Posterior analysis object
        X : array-like, optional
            Locations to generate predictions for. If None, use observed locations.
        samples : int, default=100
            Number of posterior samples to use
            
        Returns
        -------
        ndarray of shape (samples, n_points)
            Posterior predictive samples
        """
        if X is None:
            X = self.X_train
        
        X = np.asarray(X)
        all_samples = []
        
        # For each posterior sample
        for i in range(min(samples, len(posterior.samples))):
            # Extract parameters
            param_sample = {
                'lengthscale': posterior.samples['lengthscale'][i],
                'variance': posterior.samples['variance'][i],
                'noise': posterior.samples['noise'][i]
            }
            if self.kernel_type == 'matern':
                param_sample['degree'] = posterior.samples['degree'][i]
                
            # Create a GP with these parameters
            temp_gp = SpatialGP(
                kernel=self.kernel_type,
                lengthscale=param_sample['lengthscale'],
                variance=param_sample['variance'],
                noise=param_sample['noise'],
                degree=param_sample.get('degree', self.degree),
                mean_function=self.mean_function,
                jitter=self.jitter
            )
            
            # Fit to the training data
            temp_gp.fit(self.X_train, self.y_train)
            
            # Predict mean and std
            mean, std = temp_gp._predict(X, return_std=True)
            
            # Generate random sample
            sample = np.random.normal(mean, np.sqrt(std**2 + param_sample['noise']))
            all_samples.append(sample)
            
        return np.stack(all_samples)
    
    def log_likelihood(self, theta: Dict[str, Any], data: Dict[str, np.ndarray]) -> float:
        """
        Compute the marginal log-likelihood of the GP.
        
        Parameters
        ----------
        theta : dict
            Dictionary of parameter values
        data : dict
            Dictionary with 'X' and 'y' keys
            
        Returns
        -------
        float
            Log-likelihood value
        """
        X, y = data['X'], data['y']
        
        # Set parameters from theta
        old_params = {}
        for param in ['lengthscale', 'variance', 'noise', 'degree']:
            if param in theta:
                old_params[param] = getattr(self, param)
                setattr(self, param, theta[param])
        
        # Update kernel function if needed
        if 'kernel_type' in theta:
            old_params['kernel_type'] = self.kernel_type
            self.kernel_type = theta['kernel_type']
            self.kernel_fn = self._get_kernel_function()
        
        # Compute kernel matrix
        K = self.kernel_fn(X, X)
        K += np.eye(len(X)) * (self.noise + self.jitter)
        
        # Compute log likelihood
        try:
            L = cholesky(K, lower=True)
            alpha = solve_triangular(L, y - self.mean_function(X), lower=True)
            alpha = solve_triangular(L.T, alpha, lower=False)
            
            # Marginalized log likelihood
            log_likelihood = -0.5 * np.dot(y - self.mean_function(X), alpha)
            log_likelihood -= np.sum(np.log(np.diag(L)))
            log_likelihood -= 0.5 * len(X) * np.log(2 * np.pi)
        except np.linalg.LinAlgError:
            log_likelihood = -np.inf
        
        # Restore parameters
        for param, value in old_params.items():
            setattr(self, param, value)
        if 'kernel_type' in old_params:
            self.kernel_fn = self._get_kernel_function()
            
        return log_likelihood
    
    def log_prior(self, theta: Dict[str, Any]) -> float:
        """
        Compute the log-prior for the GP parameters.
        
        Parameters
        ----------
        theta : dict
            Dictionary of parameter values
            
        Returns
        -------
        float
            Log-prior value
        """
        log_prior = 0.0
        
        # Log-normal prior for lengthscale
        if 'lengthscale' in theta:
            mu = self.parameters['lengthscale']['hyperparams']['mu']
            sigma = self.parameters['lengthscale']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['lengthscale']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['lengthscale'] * sigma * np.sqrt(2 * np.pi))
        
        # Log-normal prior for variance
        if 'variance' in theta:
            mu = self.parameters['variance']['hyperparams']['mu']
            sigma = self.parameters['variance']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['variance']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['variance'] * sigma * np.sqrt(2 * np.pi))
        
        # Log-normal prior for noise
        if 'noise' in theta:
            mu = self.parameters['noise']['hyperparams']['mu']
            sigma = self.parameters['noise']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['noise']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['noise'] * sigma * np.sqrt(2 * np.pi))
        
        # Uniform prior for degree (if Matern)
        if 'degree' in theta and self.kernel_type == 'matern':
            low = self.parameters['degree']['hyperparams']['low']
            high = self.parameters['degree']['hyperparams']['high']
            if theta['degree'] < low or theta['degree'] > high:
                log_prior = -np.inf
            else:
                log_prior += -np.log(high - low)
                
        return log_prior 