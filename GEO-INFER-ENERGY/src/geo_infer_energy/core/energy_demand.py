"""Energy demand forecasting module."""

import logging
from typing import Dict, Optional
import numpy as np
import xarray as xr

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
        
        # Optional per-period temperature adjustment: use the temperature
        # series (not a single scalar) so each forecast year gets its own
        # heating/cooling adjustment. Baseline 20 degC; 1% demand shift per
        # degree of anomaly.
        if temperature is not None:
            tvals = np.asarray(temperature.values, dtype=float).flatten()
            n = len(tvals)
            if n >= forecast_years:
                edges = np.linspace(0, n, forecast_years + 1, dtype=int)
                period_means = np.array(
                    [tvals[edges[i]:edges[i + 1]].mean() for i in range(forecast_years)]
                )
            else:
                period_means = np.resize(tvals, forecast_years)

        # Population growth rate derived from the passed population data
        # (CAGR over the observed period) instead of a hard-coded assumption.
        annual_pop_growth: Optional[float] = None
        if population is not None:
            pvals = np.asarray(population.values, dtype=float).flatten()
            pvals = pvals[pvals > 0]
            if len(pvals) > 1:
                annual_pop_growth = float(
                    (pvals[-1] / pvals[0]) ** (1.0 / (len(pvals) - 1)) - 1.0
                )

        forecast_values = []
        last_value = historical_demand.isel(time=-1)
        for year in range(1, forecast_years + 1):
            forecasted = last_value + trend * year
            if temperature is not None:
                temp_factor = 1 + (period_means[year - 1] - 20) / 100
                forecasted = forecasted * temp_factor
            if annual_pop_growth is not None:
                forecasted = forecasted * ((1 + annual_pop_growth) ** year)
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

