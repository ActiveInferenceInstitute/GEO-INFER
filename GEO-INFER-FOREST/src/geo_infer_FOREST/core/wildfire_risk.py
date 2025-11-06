"""Wildfire risk assessment."""

import logging
from typing import Dict, Optional
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class WildfireRiskAnalyzer:
    """Analyze wildfire risk."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize wildfire risk analyzer."""
        self.config = config or {}
    
    def assess_wildfire_risk(
        self,
        temperature: xr.DataArray,
        precipitation: xr.DataArray,
        fuel_load: Optional[xr.DataArray] = None,
        wind_speed: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Assess wildfire risk.
        
        Args:
            temperature: Temperature data
            precipitation: Precipitation data
            fuel_load: Optional fuel load data
            wind_speed: Optional wind speed data
            
        Returns:
            Wildfire risk assessment
        """
        # Calculate drought index (simplified)
        mean_precip = precipitation.mean(dim='time')
        current_precip = precipitation.isel(time=-1)
        drought_index = 1 - (current_precip / (mean_precip + 1e-10))
        drought_index = xr.where(drought_index < 0, 0, drought_index)
        drought_index = xr.where(drought_index > 1, 1, drought_index)
        
        # Temperature factor
        temp_factor = (temperature - temperature.min()) / (temperature.max() - temperature.min() + 1e-10)
        
        # Combined risk
        risk = (drought_index + temp_factor) / 2
        
        if fuel_load is not None:
            fuel_factor = fuel_load / fuel_load.max()
            risk = (risk + fuel_factor) / 2
        
        if wind_speed is not None:
            wind_factor = wind_speed / wind_speed.max()
            risk = risk * (1 + wind_factor * 0.5)  # Wind increases risk
        
        risk = xr.where(risk > 1, 1, risk)
        
        return xr.Dataset({
            'wildfire_risk': risk,
            'drought_index': drought_index,
            'temperature_factor': temp_factor
        })
    
    def predict_fire_spread(
        self,
        ignition_points: xr.DataArray,
        fuel_load: xr.DataArray,
        wind_direction: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Predict potential fire spread.
        
        Args:
            ignition_points: Fire ignition locations
            fuel_load: Fuel load data
            wind_direction: Optional wind direction
            
        Returns:
            Fire spread prediction
        """
        # Simplified fire spread model
        spread_probability = fuel_load / fuel_load.max()
        
        if wind_direction is not None:
            # Wind increases spread in wind direction
            spread_probability = spread_probability * 1.5
        
        return xr.Dataset({
            'spread_probability': spread_probability,
            'potential_spread': ignition_points * spread_probability
        })

