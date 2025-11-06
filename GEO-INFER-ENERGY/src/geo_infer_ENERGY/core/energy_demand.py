"""Energy demand forecasting module."""

import logging
from typing import Dict, Optional, List
import numpy as np
import pandas as pd
import xarray as xr
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


class EnergyDemandForecaster:
    """Forecast energy demand."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize demand forecaster."""
        self.config = config or {}
    
    def forecast_demand(
        self,
        historical_demand: xr.DataArray,
        temperature: Optional[xr.DataArray] = None,
        population: Optional[xr.DataArray] = None,
        forecast_years: int = 10
    ) -> xr.Dataset:
        """
        Forecast future energy demand.
        
        Args:
            historical_demand: Historical demand data
            temperature: Optional temperature data (for heating/cooling)
            population: Optional population data
            forecast_years: Number of years to forecast
            
        Returns:
            Demand forecast
        """
        # Calculate trend
        time_numeric = np.arange(len(historical_demand.time))
        trend = np.polyfit(time_numeric, historical_demand.values.flatten(), 1)[0]
        
        # Base forecast from trend
        last_value = historical_demand.isel(time=-1)
        forecast_values = []
        
        for year in range(1, forecast_years + 1):
            forecasted = last_value + trend * year
            if temperature is not None:
                # Adjust for temperature (simplified)
                temp_factor = 1 + (temperature.mean() - 20) / 100  # 1% per degree from 20°C
                forecasted = forecasted * temp_factor
            if population is not None:
                # Adjust for population growth
                pop_growth = 1.02  # 2% annual growth assumption
                forecasted = forecasted * (pop_growth ** year)
            forecast_values.append(forecasted)
        
        return xr.Dataset({
            'demand_forecast': xr.concat(forecast_values, dim='forecast_year')
        })
    
    def identify_peak_demand(
        self,
        demand_time_series: xr.DataArray
    ) -> xr.Dataset:
        """
        Identify peak demand periods.
        
        Args:
            demand_time_series: Time series of demand
            
        Returns:
            Peak demand analysis
        """
        peak_demand = demand_time_series.max(dim='time')
        peak_time = demand_time_series.idxmax(dim='time')
        average_demand = demand_time_series.mean(dim='time')
        peak_factor = peak_demand / (average_demand + 1e-10)
        
        return xr.Dataset({
            'peak_demand': peak_demand,
            'peak_time': peak_time,
            'average_demand': average_demand,
            'peak_factor': peak_factor
        })

