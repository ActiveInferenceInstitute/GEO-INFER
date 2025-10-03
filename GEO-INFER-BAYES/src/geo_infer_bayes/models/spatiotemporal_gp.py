"""
Spatio-temporal Gaussian Process models for geospatial applications.

This module provides spatio-temporal Gaussian Process models that can handle
both spatial and temporal dependencies in geospatial data.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
import logging

from .base import BayesianModel
from .spatial_gp import SpatialGP

logger = logging.getLogger(__name__)

@dataclass
class SpatioTemporalConfig:
    """Configuration for spatio-temporal Gaussian Process models."""

    # Spatial parameters
    spatial_length_scale: float = 1.0
    spatial_variance: float = 1.0

    # Temporal parameters
    temporal_length_scale: float = 1.0
    temporal_variance: float = 1.0

    # Noise parameters
    observation_noise: float = 0.1
    process_noise: float = 0.01

    # Computational parameters
    max_iterations: int = 1000
    convergence_tolerance: float = 1e-6
    random_seed: Optional[int] = None

class SpatioTemporalGP(BayesianModel):
    """
    Spatio-temporal Gaussian Process model for geospatial applications.
    
    This model combines spatial and temporal dependencies to provide
    comprehensive modeling of spatio-temporal phenomena.
    """
    
    def __init__(self, config: Optional[SpatioTemporalConfig] = None):
        """
        Initialize the spatio-temporal Gaussian Process model.

        Args:
            config: Configuration parameters for the model
        """
        super().__init__(name="SpatioTemporalGP")
        self.config = config or SpatioTemporalConfig()

        # Initialize spatial and temporal components
        self.spatial_gp = SpatialGP()
        self.temporal_gp = None  # Will be initialized when needed

        # Model state
        self.is_fitted = False
        self.training_data = None
        self.spatial_coords = None
        self.temporal_coords = None
        self.observations = None

        # Set random seed if provided
        if self.config.random_seed is not None:
            np.random.seed(self.config.random_seed)
    
    def fit(self, 
            spatial_coords: np.ndarray,
            temporal_coords: np.ndarray,
            observations: np.ndarray,
            **kwargs) -> 'SpatioTemporalGP':
        """
        Fit the spatio-temporal Gaussian Process model to data.
        
        Args:
            spatial_coords: Array of shape (n_samples, 2) with [lat, lon] coordinates
            temporal_coords: Array of shape (n_samples,) with temporal coordinates
            observations: Array of shape (n_samples,) with observed values
            **kwargs: Additional fitting parameters
            
        Returns:
            Self for method chaining
        """
        logger.info("Fitting spatio-temporal Gaussian Process model...")
        
        # Validate inputs
        if len(spatial_coords) != len(temporal_coords) or len(spatial_coords) != len(observations):
            raise ValueError("All input arrays must have the same length")
        
        # Store training data
        self.spatial_coords = spatial_coords.copy()
        self.temporal_coords = temporal_coords.copy()
        self.observations = observations.copy()
        
        # Fit spatial component
        logger.info("Fitting spatial component...")
        self.spatial_gp.fit(spatial_coords, observations)
        
        # Fit temporal component (simplified - could be enhanced)
        logger.info("Fitting temporal component...")
        self._fit_temporal_component()
        
        self.is_fitted = True
        logger.info("Spatio-temporal GP model fitted successfully")
        
        return self
    
    def _fit_temporal_component(self):
        """Fit the temporal component of the model."""
        # Simple temporal fitting - could be enhanced with more sophisticated methods
        temporal_residuals = self.observations - self.spatial_gp.predict(self.spatial_coords)
        
        # Fit a simple temporal trend
        temporal_trend = np.polyfit(self.temporal_coords, temporal_residuals, 1)
        self.temporal_trend = temporal_trend
        
        # Calculate temporal variance
        self.temporal_variance = np.var(temporal_residuals)
    
    def predict(self, 
                spatial_coords: np.ndarray,
                temporal_coords: np.ndarray,
                return_std: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions using the fitted spatio-temporal model.
        
        Args:
            spatial_coords: Array of shape (n_samples, 2) with [lat, lon] coordinates
            temporal_coords: Array of shape (n_samples,) with temporal coordinates
            return_std: Whether to return standard deviations
            
        Returns:
            Predictions and optionally standard deviations
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Spatial predictions
        spatial_pred = self.spatial_gp.predict(spatial_coords, return_std=return_std)
        
        # Temporal predictions
        temporal_pred = self._predict_temporal(temporal_coords)
        
        # Combine predictions
        if return_std:
            spatial_mean, spatial_std = spatial_pred
            combined_mean = spatial_mean + temporal_pred
            # Simple combination of uncertainties
            combined_std = np.sqrt(spatial_std**2 + self.temporal_variance)
            return combined_mean, combined_std
        else:
            combined_pred = spatial_pred + temporal_pred
            return combined_pred
    
    def _predict_temporal(self, temporal_coords: np.ndarray) -> np.ndarray:
        """Make temporal predictions."""
        if hasattr(self, 'temporal_trend'):
            # Use fitted temporal trend
            return np.polyval(self.temporal_trend, temporal_coords)
        else:
            # Return zeros if no temporal component fitted
            return np.zeros_like(temporal_coords)
    
    def sample(self, 
               spatial_coords: np.ndarray,
               temporal_coords: np.ndarray,
               n_samples: int = 1) -> np.ndarray:
        """
        Generate samples from the spatio-temporal model.
        
        Args:
            spatial_coords: Array of shape (n_samples, 2) with [lat, lon] coordinates
            temporal_coords: Array of shape (n_samples,) with temporal coordinates
            n_samples: Number of samples to generate
            
        Returns:
            Array of shape (n_samples, n_points) with generated samples
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before sampling")
        
        # Get predictions and uncertainties
        mean_pred, std_pred = self.predict(spatial_coords, temporal_coords, return_std=True)
        
        # Generate samples
        samples = np.random.normal(mean_pred, std_pred, size=(n_samples, len(mean_pred)))
        
        return samples
    
    def get_model_parameters(self) -> Dict[str, Any]:
        """Get the fitted model parameters."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before accessing parameters")
        
        params = {
            'spatial_parameters': self.spatial_gp.get_model_parameters(),
            'temporal_variance': self.temporal_variance,
            'temporal_trend': getattr(self, 'temporal_trend', None),
            'config': self.config
        }
        
        return params
    
    def log_likelihood(self, 
                      spatial_coords: np.ndarray,
                      temporal_coords: np.ndarray,
                      observations: np.ndarray) -> float:
        """
        Calculate the log-likelihood of the data under the model.
        
        Args:
            spatial_coords: Array of shape (n_samples, 2) with [lat, lon] coordinates
            temporal_coords: Array of shape (n_samples,) with temporal coordinates
            observations: Array of shape (n_samples,) with observed values
            
        Returns:
            Log-likelihood value
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before calculating likelihood")
        
        # Get predictions
        predictions, std_pred = self.predict(spatial_coords, temporal_coords, return_std=True)
        
        # Calculate log-likelihood assuming Gaussian noise
        residuals = observations - predictions
        log_likelihood = -0.5 * np.sum(residuals**2 / std_pred**2 + np.log(2 * np.pi * std_pred**2))
        
        return log_likelihood
    
    def cross_validate(self, 
                      spatial_coords: np.ndarray,
                      temporal_coords: np.ndarray,
                      observations: np.ndarray,
                      n_folds: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation on the model.
        
        Args:
            spatial_coords: Array of shape (n_samples, 2) with [lat, lon] coordinates
            temporal_coords: Array of shape (n_samples,) with temporal coordinates
            observations: Array of shape (n_samples,) with observed values
            n_folds: Number of cross-validation folds
            
        Returns:
            Dictionary with cross-validation metrics
        """
        from sklearn.model_selection import KFold
        
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=self.config.random_seed)
        
        mse_scores = []
        mae_scores = []
        
        for train_idx, test_idx in kf.split(spatial_coords):
            # Split data
            train_spatial = spatial_coords[train_idx]
            train_temporal = temporal_coords[train_idx]
            train_obs = observations[train_idx]
            
            test_spatial = spatial_coords[test_idx]
            test_temporal = temporal_coords[test_idx]
            test_obs = observations[test_idx]
            
            # Fit model on training data
            model_copy = SpatioTemporalGP(self.config)
            model_copy.fit(train_spatial, train_temporal, train_obs)
            
            # Predict on test data
            test_pred = model_copy.predict(test_spatial, test_temporal)
            
            # Calculate metrics
            mse = np.mean((test_obs - test_pred)**2)
            mae = np.mean(np.abs(test_obs - test_pred))
            
            mse_scores.append(mse)
            mae_scores.append(mae)
        
        return {
            'mse_mean': np.mean(mse_scores),
            'mse_std': np.std(mse_scores),
            'mae_mean': np.mean(mae_scores),
            'mae_std': np.std(mae_scores)
        }

    def _setup_model(self, **kwargs) -> None:
        """Set up the spatio-temporal model structure and parameters."""
        # Define parameter distributions for inference
        self.parameters = {
            'spatial_lengthscale': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'spatial_variance': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'temporal_lengthscale': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'temporal_variance': {'prior': 'log_normal', 'hyperparams': {'mu': 0.0, 'sigma': 1.0}},
            'noise': {'prior': 'log_normal', 'hyperparams': {'mu': -2.0, 'sigma': 1.0}},
        }

    def log_likelihood(self, theta: Dict[str, Any], data: Any) -> float:
        """
        Compute the log-likelihood for the spatio-temporal model.

        Parameters
        ----------
        theta : dict
            Dictionary of parameter values
        data : dict
            Dictionary with 'spatial_coords', 'temporal_coords', and 'observations' keys

        Returns
        -------
        float
            Log-likelihood value
        """
        spatial_coords = data['spatial_coords']
        temporal_coords = data['temporal_coords']
        observations = data['observations']

        # Set parameters from theta
        for param in ['spatial_lengthscale', 'spatial_variance', 'temporal_lengthscale', 'temporal_variance', 'noise']:
            if param in theta:
                setattr(self, param, theta[param])

        # Compute predictions
        predictions = self.predict(spatial_coords, temporal_coords)

        # Compute log-likelihood assuming Gaussian noise
        residuals = observations - predictions
        log_likelihood = -0.5 * np.sum(residuals**2 / self.noise**2 + np.log(2 * np.pi * self.noise**2))

        return log_likelihood

    def log_prior(self, theta: Dict[str, Any]) -> float:
        """
        Compute the log-prior for the spatio-temporal model parameters.

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

        # Log-normal prior for spatial lengthscale
        if 'spatial_lengthscale' in theta:
            mu = self.parameters['spatial_lengthscale']['hyperparams']['mu']
            sigma = self.parameters['spatial_lengthscale']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['spatial_lengthscale']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['spatial_lengthscale'] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for spatial variance
        if 'spatial_variance' in theta:
            mu = self.parameters['spatial_variance']['hyperparams']['mu']
            sigma = self.parameters['spatial_variance']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['spatial_variance']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['spatial_variance'] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for temporal lengthscale
        if 'temporal_lengthscale' in theta:
            mu = self.parameters['temporal_lengthscale']['hyperparams']['mu']
            sigma = self.parameters['temporal_lengthscale']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['temporal_lengthscale']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['temporal_lengthscale'] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for temporal variance
        if 'temporal_variance' in theta:
            mu = self.parameters['temporal_variance']['hyperparams']['mu']
            sigma = self.parameters['temporal_variance']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['temporal_variance']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['temporal_variance'] * sigma * np.sqrt(2 * np.pi))

        # Log-normal prior for noise
        if 'noise' in theta:
            mu = self.parameters['noise']['hyperparams']['mu']
            sigma = self.parameters['noise']['hyperparams']['sigma']
            log_prior += -0.5 * ((np.log(theta['noise']) - mu) / sigma) ** 2
            log_prior -= np.log(theta['noise'] * sigma * np.sqrt(2 * np.pi))

        return log_prior

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
            New locations to predict at (should be [spatial_coords, temporal_coords])
        posterior : PosteriorAnalysis, optional
            Posterior analysis object. If None, use current parameters.
        samples : int, default=100
            Number of posterior samples to use
        return_std : bool, default=False
            Whether to return standard deviations

        Returns
        -------
        y_pred : ndarray
            Predictions
        y_std : ndarray, optional
            Standard deviations of predictions
        """
        if len(X_new.shape) == 1:
            X_new = X_new.reshape(1, -1)

        spatial_coords = X_new[:, :2]
        temporal_coords = X_new[:, 2]

        if posterior is not None:
            # Use posterior samples
            all_preds = []

            for i in range(min(samples, len(posterior.samples))):
                param_sample = {
                    'spatial_lengthscale': posterior.samples['spatial_lengthscale'][i],
                    'spatial_variance': posterior.samples['spatial_variance'][i],
                    'temporal_lengthscale': posterior.samples['temporal_lengthscale'][i],
                    'temporal_variance': posterior.samples['temporal_variance'][i],
                    'noise': posterior.samples['noise'][i]
                }

                # Create a model with these parameters and predict
                temp_model = SpatioTemporalGP(self.config)
                for param, value in param_sample.items():
                    setattr(temp_model, param, value)

                temp_model.is_fitted = True
                temp_model.spatial_coords = self.spatial_coords
                temp_model.temporal_coords = self.temporal_coords
                temp_model.observations = self.observations

                pred = temp_model.predict(spatial_coords, temporal_coords)
                all_preds.append(pred)

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
            if not self.is_fitted:
                raise ValueError("Model must be fitted before making predictions")

            # Simple prediction combining spatial and temporal components
            spatial_pred = self.spatial_gp.predict(spatial_coords)
            temporal_pred = self._predict_temporal(temporal_coords)

            prediction = spatial_pred + temporal_pred

            if return_std:
                # Simple uncertainty estimate
                std_pred = np.sqrt(self.config.observation_noise**2 + self.temporal_variance)
                return prediction, std_pred
            else:
                return prediction

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
            spatial_coords = self.spatial_coords
            temporal_coords = self.temporal_coords
        else:
            if len(X.shape) == 1:
                X = X.reshape(1, -1)
            spatial_coords = X[:, :2]
            temporal_coords = X[:, 2]

        all_samples = []

        for i in range(min(samples, len(posterior.samples))):
            param_sample = {
                'spatial_lengthscale': posterior.samples['spatial_lengthscale'][i],
                'spatial_variance': posterior.samples['spatial_variance'][i],
                'temporal_lengthscale': posterior.samples['temporal_lengthscale'][i],
                'temporal_variance': posterior.samples['temporal_variance'][i],
                'noise': posterior.samples['noise'][i]
            }

            # Create a model with these parameters
            temp_model = SpatioTemporalGP(self.config)
            for param, value in param_sample.items():
                setattr(temp_model, param, value)

            temp_model.is_fitted = True
            temp_model.spatial_coords = self.spatial_coords
            temp_model.temporal_coords = self.temporal_coords
            temp_model.observations = self.observations

            # Get predictions and add noise
            pred = temp_model.predict(spatial_coords, temporal_coords)
            noisy_sample = np.random.normal(pred, np.sqrt(param_sample['noise']))
            all_samples.append(noisy_sample)

        return np.stack(all_samples)

# Convenience function for creating spatio-temporal GP models
def create_spatiotemporal_gp(config: Optional[SpatioTemporalConfig] = None) -> SpatioTemporalGP:
    """
    Create a new spatio-temporal Gaussian Process model.

    Args:
        config: Configuration parameters for the model

    Returns:
        Configured SpatioTemporalGP instance
    """
    return SpatioTemporalGP(config) 