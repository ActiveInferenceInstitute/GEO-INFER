"""
Temporal interpolation for GEO-INFER-TIME.

This module provides temporal interpolation and imputation methods
for filling gaps in time series data.
"""

import logging
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np

from ..models.timeseries import TimeSeries

logger = logging.getLogger(__name__)


class TemporalInterpolator:
    """
    Temporal interpolator for time series data.

    Provides various interpolation methods for filling missing values
    and resampling temporal data.
    """

    def __init__(self) -> None:
        """Initialize the temporal interpolator."""

    def interpolate(
        self,
        timeseries: TimeSeries,
        method: str = "linear",
        limit: Optional[int] = None,
    ) -> TimeSeries:
        """
        Interpolate missing values in time series.

        Args:
            timeseries: TimeSeries object
            method: Interpolation method ('linear', 'time', 'polynomial', 'spline')
            limit: Maximum number of consecutive NaNs to fill

        Returns:
            Interpolated TimeSeries
        """
        data = timeseries.to_dataframe()

        if method == "linear":
            interpolated = data.interpolate(method="linear", limit=limit)
        elif method == "time":
            interpolated = data.interpolate(method="time", limit=limit)
        elif method == "polynomial":
            interpolated = data.interpolate(method="polynomial", order=2, limit=limit)
        elif method == "spline":
            interpolated = data.interpolate(method="spline", order=2, limit=limit)
        else:
            raise ValueError(f"Unknown interpolation method: {method}")

        return TimeSeries(
            data=interpolated,
            spatial_location=timeseries.spatial_location,
            metadata={**timeseries.metadata, "interpolated": True, "method": method},
        )

    def impute(
        self,
        timeseries: TimeSeries,
        method: str = "forward_fill",
    ) -> TimeSeries:
        """
        Impute missing values using various strategies.

        Args:
            timeseries: TimeSeries object
            method: Imputation method ('forward_fill', 'backward_fill', 'mean', 'median')

        Returns:
            Imputed TimeSeries
        """
        data = timeseries.to_dataframe()

        if method == "forward_fill":
            imputed = data.fillna(method="ffill")
        elif method == "backward_fill":
            imputed = data.fillna(method="bfill")
        elif method == "mean":
            imputed = data.fillna(data.mean())
        elif method == "median":
            imputed = data.fillna(data.median())
        else:
            raise ValueError(f"Unknown imputation method: {method}")

        return TimeSeries(
            data=imputed,
            spatial_location=timeseries.spatial_location,
            metadata={**timeseries.metadata, "imputed": True, "method": method},
        )


