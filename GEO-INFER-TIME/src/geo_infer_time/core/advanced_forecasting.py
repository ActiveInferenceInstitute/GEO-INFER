"""
Advanced forecasting methods for time series.

Includes ARIMA, exponential smoothing, and state space models.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("statsmodels not available. Advanced forecasting features will be limited.")

logger = logging.getLogger(__name__)


class AdvancedForecastingEngine:
    """
    Advanced forecasting engine with multiple methods.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize advanced forecasting engine."""
        self.config = config or {}
    
    def forecast_arima(
        self,
        time_series: pd.Series,
        order: Tuple[int, int, int] = (1, 1, 1),
        forecast_steps: int = 10,
        seasonal: Optional[Tuple[int, int, int, int]] = None
    ) -> Dict[str, Any]:
        """
        Forecast using ARIMA model.
        
        Args:
            time_series: Time series data
            order: ARIMA order (p, d, q)
            forecast_steps: Number of steps to forecast
            seasonal: Optional seasonal order (P, D, Q, s)
            
        Returns:
            Forecast results with confidence intervals
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for ARIMA forecasting")
        
        try:
            if seasonal:
                model = SARIMAX(time_series, order=order, seasonal_order=seasonal)
            else:
                model = ARIMA(time_series, order=order)
            
            fitted_model = model.fit()
            forecast = fitted_model.forecast(steps=forecast_steps)
            conf_int = fitted_model.get_forecast(steps=forecast_steps).conf_int()
            
            return {
                'forecast': forecast,
                'lower_bound': conf_int.iloc[:, 0],
                'upper_bound': conf_int.iloc[:, 1],
                'model': fitted_model
            }
        except Exception as e:
            logger.error(f"ARIMA forecasting error: {e}")
            raise
    
    def forecast_exponential_smoothing(
        self,
        time_series: pd.Series,
        trend: Optional[str] = 'add',
        seasonal: Optional[str] = None,
        forecast_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Forecast using exponential smoothing.
        
        Args:
            time_series: Time series data
            trend: Trend type ('add', 'mul', None)
            seasonal: Seasonal type ('add', 'mul', None)
            forecast_steps: Number of steps to forecast
            
        Returns:
            Forecast results
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for exponential smoothing")
        
        try:
            model = ExponentialSmoothing(
                time_series,
                trend=trend,
                seasonal=seasonal,
                seasonal_periods=12 if seasonal else None
            )
            fitted_model = model.fit()
            forecast = fitted_model.forecast(steps=forecast_steps)
            
            return {
                'forecast': forecast,
                'model': fitted_model
            }
        except Exception as e:
            logger.error(f"Exponential smoothing error: {e}")
            raise
    
    def detect_trend_seasonality(
        self,
        time_series: pd.Series
    ) -> Dict[str, Any]:
        """
        Detect trend and seasonality in time series.
        
        Args:
            time_series: Time series data
            
        Returns:
            Trend and seasonality analysis
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for trend/seasonality detection")
        
        # Decompose time series
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        decomposition = seasonal_decompose(
            time_series,
            model='additive',
            period=12 if len(time_series) > 24 else None
        )
        
        # Calculate trend strength
        trend_strength = np.var(decomposition.trend.dropna()) / np.var(time_series)
        
        # Calculate seasonality strength
        seasonal_strength = np.var(decomposition.seasonal.dropna()) / np.var(time_series)
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'trend_strength': float(trend_strength),
            'seasonal_strength': float(seasonal_strength),
            'has_trend': trend_strength > 0.1,
            'has_seasonality': seasonal_strength > 0.1
        }

