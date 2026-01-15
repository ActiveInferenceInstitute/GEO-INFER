"""
TimeSeries data model for GEO-INFER-TIME.

This module provides a comprehensive TimeSeries class for managing
temporal geospatial data with metadata and analysis capabilities.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TimeSeries:
    """
    TimeSeries data model for temporal geospatial data.

    Provides a structured representation of time-series data with
    temporal indexing, metadata, and spatial context.
    """

    def __init__(
        self,
        data: Union[pd.Series, pd.DataFrame, np.ndarray],
        timestamps: Optional[pd.DatetimeIndex] = None,
        spatial_location: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a TimeSeries object.

        Args:
            data: Time series data (Series, DataFrame, or array)
            timestamps: Optional timestamps (if None, uses data index)
            spatial_location: Optional spatial location {"lat": float, "lon": float}
            metadata: Optional metadata dictionary
        """
        # Convert to DataFrame if needed
        if isinstance(data, np.ndarray):
            if timestamps is None:
                raise ValueError("timestamps required when data is numpy array")
            self.data = pd.DataFrame(data, index=timestamps)
        elif isinstance(data, pd.Series):
            self.data = data.to_frame()
            if timestamps is not None:
                self.data.index = timestamps
        else:
            self.data = data.copy()
            if timestamps is not None:
                self.data.index = timestamps

        self.spatial_location = spatial_location
        self.metadata = metadata or {}

        # Validate temporal index
        if not isinstance(self.data.index, pd.DatetimeIndex):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception as e:
                raise ValueError(f"Could not convert index to datetime: {e}")

        logger.debug(f"Created TimeSeries with {len(self.data)} observations")

    def __len__(self) -> int:
        """Get length of time series."""
        return len(self.data)

    @property
    def timestamps(self) -> pd.DatetimeIndex:
        """Get timestamps."""
        return self.data.index

    @property
    def start_time(self) -> datetime:
        """Get start time."""
        return self.data.index[0]

    @property
    def end_time(self) -> datetime:
        """Get end time."""
        return self.data.index[-1]

    @property
    def duration(self) -> timedelta:
        """Get time series duration."""
        return self.end_time - self.start_time

    @property
    def frequency(self) -> Optional[str]:
        """Get inferred frequency."""
        try:
            return pd.infer_freq(self.data.index)
        except Exception:
            return None

    def resample(self, frequency: str, method: str = "mean") -> "TimeSeries":
        """
        Resample the time series to a different frequency.

        Args:
            frequency: Target frequency (e.g., '1H', '1D', '1W')
            method: Aggregation method ('mean', 'sum', 'max', 'min', 'first', 'last')

        Returns:
            Resampled TimeSeries
        """
        if method == "mean":
            resampled_data = self.data.resample(frequency).mean()
        elif method == "sum":
            resampled_data = self.data.resample(frequency).sum()
        elif method == "max":
            resampled_data = self.data.resample(frequency).max()
        elif method == "min":
            resampled_data = self.data.resample(frequency).min()
        elif method == "first":
            resampled_data = self.data.resample(frequency).first()
        elif method == "last":
            resampled_data = self.data.resample(frequency).last()
        else:
            raise ValueError(f"Unknown resampling method: {method}")

        return TimeSeries(
            data=resampled_data,
            spatial_location=self.spatial_location,
            metadata={**self.metadata, "resampled_from": self.frequency},
        )

    def interpolate(self, method: str = "linear") -> "TimeSeries":
        """
        Interpolate missing values.

        Args:
            method: Interpolation method ('linear', 'time', 'polynomial', 'spline')

        Returns:
            Interpolated TimeSeries
        """
        interpolated_data = self.data.interpolate(method=method)

        return TimeSeries(
            data=interpolated_data,
            spatial_location=self.spatial_location,
            metadata={**self.metadata, "interpolated": True},
        )

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistical summary of the time series.

        Returns:
            Dictionary of statistics
        """
        stats = {
            "count": len(self.data),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_days": self.duration.total_seconds() / 86400,
            "frequency": self.frequency,
        }

        # Add column-specific statistics
        for col in self.data.columns:
            stats[col] = {
                "mean": float(self.data[col].mean()),
                "std": float(self.data[col].std()),
                "min": float(self.data[col].min()),
                "max": float(self.data[col].max()),
                "missing_count": int(self.data[col].isna().sum()),
            }

        return stats

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert to pandas DataFrame.

        Returns:
            DataFrame representation
        """
        return self.data.copy()

    def slice(self, start: datetime, end: datetime) -> "TimeSeries":
        """
        Slice the time series to a time range.

        Args:
            start: Start time
            end: End time

        Returns:
            Sliced TimeSeries
        """
        sliced_data = self.data.loc[start:end]

        return TimeSeries(
            data=sliced_data,
            spatial_location=self.spatial_location,
            metadata={**self.metadata, "sliced": True},
        )



