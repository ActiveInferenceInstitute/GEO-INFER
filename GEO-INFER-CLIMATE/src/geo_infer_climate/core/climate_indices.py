"""
Climate indices calculation module.

Implements calculation of various climate indices including:
- Standardized Precipitation Index (SPI)
- Palmer Drought Severity Index (PDSI)
- Heat indices
- Climate extremes indices
"""

import logging
from typing import Dict, List, Optional, Tuple, cast
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats

logger = logging.getLogger(__name__)


class ClimateIndicesCalculator:
    """
    Calculate climate indices from climate data.
    
    Supports SPI, PDSI, heat indices, and climate extremes.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize climate indices calculator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def calculate_spi(
        self,
        precipitation: xr.DataArray,
        timescale: int = 3,
        distribution: str = 'gamma'
    ) -> xr.DataArray:
        """
        Calculate Standardized Precipitation Index (SPI).
        
        Args:
            precipitation: Precipitation data array
            timescale: Accumulation timescale in months
            distribution: Distribution type ('gamma' or 'normal')
            
        Returns:
            SPI values as DataArray
        """
        # Accumulate precipitation over timescale
        if timescale > 1:
            precip_accum = precipitation.rolling(time=timescale, center=False).sum()
        else:
            precip_accum = precipitation
        
        # Calculate SPI using gamma distribution
        if distribution == 'gamma':
            spi = self._spi_gamma(precip_accum)
        else:
            spi = self._spi_normal(precip_accum)
        
        spi.name = f'SPI_{timescale}'
        return spi
    
    def _spi_gamma(self, precip: xr.DataArray) -> xr.DataArray:
        """Calculate SPI using gamma distribution."""
        spi = precip.copy()
        
        # Fit gamma distribution and calculate SPI
        for idx in np.ndindex(precip.shape[:-1]):  # All but time dimension
            time_series = precip.values[idx]
            valid_data = time_series[~np.isnan(time_series)]
            
            if len(valid_data) > 0:
                # Fit gamma distribution
                try:
                    alpha, loc, beta = stats.gamma.fit(valid_data, floc=0)
                    # Calculate CDF
                    cdf = stats.gamma.cdf(time_series, alpha, loc=loc, scale=beta)
                    # Convert to standard normal
                    spi.values[idx] = stats.norm.ppf(cdf)
                except Exception as e:
                    logger.warning(f"Error fitting gamma distribution: {e}")
                    spi.values[idx] = np.nan
        
        return spi
    
    def _spi_normal(self, precip: xr.DataArray) -> xr.DataArray:
        """Calculate SPI using normal distribution."""
        mean = precip.mean(dim='time')
        std = precip.std(dim='time')
        
        spi = (precip - mean) / std
        return spi
    
    def calculate_heat_index(
        self,
        temperature: xr.DataArray,
        humidity: Optional[xr.DataArray] = None
    ) -> xr.DataArray:
        """
        Calculate heat index (apparent temperature).
        
        Args:
            temperature: Temperature in Celsius
            humidity: Relative humidity (0-100) if available
            
        Returns:
            Heat index values
        """
        if humidity is not None:
            # Full heat index calculation with humidity
            hi = self._heat_index_with_humidity(temperature, humidity)
        else:
            # Simplified: just temperature
            hi = temperature.copy()
            hi.name = 'heat_index'
        
        return hi
    
    def _heat_index_with_humidity(
        self,
        temp: xr.DataArray,
        rh: xr.DataArray
    ) -> xr.DataArray:
        """Calculate heat index using temperature and humidity."""
        # Heat index formula (Rothfusz equation approximation)
        hi = temp.copy()
        
        # Convert to Fahrenheit for calculation
        temp_f = temp * 9/5 + 32
        
        # Heat index calculation
        hi_values = (
            -42.379 + 
            2.04901523 * temp_f +
            10.14333127 * rh -
            0.22475541 * temp_f * rh -
            6.83783e-3 * temp_f**2 -
            5.481717e-2 * rh**2 +
            1.22874e-3 * temp_f**2 * rh +
            8.5282e-4 * temp_f * rh**2 -
            1.99e-6 * temp_f**2 * rh**2
        )
        
        # Convert back to Celsius
        hi.values = (hi_values - 32) * 5/9
        hi.name = 'heat_index'
        
        return hi
    
    def calculate_extreme_indices(
        self,
        temperature: xr.DataArray,
        precipitation: Optional[xr.DataArray] = None
    ) -> xr.Dataset:
        """
        Calculate climate extreme indices.
        
        Args:
            temperature: Temperature data
            precipitation: Optional precipitation data
            
        Returns:
            Dataset with extreme indices
        """
        indices = {}

        # Hot days (days above 90th percentile)
        temp_90th = float(temperature.quantile(0.9, dim='time'))
        hot_days = (temperature > temp_90th).sum(dim='time')
        indices['hot_days'] = hot_days

        # Cold days (days below 10th percentile)
        temp_10th = float(temperature.quantile(0.1, dim='time'))
        cold_days = (temperature < temp_10th).sum(dim='time')
        indices['cold_days'] = cold_days

        # Maximum temperature
        indices['max_temp'] = temperature.max(dim='time')

        # Minimum temperature
        indices['min_temp'] = temperature.min(dim='time')

        if precipitation is not None:
            # Heavy precipitation days (above 95th percentile)
            precip_95th = float(precipitation.quantile(0.95, dim='time'))
            heavy_precip_days = (precipitation > precip_95th).sum(dim='time')
            indices['heavy_precip_days'] = heavy_precip_days

            # Total precipitation
            indices['total_precip'] = precipitation.sum(dim='time')

        return xr.Dataset(indices)
    
    def calculate_pdsi(
        self,
        precipitation: xr.DataArray,
        temperature: xr.DataArray,
        awc: float = 100.0  # Available water capacity (mm)
    ) -> xr.DataArray:
        """
        Calculate Palmer Drought Severity Index (PDSI).
        
        Simplified implementation of PDSI calculation.
        
        Args:
            precipitation: Monthly precipitation
            temperature: Monthly temperature
            awc: Available water capacity of soil (mm)
            
        Returns:
            PDSI values
        """
        # Simplified PDSI calculation
        # Full PDSI requires complex water balance calculations
        
        # Calculate potential evapotranspiration (Thornthwaite method)
        pet = self._calculate_pet(temperature)
        
        # Water balance
        water_balance = precipitation - pet
        
        # Accumulate water balance
        accumulated = water_balance.cumsum(dim='time')
        
        # Normalize to PDSI scale (-6 to +6)
        mean_balance = accumulated.mean(dim='time')
        std_balance = accumulated.std(dim='time')
        
        pdsi = (accumulated - mean_balance) / (std_balance + 1e-10) * 2
        pdsi = xr.where(pdsi > 6, 6, pdsi)
        pdsi = xr.where(pdsi < -6, -6, pdsi)
        
        pdsi.name = 'PDSI'
        return cast(xr.DataArray, pdsi)
    
    def _calculate_pet(self, temperature: xr.DataArray) -> xr.DataArray:
        """Calculate potential evapotranspiration using Thornthwaite method."""
        # Simplified PET calculation
        # Full method requires day length and latitude
        pet = 16 * ((10 * temperature / temperature.mean(dim='time')) ** 1.5)
        pet = xr.where(pet < 0, 0, pet)
        return cast(xr.DataArray, pet)

