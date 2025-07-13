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

from .base import BaseBayesianModel
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

class SpatioTemporalGP(BaseBayesianModel):
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
        super().__init__()
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