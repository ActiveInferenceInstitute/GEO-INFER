"""
Event detection for GEO-INFER-TIME.

This module provides event detection capabilities for identifying
anomalies, changepoints, and significant events in time series data.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from ..models.timeseries import TimeSeries

logger = logging.getLogger(__name__)


class EventDetector:
    """
    Event detector for time series data.

    Provides methods for detecting anomalies, changepoints, and
    significant events in temporal data.
    """

    def __init__(
        self,
        threshold_multiplier: float = 3.0,
        window_size: int = 10,
    ) -> None:
        """
        Initialize the event detector.

        Args:
            threshold_multiplier: Multiplier for standard deviation threshold
            window_size: Window size for moving statistics
        """
        self.threshold_multiplier = threshold_multiplier
        self.window_size = window_size

    def detect_anomalies(
        self, timeseries: TimeSeries, method: str = "z_score"
    ) -> Dict[str, Any]:
        """
        Detect anomalies in time series.

        Args:
            timeseries: TimeSeries object
            method: Detection method ('z_score', 'iqr', 'isolation_forest')

        Returns:
            Dictionary with detected anomalies
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values
        timestamps = data.index[~data.iloc[:, 0].isna()]

        anomalies = []

        if method == "z_score":
            mean = np.mean(values)
            std = np.std(values)
            threshold = self.threshold_multiplier * std

            for i, (val, ts) in enumerate(zip(values, timestamps)):
                z_score = abs(val - mean) / std if std > 0 else 0
                if z_score > self.threshold_multiplier:
                    anomalies.append(
                        {
                            "timestamp": ts.isoformat(),
                            "value": float(val),
                            "z_score": float(z_score),
                            "type": "outlier",
                        }
                    )

        elif method == "iqr":
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - self.threshold_multiplier * iqr
            upper_bound = q3 + self.threshold_multiplier * iqr

            for val, ts in zip(values, timestamps):
                if val < lower_bound or val > upper_bound:
                    anomalies.append(
                        {
                            "timestamp": ts.isoformat(),
                            "value": float(val),
                            "type": "outlier",
                        }
                    )

        else:
            raise ValueError(f"Unknown anomaly detection method: {method}")

        return {
            "method": method,
            "anomalies": anomalies,
            "count": len(anomalies),
        }

    def detect_changepoints(
        self, timeseries: TimeSeries, sensitivity: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect changepoints in time series.

        Args:
            timeseries: TimeSeries object
            sensitivity: Sensitivity parameter (0.0 to 1.0)

        Returns:
            Dictionary with detected changepoints
        """
        data = timeseries.to_dataframe()
        values = data.iloc[:, 0].dropna().values
        timestamps = data.index[~data.iloc[:, 0].isna()]

        changepoints = []

        # Simple changepoint detection using moving window statistics
        for i in range(self.window_size, len(values) - self.window_size):
            window_before = values[i - self.window_size : i]
            window_after = values[i : i + self.window_size]

            mean_before = np.mean(window_before)
            mean_after = np.mean(window_after)
            std_before = np.std(window_before)
            std_after = np.std(window_after)

            # Detect significant change in mean
            mean_change = abs(mean_after - mean_before)
            threshold = sensitivity * (std_before + std_after) / 2

            if mean_change > threshold:
                changepoints.append(
                    {
                        "timestamp": timestamps[i].isoformat(),
                        "index": i,
                        "mean_change": float(mean_change),
                        "mean_before": float(mean_before),
                        "mean_after": float(mean_after),
                    }
                )

        return {
            "changepoints": changepoints,
            "count": len(changepoints),
        }



