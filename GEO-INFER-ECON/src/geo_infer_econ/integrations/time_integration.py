"""
GEO-INFER-TIME Integration Adapter

Provides temporal analysis wrapper for economic time series.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Try to import GEO-INFER-TIME modules
try:
    from geo_infer_time.core.temporal_analyzer import TemporalAnalyzer
    from geo_infer_time.core.forecasting import ForecastingEngine
    TIME_AVAILABLE = True
except ImportError:
    TIME_AVAILABLE = False
    logger.warning(
        "GEO-INFER-TIME not available. Temporal operations will be limited. "
        "Install geo-infer-time to enable full functionality."
    )


class TimeIntegration:
    """
    Integration adapter for GEO-INFER-TIME.
    
    Provides temporal analysis for economic data including:
    - Time series analysis (trends, seasonality, decomposition)
    - Forecasting (economic indicators, growth rates)
    - Temporal alignment and synchronization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize time integration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        if not TIME_AVAILABLE:
            logger.warning("TimeIntegration initialized but GEO-INFER-TIME not available")
            self.analyzer = None
            self.forecaster = None
        else:
            try:
                self.analyzer = TemporalAnalyzer()
                self.forecaster = ForecastingEngine()
                logger.info("TimeIntegration initialized")
            except Exception as e:
                logger.error(f"Failed to initialize TimeIntegration: {e}")
                self.analyzer = None
                self.forecaster = None
    
    def detect_trend(
        self,
        time_series: pd.Series,
        method: str = 'linear'
    ) -> Optional[Dict[str, Any]]:
        """
        Detect trends in economic time series.
        
        Args:
            time_series: Time series data
            method: Trend detection method ('linear', 'polynomial', etc.)
            
        Returns:
            Dictionary with trend analysis results or None if unavailable
        """
        if not TIME_AVAILABLE or self.analyzer is None:
            # Fallback to simple linear trend
            try:
                from scipy import stats
                x = np.arange(len(time_series))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, time_series.values)
                return {
                    'slope': slope,
                    'intercept': intercept,
                    'r_squared': r_value**2,
                    'p_value': p_value,
                    'trend': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable'
                }
            except Exception as e:
                logger.error(f"Failed to detect trend: {e}")
                return None
        
        try:
            return self.analyzer.detect_trend(time_series, method=method)
        except Exception as e:
            logger.error(f"Failed to detect trend: {e}")
            return None
    
    def analyze_seasonality(
        self,
        time_series: pd.Series,
        period: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze seasonality in economic time series.
        
        Args:
            time_series: Time series data
            period: Expected seasonal period (auto-detect if None)
            
        Returns:
            Dictionary with seasonality analysis results or None if unavailable
        """
        if not TIME_AVAILABLE or self.analyzer is None:
            logger.warning("Temporal analyzer not available for seasonality analysis")
            return None
        
        try:
            return self.analyzer.analyze_seasonality(time_series, period=period)
        except Exception as e:
            logger.error(f"Failed to analyze seasonality: {e}")
            return None
    
    def decompose_time_series(
        self,
        time_series: pd.Series,
        model: str = 'additive'
    ) -> Optional[Dict[str, pd.Series]]:
        """
        Decompose time series into trend, seasonal, and residual components.
        
        Args:
            time_series: Time series data
            model: Decomposition model ('additive' or 'multiplicative')
            
        Returns:
            Dictionary with decomposed components or None if unavailable
        """
        if not TIME_AVAILABLE or self.analyzer is None:
            # Fallback to statsmodels
            try:
                from statsmodels.tsa.seasonal import seasonal_decompose
                decomposition = seasonal_decompose(
                    time_series, 
                    model=model, 
                    period=max(2, len(time_series) // 10) if len(time_series) > 10 else 2
                )
                return {
                    'trend': decomposition.trend,
                    'seasonal': decomposition.seasonal,
                    'residual': decomposition.resid
                }
            except Exception as e:
                logger.error(f"Failed to decompose time series: {e}")
                return None
        
        try:
            return self.analyzer.decompose(time_series, model=model)
        except Exception as e:
            logger.error(f"Failed to decompose time series: {e}")
            return None
    
    def forecast(
        self,
        time_series: pd.Series,
        horizon: int,
        method: str = 'arima',
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Forecast economic time series.
        
        Args:
            time_series: Historical time series data
            horizon: Forecast horizon (number of periods ahead)
            method: Forecasting method ('arima', 'exponential_smoothing', etc.)
            **kwargs: Additional parameters for forecasting
            
        Returns:
            Dictionary with forecast results or None if unavailable
        """
        if not TIME_AVAILABLE or self.forecaster is None:
            logger.warning("Forecasting engine not available")
            return None
        
        try:
            return self.forecaster.forecast(time_series, horizon=horizon, method=method, **kwargs)
        except Exception as e:
            logger.error(f"Failed to forecast: {e}")
            return None
    
    def align_time_series(
        self,
        time_series_list: List[pd.Series],
        method: str = 'interpolate'
    ) -> Optional[List[pd.Series]]:
        """
        Align multiple time series to common time index.
        
        Args:
            time_series_list: List of time series to align
            method: Alignment method ('interpolate', 'forward_fill', etc.)
            
        Returns:
            List of aligned time series or None if unavailable
        """
        if not TIME_AVAILABLE or self.analyzer is None:
            # Fallback to pandas alignment
            try:
                # Find common time index
                common_index = time_series_list[0].index
                for ts in time_series_list[1:]:
                    common_index = common_index.union(ts.index)
                
                aligned = []
                for ts in time_series_list:
                    if method == 'interpolate':
                        aligned.append(ts.reindex(common_index).interpolate())
                    elif method == 'forward_fill':
                        aligned.append(ts.reindex(common_index).ffill())
                    else:
                        aligned.append(ts.reindex(common_index))
                
                return aligned
            except Exception as e:
                logger.error(f"Failed to align time series: {e}")
                return None
        
        try:
            return self.analyzer.align_time_series(time_series_list, method=method)
        except Exception as e:
            logger.error(f"Failed to align time series: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if GEO-INFER-TIME is available."""
        return TIME_AVAILABLE and self.analyzer is not None

