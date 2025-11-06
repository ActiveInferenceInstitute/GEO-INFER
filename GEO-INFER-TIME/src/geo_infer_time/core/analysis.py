"""
Temporal analysis for GEO-INFER-TIME.

This module provides time series analysis including trend detection,
seasonality analysis, decomposition, and statistical analysis.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

from ..models.timeseries import TimeSeries

logger = logging.getLogger(__name__)


class TemporalAnalyzer:
    """
    Temporal analyzer for time series data.

    Provides comprehensive temporal analysis including trend detection,
    seasonality analysis, decomposition, and statistical tests.
    """

    def __init__(self) -> None:
        """Initialize the temporal analyzer."""

    def detect_trend(
        self, timeseries: TimeSeries, method: str = "linear"
    ) -> Dict[str, Any]:
        """
        Detect trend in time series.

        Args:
            timeseries: TimeSeries object
            method: Trend detection method ('linear', 'polynomial', 'moving_average')

        Returns:
            Dictionary with trend information
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].values
        time_points = np.arange(len(values))

        if method == "linear":
            # Linear regression for trend
            coeffs = np.polyfit(time_points, values, 1)
            trend_line = np.polyval(coeffs, time_points)
            trend_direction = "increasing" if coeffs[0] > 0 else "decreasing"
            trend_strength = abs(coeffs[0])

        elif method == "polynomial":
            # Polynomial trend
            coeffs = np.polyfit(time_points, values, 2)
            trend_line = np.polyval(coeffs, time_points)
            trend_direction = "non-linear"
            trend_strength = np.std(trend_line) / np.std(values)

        elif method == "moving_average":
            # Moving average trend
            window = min(30, len(values) // 10)
            trend_line = pd.Series(values).rolling(window=window, center=True).mean().values
            trend_direction = "variable"
            trend_strength = np.corrcoef(values, trend_line)[0, 1]

        else:
            raise ValueError(f"Unknown trend detection method: {method}")

        return {
            "method": method,
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "trend_values": trend_line.tolist(),
        }

    def detect_seasonality(
        self, timeseries: TimeSeries, max_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Detect seasonality in time series.

        Args:
            timeseries: TimeSeries object
            max_periods: Maximum period to check for seasonality

        Returns:
            Dictionary with seasonality information
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].values

        # Use autocorrelation to detect seasonality
        autocorr = []
        for lag in range(1, min(max_periods + 1, len(values) // 2)):
            if len(values) > lag:
                corr = np.corrcoef(values[:-lag], values[lag:])[0, 1]
                autocorr.append({"lag": lag, "correlation": float(corr)})

        # Find strongest seasonal pattern
        if autocorr:
            strongest = max(autocorr, key=lambda x: abs(x["correlation"]))
            period = strongest["lag"]
            strength = abs(strongest["correlation"])
        else:
            period = None
            strength = 0.0

        return {
            "has_seasonality": strength > 0.5,
            "period": period,
            "strength": strength,
            "autocorrelations": autocorr,
        }

    def decompose(
        self,
        timeseries: TimeSeries,
        model: str = "additive",
        period: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Decompose time series into trend, seasonal, and residual components.

        Args:
            timeseries: TimeSeries object
            model: Decomposition model ('additive', 'multiplicative')
            period: Optional seasonal period (if None, auto-detect)

        Returns:
            Dictionary with decomposition components
        """
        data = timeseries.to_dataframe()
        series = data.iloc[:, 0]

        # Auto-detect period if not provided
        if period is None:
            freq = timeseries.frequency
            if freq:
                # Estimate period from frequency
                if "H" in freq:
                    period = 24  # Daily seasonality
                elif "D" in freq:
                    period = 7  # Weekly seasonality
                elif "W" in freq:
                    period = 52  # Yearly seasonality
                else:
                    period = min(12, len(series) // 2)
            else:
                period = min(12, len(series) // 2)

        try:
            decomposition = seasonal_decompose(
                series, model=model, period=period, extrapolate_trend="freq"
            )

            return {
                "trend": decomposition.trend.dropna().tolist(),
                "seasonal": decomposition.seasonal.dropna().tolist(),
                "residual": decomposition.resid.dropna().tolist(),
                "model": model,
                "period": period,
            }
        except Exception as e:
            logger.error(f"Decomposition failed: {e}")
            return {
                "trend": series.tolist(),
                "seasonal": [0.0] * len(series),
                "residual": [0.0] * len(series),
                "model": model,
                "period": period,
                "error": str(e),
            }

    def test_stationarity(self, timeseries: TimeSeries) -> Dict[str, Any]:
        """
        Test time series stationarity using Augmented Dickey-Fuller test.

        Args:
            timeseries: TimeSeries object

        Returns:
            Dictionary with stationarity test results
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values

        try:
            result = adfuller(values)

            return {
                "is_stationary": result[1] < 0.05,  # p-value < 0.05
                "adf_statistic": float(result[0]),
                "p_value": float(result[1]),
                "critical_values": {k: float(v) for k, v in result[4].items()},
            }
        except Exception as e:
            logger.error(f"Stationarity test failed: {e}")
            return {
                "is_stationary": False,
                "error": str(e),
            }


