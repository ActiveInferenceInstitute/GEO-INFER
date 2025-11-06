"""
Extreme weather event analysis module.
"""

import logging
from typing import Dict, List, Optional
import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


class ExtremeEventAnalyzer:
    """
    Analyze extreme weather events.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize extreme event analyzer.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
    
    def detect_heatwaves(
        self,
        temperature: xr.DataArray,
        threshold_percentile: float = 90.0,
        min_duration: int = 3
    ) -> xr.Dataset:
        """
        Detect heatwave events.
        
        Args:
            temperature: Temperature data
            threshold_percentile: Percentile threshold for heatwave
            min_duration: Minimum duration in days
            
        Returns:
            Dataset with heatwave events
        """
        threshold = temperature.quantile(threshold_percentile / 100.0, dim='time')
        
        # Identify days above threshold
        above_threshold = temperature > threshold
        
        # Find consecutive periods
        heatwaves = self._find_consecutive_periods(above_threshold, min_duration)
        
        return heatwaves
    
    def detect_droughts(
        self,
        precipitation: xr.DataArray,
        threshold_percentile: float = 10.0,
        min_duration: int = 30
    ) -> xr.Dataset:
        """
        Detect drought events.
        
        Args:
            precipitation: Precipitation data
            threshold_percentile: Percentile threshold for drought
            min_duration: Minimum duration in days
            
        Returns:
            Dataset with drought events
        """
        threshold = precipitation.quantile(threshold_percentile / 100.0, dim='time')
        
        # Identify days below threshold
        below_threshold = precipitation < threshold
        
        # Find consecutive periods
        droughts = self._find_consecutive_periods(below_threshold, min_duration)
        
        return droughts
    
    def _find_consecutive_periods(
        self,
        condition: xr.DataArray,
        min_duration: int
    ) -> xr.Dataset:
        """Find consecutive periods meeting condition."""
        # Simplified: count consecutive True values
        events = condition.astype(int).groupby('time').sum()
        events = events.where(events >= min_duration, 0)
        
        return xr.Dataset({'events': events})

