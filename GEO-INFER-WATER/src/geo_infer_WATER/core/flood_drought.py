"""Flood and drought analysis module."""

import logging
from typing import Dict, Optional
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class FloodDroughtAnalyzer:
    """Analyze flood and drought risks."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize flood/drought analyzer."""
        self.config = config or {}
    
    def assess_flood_risk(
        self,
        precipitation: xr.DataArray,
        elevation: xr.DataArray,
        soil_saturation: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Assess flood risk.
        
        Args:
            precipitation: Precipitation data
            elevation: Elevation data
            soil_saturation: Optional soil saturation data
            
        Returns:
            Flood risk assessment
        """
        # Extreme precipitation
        precip_threshold = precipitation.quantile(0.95, dim='time').drop_vars('quantile')
        extreme_precip = precipitation > precip_threshold

        # Low elevation (flood-prone areas)
        elevation_threshold = elevation.quantile(0.2).drop_vars('quantile')
        low_elevation = elevation < elevation_threshold

        # Combined risk
        flood_risk = (extreme_precip.astype(float).mean(dim='time') + low_elevation.astype(float)) / 2

        if soil_saturation is not None:
            # Saturated soil increases risk
            saturated = soil_saturation > 0.8
            flood_risk = (flood_risk + saturated.astype(float)) / 2

        return xr.Dataset({
            'flood_risk': flood_risk,
            'extreme_precipitation': extreme_precip,
            'low_elevation': low_elevation
        })
    
    def assess_drought_risk(
        self,
        precipitation: xr.DataArray,
        evapotranspiration: Optional[xr.DataArray] = None,
        soil_moisture: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Assess drought risk.
        
        Args:
            precipitation: Precipitation data
            evapotranspiration: Optional ET data
            soil_moisture: Optional soil moisture data
            
        Returns:
            Drought risk assessment
        """
        # Low precipitation
        precip_threshold = precipitation.quantile(0.1, dim='time')
        low_precip = precipitation < precip_threshold
        
        # Water deficit
        if evapotranspiration is not None:
            water_deficit = evapotranspiration - precipitation
            deficit_threshold = water_deficit.quantile(0.9)
            high_deficit = water_deficit > deficit_threshold
        else:
            high_deficit = low_precip
        
        # Combined risk
        drought_risk = (low_precip.astype(int) + high_deficit.astype(int)) / 2
        
        if soil_moisture is not None:
            # Low soil moisture increases risk
            low_moisture = soil_moisture < soil_moisture.quantile(0.2)
            drought_risk = (drought_risk + low_moisture.astype(int)) / 2
        
        return xr.Dataset({
            'drought_risk': drought_risk,
            'low_precipitation': low_precip,
            'water_deficit': water_deficit if evapotranspiration is not None else None
        })

