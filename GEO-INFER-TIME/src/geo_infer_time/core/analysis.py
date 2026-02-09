"""
Temporal analysis for GEO-INFER-TIME.

This module provides time series analysis including trend detection,
seasonality analysis, decomposition, and statistical analysis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np

from ..models.timeseries import TimeSeries

# Optional statsmodels imports
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller, acf, ccf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Types of anomalies."""
    POINT = "point"
    CONTEXTUAL = "contextual"
    COLLECTIVE = "collective"


@dataclass
class Anomaly:
    """Detected anomaly."""
    index: int
    timestamp: str
    value: float
    expected_value: float
    deviation: float
    anomaly_type: AnomalyType
    severity: str


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
            if not HAS_STATSMODELS:
                raise ImportError("statsmodels required for decomposition")
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
            if not HAS_STATSMODELS:
                raise ImportError("statsmodels required for stationarity test")
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

    def detect_anomalies(
        self,
        timeseries: TimeSeries,
        method: str = "zscore",
        threshold: float = 3.0,
        window_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies in time series.

        Args:
            timeseries: TimeSeries object
            method: Detection method ('zscore', 'iqr', 'rolling_zscore', 'isolation')
            threshold: Threshold for anomaly detection
            window_size: Window size for rolling methods

        Returns:
            Anomaly detection results
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].values
        timestamps = data.index.astype(str).tolist()

        anomalies = []

        if method == "zscore":
            mean = np.mean(values)
            std = np.std(values)
            z_scores = (values - mean) / (std + 1e-10)

            for i, (z, val) in enumerate(zip(z_scores, values)):
                if abs(z) > threshold:
                    severity = "high" if abs(z) > threshold * 1.5 else "medium"
                    anomalies.append(Anomaly(
                        index=i,
                        timestamp=timestamps[i] if i < len(timestamps) else str(i),
                        value=float(val),
                        expected_value=float(mean),
                        deviation=float(z),
                        anomaly_type=AnomalyType.POINT,
                        severity=severity
                    ))

        elif method == "iqr":
            q1, q3 = np.percentile(values, [25, 75])
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr

            for i, val in enumerate(values):
                if val < lower or val > upper:
                    deviation = (val - (q1 + q3) / 2) / (iqr + 1e-10)
                    severity = "high" if abs(deviation) > 3 else "medium"
                    anomalies.append(Anomaly(
                        index=i,
                        timestamp=timestamps[i] if i < len(timestamps) else str(i),
                        value=float(val),
                        expected_value=float((q1 + q3) / 2),
                        deviation=float(deviation),
                        anomaly_type=AnomalyType.POINT,
                        severity=severity
                    ))

        elif method == "rolling_zscore":
            window = window_size or max(10, len(values) // 20)
            series = pd.Series(values)
            rolling_mean = series.rolling(window=window, center=True).mean()
            rolling_std = series.rolling(window=window, center=True).std()

            z_scores = (series - rolling_mean) / (rolling_std + 1e-10)

            for i, (z, val) in enumerate(zip(z_scores.values, values)):
                if not np.isnan(z) and abs(z) > threshold:
                    severity = "high" if abs(z) > threshold * 1.5 else "medium"
                    anomalies.append(Anomaly(
                        index=i,
                        timestamp=timestamps[i] if i < len(timestamps) else str(i),
                        value=float(val),
                        expected_value=float(rolling_mean.iloc[i]),
                        deviation=float(z),
                        anomaly_type=AnomalyType.CONTEXTUAL,
                        severity=severity
                    ))

        return {
            "method": method,
            "threshold": threshold,
            "total_points": len(values),
            "anomalies_detected": len(anomalies),
            "anomaly_rate": len(anomalies) / len(values) * 100,
            "anomalies": [
                {
                    "index": a.index,
                    "timestamp": a.timestamp,
                    "value": a.value,
                    "expected": a.expected_value,
                    "deviation": a.deviation,
                    "type": a.anomaly_type.value,
                    "severity": a.severity
                }
                for a in anomalies
            ]
        }

    def detect_change_points(
        self,
        timeseries: TimeSeries,
        method: str = "cusum",
        min_segment_length: int = 10
    ) -> Dict[str, Any]:
        """
        Detect change points (structural breaks) in time series.

        Args:
            timeseries: TimeSeries object
            method: Detection method ('cusum', 'pelt', 'binary_segmentation')
            min_segment_length: Minimum segment length between change points

        Returns:
            Change point detection results
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].values
        n = len(values)

        change_points = []

        if method == "cusum":
            # CUSUM-based change point detection
            mean = np.mean(values)
            cumsum = np.cumsum(values - mean)

            # Find points where CUSUM changes significantly
            for i in range(min_segment_length, n - min_segment_length):
                left_mean = np.mean(values[:i])
                right_mean = np.mean(values[i:])
                diff = abs(right_mean - left_mean)

                # Threshold based on overall std
                threshold = 0.5 * np.std(values)
                if diff > threshold:
                    # Check if this is a local maximum in cumsum
                    window = min_segment_length // 2
                    local_max = max(abs(cumsum[max(0, i-window):min(n, i+window)]))
                    if abs(cumsum[i]) >= local_max * 0.9:
                        # Avoid duplicates
                        if not change_points or i - change_points[-1]['index'] >= min_segment_length:
                            change_points.append({
                                'index': i,
                                'mean_before': float(left_mean),
                                'mean_after': float(right_mean),
                                'magnitude': float(diff)
                            })

        elif method == "binary_segmentation":
            # Simplified binary segmentation
            def find_change_point(start, end):
                if end - start < 2 * min_segment_length:
                    return None

                best_cost = float('inf')
                best_idx = None
                segment = values[start:end]

                for i in range(min_segment_length, len(segment) - min_segment_length):
                    left = segment[:i]
                    right = segment[i:]
                    cost = np.var(left) * len(left) + np.var(right) * len(right)
                    if cost < best_cost:
                        best_cost = cost
                        best_idx = start + i

                if best_idx:
                    # Check if significant
                    left_mean = np.mean(values[start:best_idx])
                    right_mean = np.mean(values[best_idx:end])
                    if abs(right_mean - left_mean) > 0.3 * np.std(values):
                        return {
                            'index': best_idx,
                            'mean_before': float(left_mean),
                            'mean_after': float(right_mean),
                            'magnitude': float(abs(right_mean - left_mean))
                        }
                return None

            # Iterative binary segmentation
            segments = [(0, n)]
            while segments:
                start, end = segments.pop(0)
                cp = find_change_point(start, end)
                if cp:
                    change_points.append(cp)
                    segments.append((start, cp['index']))
                    segments.append((cp['index'], end))
                    if len(change_points) >= 10:  # Limit
                        break

        # Sort by index
        change_points.sort(key=lambda x: x['index'])

        return {
            "method": method,
            "series_length": n,
            "change_points_detected": len(change_points),
            "change_points": change_points,
            "segments": len(change_points) + 1
        }

    def calculate_cross_correlation(
        self,
        timeseries1: TimeSeries,
        timeseries2: TimeSeries,
        max_lag: int = 20
    ) -> Dict[str, Any]:
        """
        Calculate cross-correlation between two time series.

        Args:
            timeseries1: First time series
            timeseries2: Second time series
            max_lag: Maximum lag to compute

        Returns:
            Cross-correlation analysis
        """
        data1 = timeseries1.to_dataframe().iloc[:, 0].values
        data2 = timeseries2.to_dataframe().iloc[:, 0].values

        # Align lengths
        min_len = min(len(data1), len(data2))
        data1 = data1[:min_len]
        data2 = data2[:min_len]

        # Calculate cross-correlation
        correlations = []
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = np.corrcoef(data1[-lag:], data2[:lag])[0, 1]
            elif lag > 0:
                corr = np.corrcoef(data1[:-lag], data2[lag:])[0, 1]
            else:
                corr = np.corrcoef(data1, data2)[0, 1]

            if not np.isnan(corr):
                correlations.append({"lag": lag, "correlation": float(corr)})

        # Find peak correlation
        if correlations:
            peak = max(correlations, key=lambda x: abs(x["correlation"]))
        else:
            peak = {"lag": 0, "correlation": 0}

        return {
            "max_lag": max_lag,
            "series_length": min_len,
            "correlations": correlations,
            "peak_correlation": {
                "lag": peak["lag"],
                "correlation": peak["correlation"],
                "interpretation": (
                    f"Series 2 leads by {abs(peak['lag'])} periods"
                    if peak["lag"] < 0
                    else f"Series 1 leads by {peak['lag']} periods"
                    if peak["lag"] > 0
                    else "Series are synchronous"
                )
            },
            "zero_lag_correlation": float(np.corrcoef(data1, data2)[0, 1])
        }

    def validate_forecast(
        self,
        actual: List[float],
        predicted: List[float],
        confidence_intervals: Optional[List[Tuple[float, float]]] = None
    ) -> Dict[str, Any]:
        """
        Validate forecast accuracy with multiple metrics.

        Args:
            actual: Actual observed values
            predicted: Predicted values
            confidence_intervals: Optional (lower, upper) confidence bounds

        Returns:
            Forecast validation metrics
        """
        actual = np.array(actual)
        predicted = np.array(predicted)

        n = len(actual)
        errors = actual - predicted
        abs_errors = np.abs(errors)
        pct_errors = np.abs(errors / (actual + 1e-10)) * 100

        # Core metrics
        mae = float(np.mean(abs_errors))
        mse = float(np.mean(errors ** 2))
        rmse = float(np.sqrt(mse))
        mape = float(np.mean(pct_errors))

        # Symmetric MAPE
        smape = float(np.mean(2 * abs_errors / (np.abs(actual) + np.abs(predicted) + 1e-10)) * 100)

        # Directional accuracy
        if len(actual) > 1:
            actual_direction = np.sign(np.diff(actual))
            predicted_direction = np.sign(np.diff(predicted))
            directional_accuracy = float(np.mean(actual_direction == predicted_direction) * 100)
        else:
            directional_accuracy = None

        # Confidence interval coverage
        if confidence_intervals:
            coverage = sum(
                1 for a, (low, high) in zip(actual, confidence_intervals)
                if low <= a <= high
            ) / n * 100
        else:
            coverage = None

        # Theil's U statistic
        naive_errors = np.abs(np.diff(actual))
        if len(naive_errors) > 0 and np.mean(naive_errors) > 0:
            theil_u = rmse / np.sqrt(np.mean(naive_errors ** 2))
        else:
            theil_u = None

        return {
            "sample_size": n,
            "metrics": {
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "mape": mape,
                "smape": smape,
                "theil_u": theil_u,
                "directional_accuracy": directional_accuracy,
                "confidence_coverage": coverage
            },
            "interpretation": {
                "rmse_vs_std": rmse / np.std(actual) if np.std(actual) > 0 else None,
                "forecast_quality": (
                    "Excellent" if mape < 10
                    else "Good" if mape < 20
                    else "Acceptable" if mape < 30
                    else "Poor"
                )
            },
            "residuals": {
                "mean": float(np.mean(errors)),
                "std": float(np.std(errors)),
                "min": float(np.min(errors)),
                "max": float(np.max(errors))
            }
        }

    def calculate_autocorrelation(
        self,
        timeseries: TimeSeries,
        max_lag: int = 40
    ) -> Dict[str, Any]:
        """
        Calculate autocorrelation function.

        Args:
            timeseries: TimeSeries object
            max_lag: Maximum lag to compute

        Returns:
            Autocorrelation analysis
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values

        # Calculate ACF
        nlags = min(max_lag, len(values) // 2)
        if not HAS_STATSMODELS:
            # Fallback: compute ACF manually
            n = len(values)
            mean = np.mean(values)
            var = np.var(values)
            acf_values = np.array([
                np.sum((values[:n-k] - mean) * (values[k:] - mean)) / (n * var)
                if var > 0 else 0.0
                for k in range(nlags + 1)
            ])
        else:
            acf_values = acf(values, nlags=nlags, fft=True)

        # Find significant lags
        n = len(values)
        conf_bound = 1.96 / np.sqrt(n)

        significant_lags = [
            {"lag": i, "acf": float(a), "significant": abs(a) > conf_bound}
            for i, a in enumerate(acf_values)
            if i > 0
        ]

        # Detect periodicity from ACF peaks
        peaks = []
        for i in range(1, len(acf_values) - 1):
            if acf_values[i] > acf_values[i-1] and acf_values[i] > acf_values[i+1]:
                if acf_values[i] > conf_bound:
                    peaks.append({"lag": i, "acf": float(acf_values[i])})

        return {
            "max_lag": nlags,
            "confidence_bound": float(conf_bound),
            "acf_values": [float(a) for a in acf_values],
            "significant_lags": [l for l in significant_lags if l["significant"]],
            "detected_periods": peaks[:5] if peaks else [],
            "summary": {
                "first_significant_lag": next(
                    (l["lag"] for l in significant_lags if l["significant"]),
                    None
                ),
                "number_significant": sum(1 for l in significant_lags if l["significant"])
            }
        }

    def calculate_rolling_statistics(
        self,
        timeseries: TimeSeries,
        window: int = 10,
        statistics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate rolling statistics over a time series.

        Args:
            timeseries: TimeSeries object
            window: Rolling window size
            statistics: List of statistics to calculate 
                       ('mean', 'std', 'min', 'max', 'var', 'sum', 'median')
                       If None, calculates all.

        Returns:
            Dictionary with rolling statistics for each requested statistic
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0]
        
        available_stats = {
            'mean': lambda s: s.rolling(window=window).mean(),
            'std': lambda s: s.rolling(window=window).std(),
            'var': lambda s: s.rolling(window=window).var(),
            'min': lambda s: s.rolling(window=window).min(),
            'max': lambda s: s.rolling(window=window).max(),
            'sum': lambda s: s.rolling(window=window).sum(),
            'median': lambda s: s.rolling(window=window).median(),
        }
        
        if statistics is None:
            statistics = list(available_stats.keys())
        
        results = {}
        for stat_name in statistics:
            if stat_name in available_stats:
                stat_values = available_stats[stat_name](values)
                results[stat_name] = {
                    'values': stat_values.dropna().tolist(),
                    'latest': float(stat_values.iloc[-1]) if not pd.isna(stat_values.iloc[-1]) else None,
                }
            else:
                logger.warning(f"Unknown statistic: {stat_name}")
        
        # Calculate Bollinger Bands if we have mean and std
        if 'mean' in results and 'std' in results:
            mean_vals = pd.Series(values).rolling(window=window).mean()
            std_vals = pd.Series(values).rolling(window=window).std()
            results['bollinger_upper'] = {
                'values': (mean_vals + 2 * std_vals).dropna().tolist(),
            }
            results['bollinger_lower'] = {
                'values': (mean_vals - 2 * std_vals).dropna().tolist(),
            }
        
        return {
            'window': window,
            'series_length': len(values),
            'statistics': results,
            'summary': {
                'statistics_calculated': list(results.keys()),
                'valid_observations': len(values) - window + 1
            }
        }

    def detect_periodicity(
        self,
        timeseries: TimeSeries,
        max_period: int = 60
    ) -> Dict[str, Any]:
        """
        Detect periodicity in time series using FFT-based spectral analysis.

        Args:
            timeseries: TimeSeries object
            max_period: Maximum period to search for

        Returns:
            Dictionary with periodicity analysis results
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values
        n = len(values)
        
        if n < 4:
            return {
                'error': 'Time series too short for periodicity detection',
                'minimum_length': 4,
                'actual_length': n
            }
        
        # Detrend the data
        detrended = values - np.mean(values)
        
        # FFT
        fft_values = np.fft.rfft(detrended)
        power_spectrum = np.abs(fft_values) ** 2
        
        # Get frequencies
        freqs = np.fft.rfftfreq(n)
        
        # Convert to periods (exclude DC component)
        periods = []
        for i in range(1, len(freqs)):
            if freqs[i] > 0:
                period = 1 / freqs[i]
                if period <= max_period:
                    periods.append({
                        'period': float(period),
                        'power': float(power_spectrum[i]),
                        'frequency': float(freqs[i])
                    })
        
        # Sort by power
        periods.sort(key=lambda x: x['power'], reverse=True)
        top_periods = periods[:5]
        
        # Determine dominant period
        if top_periods:
            dominant = top_periods[0]
            # Calculate periodicity strength
            total_power = sum(p['power'] for p in periods)
            dominant_strength = dominant['power'] / total_power if total_power > 0 else 0
        else:
            dominant = None
            dominant_strength = 0
        
        return {
            'series_length': n,
            'max_period_searched': max_period,
            'dominant_period': {
                'period': dominant['period'] if dominant else None,
                'strength': float(dominant_strength),
                'interpretation': (
                    f"Strong periodicity at {dominant['period']:.1f} periods"
                    if dominant_strength > 0.3 and dominant
                    else "No strong periodicity detected"
                )
            },
            'top_periods': top_periods,
            'spectral_entropy': float(self._spectral_entropy(power_spectrum))
        }

    def _spectral_entropy(self, power_spectrum: np.ndarray) -> float:
        """Calculate spectral entropy from power spectrum."""
        # Normalize to probability distribution
        total = np.sum(power_spectrum)
        if total == 0:
            return 0.0
        probs = power_spectrum / total
        # Remove zeros to avoid log(0)
        probs = probs[probs > 0]
        return float(-np.sum(probs * np.log2(probs)))

    def calculate_granger_causality(
        self,
        timeseries1: TimeSeries,
        timeseries2: TimeSeries,
        max_lag: int = 5
    ) -> Dict[str, Any]:
        """
        Test for Granger causality between two time series.
        
        Tests whether timeseries1 Granger-causes timeseries2 and vice versa.

        Args:
            timeseries1: First time series
            timeseries2: Second time series
            max_lag: Maximum lag to test

        Returns:
            Dictionary with Granger causality test results
        """
        from scipy import stats
        
        data1 = timeseries1.to_dataframe().iloc[:, 0].dropna().values
        data2 = timeseries2.to_dataframe().iloc[:, 0].dropna().values
        
        # Align lengths
        min_len = min(len(data1), len(data2))
        data1 = data1[:min_len]
        data2 = data2[:min_len]
        
        results = {
            'series_length': min_len,
            'max_lag': max_lag,
            'tests': {}
        }
        
        def test_granger(y: np.ndarray, x: np.ndarray, lag: int) -> Dict[str, Any]:
            """Simple F-test for Granger causality."""
            if len(y) <= lag + 1:
                return {'error': 'Insufficient data for lag'}
            
            # Create lagged variables
            y_lagged = y[lag:]
            y_lags = np.column_stack([y[lag-i-1:-i-1] for i in range(lag)])
            x_lags = np.column_stack([x[lag-i-1:-i-1] for i in range(lag)])
            
            # Restricted model (only y lags)
            try:
                # Simple OLS
                X_r = np.column_stack([np.ones(len(y_lagged)), y_lags])
                beta_r = np.linalg.lstsq(X_r, y_lagged, rcond=None)[0]
                residuals_r = y_lagged - X_r @ beta_r
                rss_r = np.sum(residuals_r ** 2)
                
                # Unrestricted model (y and x lags)
                X_u = np.column_stack([np.ones(len(y_lagged)), y_lags, x_lags])
                beta_u = np.linalg.lstsq(X_u, y_lagged, rcond=None)[0]
                residuals_u = y_lagged - X_u @ beta_u
                rss_u = np.sum(residuals_u ** 2)
                
                # F-test
                n = len(y_lagged)
                k_r = lag + 1
                k_u = 2 * lag + 1
                
                if rss_u > 0:
                    f_stat = ((rss_r - rss_u) / lag) / (rss_u / (n - k_u))
                    p_value = 1 - stats.f.cdf(f_stat, lag, n - k_u)
                else:
                    f_stat = float('inf')
                    p_value = 0.0
                
                return {
                    'f_statistic': float(f_stat),
                    'p_value': float(p_value),
                    'significant': p_value < 0.05,
                    'lag': lag
                }
            except Exception as e:
                return {'error': str(e)}
        
        # Test if series1 Granger-causes series2
        for lag in range(1, max_lag + 1):
            key = f'series1_causes_series2_lag{lag}'
            results['tests'][key] = test_granger(data2, data1, lag)
        
        # Test if series2 Granger-causes series1
        for lag in range(1, max_lag + 1):
            key = f'series2_causes_series1_lag{lag}'
            results['tests'][key] = test_granger(data1, data2, lag)
        
        # Summarize
        s1_causes_s2 = any(
            v.get('significant', False) 
            for k, v in results['tests'].items() 
            if 'series1_causes_series2' in k
        )
        s2_causes_s1 = any(
            v.get('significant', False) 
            for k, v in results['tests'].items() 
            if 'series2_causes_series1' in k
        )
        
        results['summary'] = {
            'series1_granger_causes_series2': s1_causes_s2,
            'series2_granger_causes_series1': s2_causes_s1,
            'bidirectional_causality': s1_causes_s2 and s2_causes_s1,
            'interpretation': (
                "Bidirectional causality detected" if s1_causes_s2 and s2_causes_s1
                else "Series 1 Granger-causes Series 2" if s1_causes_s2
                else "Series 2 Granger-causes Series 1" if s2_causes_s1
                else "No significant Granger causality detected"
            )
        }
        
        return results

    def compute_temporal_entropy(
        self,
        timeseries: TimeSeries,
        bins: int = 10,
        method: str = "shannon"
    ) -> Dict[str, Any]:
        """
        Compute entropy measures for a time series.

        Args:
            timeseries: TimeSeries object
            bins: Number of bins for histogram-based entropy
            method: Entropy method ('shannon', 'sample', 'approximate')

        Returns:
            Dictionary with entropy measures
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values
        n = len(values)
        
        results = {
            'series_length': n,
            'method': method,
        }
        
        # Shannon entropy (histogram-based)
        hist, _ = np.histogram(values, bins=bins, density=True)
        hist = hist[hist > 0]  # Remove zeros
        if len(hist) > 0:
            # Normalize to probabilities
            probs = hist / np.sum(hist)
            shannon_entropy = -np.sum(probs * np.log2(probs))
        else:
            shannon_entropy = 0.0
        
        results['shannon_entropy'] = {
            'value': float(shannon_entropy),
            'bins': bins,
            'normalized': float(shannon_entropy / np.log2(bins)) if bins > 1 else 0.0
        }
        
        # Sample entropy (approximation)
        if method in ('sample', 'approximate') and n > 10:
            m = 2  # Embedding dimension
            r = 0.2 * np.std(values)  # Tolerance
            
            def count_matches(template_length):
                count = 0
                templates = []
                for i in range(n - template_length):
                    templates.append(values[i:i + template_length])
                
                for i, t1 in enumerate(templates):
                    for t2 in templates[i+1:]:
                        if np.max(np.abs(t1 - t2)) < r:
                            count += 1
                return count
            
            try:
                b_m = count_matches(m)
                a_m = count_matches(m + 1)
                
                if b_m > 0 and a_m > 0:
                    sample_entropy = -np.log(a_m / b_m)
                else:
                    sample_entropy = None
                    
                results['sample_entropy'] = {
                    'value': float(sample_entropy) if sample_entropy else None,
                    'embedding_dim': m,
                    'tolerance': float(r)
                }
            except Exception as e:
                results['sample_entropy'] = {'error': str(e)}
        
        # Approximate entropy
        if method == 'approximate' and n > 10:
            # Use sample entropy result for approximation
            if 'sample_entropy' in results and results['sample_entropy'].get('value'):
                results['approximate_entropy'] = {
                    'value': results['sample_entropy']['value'],
                    'note': 'Approximated using sample entropy'
                }
        
        # Interpretation
        norm_entropy = results['shannon_entropy']['normalized']
        results['interpretation'] = {
            'complexity': (
                'High' if norm_entropy > 0.8
                else 'Medium' if norm_entropy > 0.5
                else 'Low'
            ),
            'predictability': (
                'Low' if norm_entropy > 0.8
                else 'Medium' if norm_entropy > 0.5
                else 'High'
            ),
            'description': (
                'Series appears random/complex' if norm_entropy > 0.8
                else 'Series has moderate regularity' if norm_entropy > 0.5
                else 'Series has high regularity/predictability'
            )
        }
        
        return results

