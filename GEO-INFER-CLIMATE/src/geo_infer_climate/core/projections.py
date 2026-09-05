"""
Climate projections module.

Handles climate change projections and scenario analysis.
"""

import logging
from typing import Dict, List, Optional, cast
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
        years: Optional[List[int]] = None
    ) -> xr.DataArray:
        """
        Project future climate based on historical data and scenario.

        This is a simplified linear-scaling projection: the linear trend of
        the historical series is extrapolated forward and scaled by a
        scenario factor. It is NOT a climate model emulator, an ensemble
        method, or a pattern-scaling approach based on CMIP6 response
        patterns; treat results as illustrative, not predictive.

        Args:
            historical_data: Historical climate data with a ``time``
                coordinate (datetime or numeric year values)
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

        # Last year of the historical record (handles datetime or numeric
        # year coordinates)
        t_max = historical_data["time"].max().values
        if np.issubdtype(np.asarray(t_max).dtype, np.datetime64):
            last_year = int(np.asarray(t_max, dtype="datetime64[Y]").astype(int)) + 1970
        else:
            last_year = int(t_max)

        # Project future values
        projections = []
        for year in years:
            years_ahead = year - last_year
            projected = historical_data.mean(dim='time') + trend * years_ahead * scenario_factor
            projected = projected.expand_dims('time').assign_coords(
                time=[np.datetime64(f'{year}-01-01')]
            )
            projections.append(projected)

        return cast(xr.DataArray, xr.concat(projections, dim='time'))
    
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

