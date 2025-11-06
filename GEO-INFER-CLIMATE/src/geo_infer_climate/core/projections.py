"""
Climate projections module.

Handles climate change projections and scenario analysis.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class ClimateProjections:
    """
    Climate change projections and scenario analysis.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize climate projections.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.scenarios = ['ssp126', 'ssp245', 'ssp370', 'ssp585']
    
    def project_future_climate(
        self,
        historical_data: xr.DataArray,
        scenario: str = 'ssp245',
        years: List[int] = None
    ) -> xr.DataArray:
        """
        Project future climate based on historical data and scenario.
        
        Args:
            historical_data: Historical climate data
            scenario: Climate scenario (ssp126, ssp245, ssp370, ssp585)
            years: List of future years to project
            
        Returns:
            Projected climate data
        """
        if scenario not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario}")
        
        years = years or [2050, 2100]
        
        # Calculate trend from historical data
        trend = self._calculate_trend(historical_data)
        
        # Apply scenario-based scaling
        scenario_factor = self._get_scenario_factor(scenario)
        
        # Project future values
        projections = []
        for year in years:
            years_ahead = year - historical_data.time.max().values.astype('datetime64[Y]').astype(int)
            projected = historical_data.mean(dim='time') + trend * years_ahead * scenario_factor
            projected = projected.expand_dims('time').assign_coords(
                time=[np.datetime64(f'{year}-01-01')]
            )
            projections.append(projected)
        
        return xr.concat(projections, dim='time')
    
    def _calculate_trend(self, data: xr.DataArray) -> xr.DataArray:
        """Calculate linear trend from time series."""
        # Simple linear trend
        time_numeric = np.arange(len(data.time))
        trend = np.polyfit(time_numeric, data.values, 1)[0]
        return xr.DataArray(trend, dims=data.dims[:-1])
    
    def _get_scenario_factor(self, scenario: str) -> float:
        """Get scenario-specific scaling factor."""
        factors = {
            'ssp126': 0.5,  # Low emissions
            'ssp245': 1.0,  # Medium emissions
            'ssp370': 1.5,  # High emissions
            'ssp585': 2.0   # Very high emissions
        }
        return factors.get(scenario, 1.0)

