"""
Real-time stream processing for GEO-INFER-TIME.

This module provides capabilities for processing temporal data streams
in real-time with windowing, aggregation, and event detection.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Real-time stream processor for temporal data.

    Provides windowing, aggregation, and real-time processing capabilities
    for temporal data streams.
    """

    def __init__(
        self,
        window_size: timedelta,
        slide_interval: Optional[timedelta] = None,
        aggregation_func: Optional[Callable] = None,
    ) -> None:
        """
        Initialize the stream processor.

        Args:
            window_size: Size of the processing window
            slide_interval: Interval for sliding windows (if None, uses window_size)
            aggregation_func: Optional aggregation function
        """
        self.window_size = window_size
        self.slide_interval = slide_interval or window_size
        self.aggregation_func = aggregation_func or np.mean

        self.buffer: deque = deque()
        self.windows: List[Dict[str, Any]] = []

    def add_data_point(self, timestamp: datetime, value: float, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a data point to the stream.

        Args:
            timestamp: Data point timestamp
            value: Data point value
            metadata: Optional metadata
        """
        self.buffer.append(
            {
                "timestamp": timestamp,
                "value": value,
                "metadata": metadata or {},
            }
        )

        # Remove old data points outside window
        cutoff_time = timestamp - self.window_size
        while self.buffer and self.buffer[0]["timestamp"] < cutoff_time:
            self.buffer.popleft()

    def process_window(self) -> Optional[Dict[str, Any]]:
        """
        Process the current window and return aggregated result.

        Returns:
            Aggregated window result or None if window is empty
        """
        if not self.buffer:
            return None

        window_data = list(self.buffer)
        values = [point["value"] for point in window_data]

        result = {
            "window_start": window_data[0]["timestamp"].isoformat(),
            "window_end": window_data[-1]["timestamp"].isoformat(),
            "count": len(window_data),
            "aggregated_value": float(self.aggregation_func(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "std": float(np.std(values)),
        }

        self.windows.append(result)
        return result

    def get_recent_windows(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent processing windows.

        Args:
            count: Number of recent windows to return

        Returns:
            List of recent window results
        """
        return self.windows[-count:]


