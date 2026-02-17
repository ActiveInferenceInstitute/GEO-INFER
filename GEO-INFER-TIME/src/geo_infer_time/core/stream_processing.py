"""
Real-time stream processing for GEO-INFER-TIME.

This module provides capabilities for processing temporal data streams
in real-time with sliding windows, tumbling windows, session windows,
aggregation, late data handling, and event detection.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import deque
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class StreamProcessor:
    """
    Real-time stream processor for temporal data.

    Provides sliding, tumbling, and session windowing with aggregation,
    late data handling, watermark management, and event detection.
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
        self._watermark: Optional[datetime] = None
        self._late_data: List[Dict[str, Any]] = []
        self._event_handlers: Dict[str, Callable] = {}
        self._stats = {
            "total_points": 0,
            "total_windows": 0,
            "late_arrivals": 0,
            "events_detected": 0,
        }

    def add_data_point(
        self,
        timestamp: datetime,
        value: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a data point to the stream.

        Args:
            timestamp: Data point timestamp
            value: Data point value
            metadata: Optional metadata
        """
        point = {
            "timestamp": timestamp,
            "value": value,
            "metadata": metadata or {},
        }

        # Check for late data (arrived after watermark)
        if self._watermark is not None and timestamp < self._watermark:
            self._late_data.append(point)
            self._stats["late_arrivals"] += 1
            logger.debug(
                "Late data point received: %s (watermark: %s)",
                timestamp.isoformat(),
                self._watermark.isoformat(),
            )
        else:
            self.buffer.append(point)

        self._stats["total_points"] += 1

        # Remove old data points outside window
        cutoff_time = timestamp - self.window_size
        while self.buffer and self.buffer[0]["timestamp"] < cutoff_time:
            self.buffer.popleft()

        # Update watermark
        if self._watermark is None or timestamp > self._watermark:
            self._watermark = timestamp

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
            "std": float(np.std(values)) if len(values) > 1 else 0.0,
            "median": float(np.median(values)),
        }

        self.windows.append(result)
        self._stats["total_windows"] += 1
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

    def process_tumbling_windows(self) -> List[Dict[str, Any]]:
        """
        Process data using non-overlapping tumbling windows.

        Divides the buffered data into fixed-size, non-overlapping windows
        and aggregates each independently.

        Returns:
            List of tumbling window results.
        """
        if not self.buffer:
            return []

        all_points = sorted(self.buffer, key=lambda p: p["timestamp"])
        if not all_points:
            return []

        window_start = all_points[0]["timestamp"]
        results: List[Dict[str, Any]] = []
        current_window: List[Dict[str, Any]] = []

        for point in all_points:
            if point["timestamp"] >= window_start + self.window_size:
                # Emit current window
                if current_window:
                    results.append(self._aggregate_points(current_window))
                # Start new window aligned to boundary
                window_start = window_start + self.window_size
                current_window = []
            current_window.append(point)

        # Emit last window if non-empty
        if current_window:
            results.append(self._aggregate_points(current_window))

        return results

    def process_sliding_windows(self) -> List[Dict[str, Any]]:
        """
        Process data using overlapping sliding windows.

        Slides a window of fixed size across the data at the configured
        slide interval, producing an aggregated result for each position.

        Returns:
            List of sliding window results.
        """
        if not self.buffer:
            return []

        all_points = sorted(self.buffer, key=lambda p: p["timestamp"])
        if not all_points:
            return []

        results: List[Dict[str, Any]] = []
        window_start = all_points[0]["timestamp"]
        stream_end = all_points[-1]["timestamp"]

        while window_start <= stream_end:
            window_end = window_start + self.window_size
            window_points = [
                p
                for p in all_points
                if window_start <= p["timestamp"] < window_end
            ]

            if window_points:
                results.append(self._aggregate_points(window_points))

            window_start += self.slide_interval

        return results

    def process_session_windows(
        self,
        session_gap: timedelta,
    ) -> List[Dict[str, Any]]:
        """
        Process data using session windows.

        Groups data points that arrive within a specified gap of each other
        into sessions. A new session starts when no data arrives for longer
        than session_gap.

        Args:
            session_gap: Maximum inactivity gap before starting a new session.

        Returns:
            List of session window results.
        """
        if not self.buffer:
            return []

        all_points = sorted(self.buffer, key=lambda p: p["timestamp"])
        if not all_points:
            return []

        results: List[Dict[str, Any]] = []
        current_session: List[Dict[str, Any]] = [all_points[0]]

        for i in range(1, len(all_points)):
            gap = all_points[i]["timestamp"] - all_points[i - 1]["timestamp"]
            if gap > session_gap:
                # End current session, start new one
                results.append(self._aggregate_points(current_session))
                current_session = []
            current_session.append(all_points[i])

        # Emit last session
        if current_session:
            results.append(self._aggregate_points(current_session))

        return results

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: Type of event to handle (e.g. 'threshold_breach',
                'anomaly', 'trend_change')
            handler: Callback function that receives the event dict.
        """
        self._event_handlers[event_type] = handler
        logger.info("Registered event handler for '%s'", event_type)

    def detect_threshold_events(
        self,
        upper_threshold: Optional[float] = None,
        lower_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Detect threshold breach events in the current buffer.

        Args:
            upper_threshold: Upper value threshold.
            lower_threshold: Lower value threshold.

        Returns:
            List of detected threshold events.
        """
        events: List[Dict[str, Any]] = []

        for point in self.buffer:
            value = point["value"]
            ts = point["timestamp"]

            if upper_threshold is not None and value > upper_threshold:
                event = {
                    "type": "threshold_breach",
                    "direction": "upper",
                    "timestamp": ts.isoformat(),
                    "value": value,
                    "threshold": upper_threshold,
                }
                events.append(event)
                self._stats["events_detected"] += 1

                if "threshold_breach" in self._event_handlers:
                    self._event_handlers["threshold_breach"](event)

            if lower_threshold is not None and value < lower_threshold:
                event = {
                    "type": "threshold_breach",
                    "direction": "lower",
                    "timestamp": ts.isoformat(),
                    "value": value,
                    "threshold": lower_threshold,
                }
                events.append(event)
                self._stats["events_detected"] += 1

                if "threshold_breach" in self._event_handlers:
                    self._event_handlers["threshold_breach"](event)

        return events

    def detect_anomalies_zscore(
        self,
        z_threshold: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous data points using z-score on the current buffer.

        Args:
            z_threshold: Z-score threshold for anomaly detection.

        Returns:
            List of detected anomaly events.
        """
        if len(self.buffer) < 3:
            return []

        values = np.array([p["value"] for p in self.buffer])
        mean = np.mean(values)
        std = np.std(values)

        if std < 1e-10:
            return []

        anomalies: List[Dict[str, Any]] = []

        for point in self.buffer:
            z_score = abs(point["value"] - mean) / std
            if z_score > z_threshold:
                event = {
                    "type": "anomaly",
                    "method": "zscore",
                    "timestamp": point["timestamp"].isoformat(),
                    "value": point["value"],
                    "z_score": round(float(z_score), 4),
                    "mean": round(float(mean), 4),
                    "std": round(float(std), 4),
                }
                anomalies.append(event)
                self._stats["events_detected"] += 1

                if "anomaly" in self._event_handlers:
                    self._event_handlers["anomaly"](event)

        return anomalies

    def get_watermark(self) -> Optional[datetime]:
        """
        Get the current watermark timestamp.

        The watermark represents the latest timestamp seen,
        used for late data detection.

        Returns:
            Current watermark or None if no data received.
        """
        return self._watermark

    def get_late_data(self) -> List[Dict[str, Any]]:
        """
        Get all late-arriving data points.

        Returns:
            List of data points that arrived after the watermark.
        """
        return list(self._late_data)

    def flush_late_data(self) -> List[Dict[str, Any]]:
        """
        Flush late data and return it, clearing the late buffer.

        Returns:
            List of late data points that were cleared.
        """
        flushed = list(self._late_data)
        self._late_data.clear()
        return flushed

    def get_buffer_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current buffer state.

        Returns:
            Dictionary with buffer statistics.
        """
        if not self.buffer:
            return {
                "size": 0,
                "window_start": None,
                "window_end": None,
                "watermark": self._watermark.isoformat() if self._watermark else None,
            }

        values = [p["value"] for p in self.buffer]
        return {
            "size": len(self.buffer),
            "window_start": self.buffer[0]["timestamp"].isoformat(),
            "window_end": self.buffer[-1]["timestamp"].isoformat(),
            "mean": round(float(np.mean(values)), 4),
            "min": round(float(np.min(values)), 4),
            "max": round(float(np.max(values)), 4),
            "watermark": self._watermark.isoformat() if self._watermark else None,
            "late_data_count": len(self._late_data),
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get stream processing statistics.

        Returns:
            Dictionary of cumulative statistics.
        """
        return dict(self._stats)

    def reset(self) -> None:
        """Reset the stream processor, clearing all buffers and state."""
        self.buffer.clear()
        self.windows.clear()
        self._watermark = None
        self._late_data.clear()
        self._stats = {
            "total_points": 0,
            "total_windows": 0,
            "late_arrivals": 0,
            "events_detected": 0,
        }
        logger.info("StreamProcessor reset")

    def _aggregate_points(
        self,
        points: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Aggregate a list of data points into a window result.

        Args:
            points: List of data point dicts.

        Returns:
            Aggregated window result dict.
        """
        values = [p["value"] for p in points]
        return {
            "window_start": points[0]["timestamp"].isoformat(),
            "window_end": points[-1]["timestamp"].isoformat(),
            "count": len(points),
            "aggregated_value": float(self.aggregation_func(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "std": float(np.std(values)) if len(values) > 1 else 0.0,
            "median": float(np.median(values)),
        }
