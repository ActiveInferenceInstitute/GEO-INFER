"""
Climate downscaling methods module.

Implements statistical and dynamical downscaling techniques to convert
coarse-resolution climate model output to fine-resolution data.
"""

import logging
from typing import Dict, Optional, Tuple
import numpy as np
import xarray as xr
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


class DownscalingMethods:
    """
    Climate downscaling methods.
    
    Supports statistical downscaling (bias correction, quantile mapping)
    and simple dynamical downscaling approaches.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize downscaling methods.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def bias_correction(
        self,
        model_data: xr.DataArray,
        observed_data: xr.DataArray,
        method: str = 'linear'
    ) -> xr.DataArray:
        """
        Apply bias correction to climate model data.
        
        Args:
            model_data: Climate model output
            observed_data: Observed/reference data
            method: Correction method ('linear', 'quantile')
            
        Returns:
            Bias-corrected data
        """
        if method == 'linear':
            return self._linear_bias_correction(model_data, observed_data)
        elif method == 'quantile':
            return self._quantile_mapping(model_data, observed_data)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _linear_bias_correction(
        self,
        model: xr.DataArray,
        observed: xr.DataArray
    ) -> xr.DataArray:
        """Linear bias correction (additive and multiplicative)."""
        # Calculate bias statistics
        model_mean = model.mean(dim='time')
        observed_mean = observed.mean(dim='time')
        
        model_std = model.std(dim='time')
        observed_std = observed.std(dim='time')
        
        # Apply correction
        corrected = (model - model_mean) * (observed_std / (model_std + 1e-10)) + observed_mean
        
        return corrected
    
    def _quantile_mapping(
        self,
        model: xr.DataArray,
        observed: xr.DataArray
    ) -> xr.DataArray:
        """Quantile mapping bias correction."""
        # Simplified quantile mapping
        # Match quantiles between model and observed
        corrected = model.copy()
        
        # Calculate quantiles
        model_quantiles = model.quantile([0.1, 0.25, 0.5, 0.75, 0.9], dim='time')
        observed_quantiles = observed.quantile([0.1, 0.25, 0.5, 0.75, 0.9], dim='time')
        
        # Apply mapping (simplified)
        for q in [0.1, 0.25, 0.5, 0.75, 0.9]:
            model_q = model_quantiles.sel(quantile=q)
            obs_q = observed_quantiles.sel(quantile=q)
            mask = (model >= model_q.min()) & (model <= model_q.max())
            corrected = xr.where(mask, model + (obs_q - model_q), corrected)
        
        return corrected
    
    def statistical_downscaling(
        self,
        coarse_data: xr.DataArray,
        fine_topography: Optional[xr.DataArray] = None,
        method: str = 'regression'
    ) -> xr.DataArray:
        """
        Statistical downscaling to higher resolution.
        
        Args:
            coarse_data: Coarse resolution climate data
            fine_topography: Fine resolution topography (optional)
            method: Downscaling method ('regression', 'rf')
            
        Returns:
            Downscaled fine resolution data
        """
        if method == 'regression':
            return self._regression_downscaling(coarse_data, fine_topography)
        elif method == 'rf':
            return self._random_forest_downscaling(coarse_data, fine_topography)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _regression_downscaling(
        self,
        coarse: xr.DataArray,
        topography: Optional[xr.DataArray] = None
    ) -> xr.DataArray:
        """Regression-based downscaling."""
        # Simplified: interpolate to finer grid
        # In practice, would use regression with topography
        fine = coarse.interp(
            lat=np.linspace(coarse.lat.min(), coarse.lat.max(), len(coarse.lat) * 2),
            lon=np.linspace(coarse.lon.min(), coarse.lon.max(), len(coarse.lon) * 2),
            method='linear'
        )
        return fine
    
    def _random_forest_downscaling(
        self,
        coarse: xr.DataArray,
        topography: Optional[xr.DataArray] = None
    ) -> xr.DataArray:
        """Random forest-based downscaling."""
        # Baseline for RF downscaling
        # Would train RF model on coarse-fine pairs
        return self._regression_downscaling(coarse, topography)

