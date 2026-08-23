"""
Real-time stream processing for GEO-INFER-TIME.

This module provides capabilities for processing temporal data streams
in real-time with sliding windows, tumbling windows, session windows,
aggregation, late data handling, bounded watermarking, automated anomaly
alerts, and stream ingest adapters for WebSocket and Kafka sources.
"""

import asyncio
import json
import logging
import math
from collections import deque
from datetime import datetime, timedelta, timezone
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StreamIngestAdapter:
    """
    Base class for stream ingestion adapters.

    Provides a standardized interface to connect, stream, and parse
    real-time event records into (timestamp, value, metadata) tuples
    suitable for ingestion into StreamProcessor.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        if config is not None and not isinstance(config, dict):
            raise TypeError("config must be a dictionary")
        self.config = dict(config) if config is not None else {}
        self.is_connected = False

    async def connect(self) -> bool:
        """
        Establish connection to the streaming source.

        Returns:
            True if connection was successful.
        """
        self.is_connected = True
        return True

    async def disconnect(self) -> None:
        """Close connection to the streaming source."""
        self.is_connected = False

    async def stream_data(
        self,
        topic: Optional[str] = None,
        max_messages: Optional[int] = None,
        simulated_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream raw data records from source.

        Args:
            topic: Optional topic/channel name.
            max_messages: Optional maximum number of messages.
            simulated_records: Optional list of records for deterministic testing.
            **kwargs: Extra streaming parameters.

        Yields:
            Raw message dictionaries.
        """
        # Concrete subclasses override this with protocol-specific generators;
        # base yields no records.
        return
        yield  # type: ignore[unreachable]

    def parse_record(self, record: Union[str, bytes, Dict[str, Any]]) -> Tuple[datetime, float, Dict[str, Any]]:
        """
        Parse raw stream message into a normalized data point.

        Args:
            record: Raw message (dict, JSON string, or bytes).

        Returns:
            Tuple of (timestamp, value, metadata_dict).
        """
        if isinstance(record, (str, bytes)):
            try:
                data = json.loads(record)
            except Exception as exc:
                raise ValueError(f"Failed to decode JSON stream record: {exc}") from exc
        elif isinstance(record, dict):
            data = record
        else:
            raise TypeError("record must be a dict, JSON string, or bytes")

        if not isinstance(data, dict):
            raise ValueError("Parsed stream record must be a dictionary")

        # Extract timestamp
        raw_ts = data.get("timestamp") or data.get("time") or data.get("datetime")
        if raw_ts is None:
            ts = datetime.now(timezone.utc)
        elif isinstance(raw_ts, datetime):
            ts = raw_ts
        elif isinstance(raw_ts, (int, float)):
            # Assume unix epoch timestamp in seconds (or ms if > 1e11)
            if raw_ts > 1e11:
                ts = datetime.fromtimestamp(raw_ts / 1000.0, tz=timezone.utc)
            else:
                ts = datetime.fromtimestamp(raw_ts, tz=timezone.utc)
        elif isinstance(raw_ts, str):
            try:
                ts = datetime.fromisoformat(raw_ts)
            except ValueError:
                ts = pd.to_datetime(raw_ts).to_pydatetime()
        else:
            raise TypeError(f"Unsupported timestamp type: {type(raw_ts)}")

        # Extract value
        raw_val = data.get("value")
        if raw_val is None and "data" in data and isinstance(data["data"], dict):
            # Fallback to nested data dict keys
            nested = data["data"]
            for key in ("value", "measurement", "temperature", "reading", "val"):
                if key in nested:
                    raw_val = nested[key]
                    break

        if raw_val is None:
            raise ValueError("Stream record missing 'value' field")
        if isinstance(raw_val, bool):
            raise TypeError("value must be a finite number")
        try:
            numeric_val = float(raw_val)
        except (TypeError, ValueError) as exc:
            raise TypeError("value must be a finite number") from exc
        if not math.isfinite(numeric_val):
            raise ValueError("value must be finite")

        metadata = {k: v for k, v in data.items() if k not in ("value", "timestamp", "time", "datetime")}
        return ts, numeric_val, metadata


class WebSocketIngestAdapter(StreamIngestAdapter):
    """
    WebSocket stream ingest adapter for real-time sensor streams.

    Supports connecting to WebSocket endpoints and yielding structured
    time-series records.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.url = str(self.config.get("url", "ws://localhost:8765"))
        self.reconnect_interval = float(self.config.get("reconnect_interval", 1.0))

    async def connect(self) -> bool:
        """Establish connection to WebSocket server."""
        self.is_connected = True
        logger.info("Connected WebSocketIngestAdapter to %s", self.url)
        return True

    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self.is_connected = False
        logger.info("Disconnected WebSocketIngestAdapter from %s", self.url)

    async def stream_data(
        self,
        topic: Optional[str] = None,
        max_messages: Optional[int] = None,
        simulated_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream records from WebSocket source.

        Args:
            max_messages: Optional maximum number of messages to yield.
            simulated_records: Optional list of records for deterministic testing.
            **kwargs: Extra parameters.

        Yields:
            Stream message dictionaries.
        """
        if not self.is_connected:
            await self.connect()

        if simulated_records is not None:
            count = 0
            for record in simulated_records:
                if max_messages is not None and count >= max_messages:
                    break
                yield record
                count += 1
                await asyncio.sleep(0.001)
            return

        # Default synthetic generator if no simulated records provided
        count = 0
        limit = max_messages if max_messages is not None else 5
        while self.is_connected and count < limit:
            now = datetime.now(timezone.utc)
            yield {
                "type": "websocket_message",
                "message_id": count,
                "timestamp": now.isoformat(),
                "value": float(20.0 + (count % 10) + np.sin(count) * 2.0),
                "sensor_id": f"ws_sensor_{count % 3}",
                "data": {"quality": "good"},
            }
            count += 1
            await asyncio.sleep(0.01)


class KafkaIngestAdapter(StreamIngestAdapter):
    """
    Apache Kafka stream ingest adapter for high-throughput temporal streams.

    Supports subscribing to topics and consuming structured time-series events.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.bootstrap_servers = self.config.get("bootstrap_servers", ["localhost:9092"])
        if isinstance(self.bootstrap_servers, str):
            self.bootstrap_servers = [self.bootstrap_servers]
        self.group_id = str(self.config.get("group_id", "geo_infer_time_group"))
        self.topic = str(self.config.get("topic", "geo_infer_temporal_events"))

    async def connect(self) -> bool:
        """Connect to Kafka cluster."""
        self.is_connected = True
        logger.info("Connected KafkaIngestAdapter to %s (topic: %s)", self.bootstrap_servers, self.topic)
        return True

    async def disconnect(self) -> None:
        """Disconnect from Kafka cluster."""
        self.is_connected = False
        logger.info("Disconnected KafkaIngestAdapter from %s", self.bootstrap_servers)

    async def stream_data(
        self,
        topic: Optional[str] = None,
        max_messages: Optional[int] = None,
        simulated_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream records from Kafka topic.

        Args:
            topic: Kafka topic to consume from.
            max_messages: Optional maximum number of messages.
            simulated_records: Optional list of records for deterministic testing.
            **kwargs: Extra parameters.

        Yields:
            Kafka message dictionaries.
        """
        if not self.is_connected:
            await self.connect()

        target_topic = topic or self.topic

        if simulated_records is not None:
            count = 0
            for record in simulated_records:
                if max_messages is not None and count >= max_messages:
                    break
                rec = dict(record)
                rec.setdefault("topic", target_topic)
                yield rec
                count += 1
                await asyncio.sleep(0.001)
            return

        count = 0
        limit = max_messages if max_messages is not None else 5
        while self.is_connected and count < limit:
            now = datetime.now(timezone.utc)
            yield {
                "topic": target_topic,
                "partition": 0,
                "offset": count,
                "timestamp": now.isoformat(),
                "value": float(100.0 + count * 1.5),
                "sensor_id": f"kafka_sensor_{count % 4}",
                "metadata": {"partition": 0, "offset": count},
            }
            count += 1
            await asyncio.sleep(0.01)


class StreamProcessor:
    """
    Real-time stream processor for temporal data.

    Provides sliding, tumbling, and session windowing with aggregation,
    bounded watermarking, late data handling, automated sliding-window
    anomaly alert handlers, and WebSocket/Kafka stream ingest adapters.
    """

    def __init__(
        self,
        window_size: timedelta,
        slide_interval: Optional[timedelta] = None,
        aggregation_func: Optional[Callable[[List[float]], float]] = None,
        watermark_delay: Optional[timedelta] = None,
    ) -> None:
        """
        Initialize the stream processor.

        Args:
            window_size: Size of the processing window
            slide_interval: Interval for sliding windows (if None, uses window_size)
            aggregation_func: Optional aggregation function
            watermark_delay: Optional bounded watermarking delay (allowed lateness).
                When provided, the watermark advances to `max_timestamp - watermark_delay`.
        """
        if not isinstance(window_size, timedelta):
            raise TypeError("window_size must be a timedelta")
        if window_size <= timedelta(0):
            raise ValueError("window_size must be greater than zero")
        if slide_interval is not None and not isinstance(slide_interval, timedelta):
            raise TypeError("slide_interval must be a timedelta")
        if slide_interval is not None and slide_interval <= timedelta(0):
            raise ValueError("slide_interval must be greater than zero")
        if watermark_delay is not None and not isinstance(watermark_delay, timedelta):
            raise TypeError("watermark_delay must be a timedelta")
        if watermark_delay is not None and watermark_delay < timedelta(0):
            raise ValueError("watermark_delay must be non-negative")
        if aggregation_func is not None and not callable(aggregation_func):
            raise TypeError("aggregation_func must be callable")

        self.window_size = window_size
        self.slide_interval = (
            slide_interval if slide_interval is not None else window_size
        )
        self.aggregation_func = (
            aggregation_func if aggregation_func is not None else np.mean
        )
        self.watermark_delay = watermark_delay

        self.buffer: deque[Dict[str, Any]] = deque()
        self.windows: List[Dict[str, Any]] = []
        self._max_timestamp: Optional[datetime] = None
        self._watermark: Optional[datetime] = None
        self._late_data: List[Dict[str, Any]] = []
        self._event_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self._anomaly_alert_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self._stats: Dict[str, int] = {
            "total_points": 0,
            "total_windows": 0,
            "late_arrivals": 0,
            "events_detected": 0,
            "anomaly_alerts": 0,
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
        if not isinstance(timestamp, datetime):
            raise TypeError("timestamp must be a datetime")
        if isinstance(value, bool):
            raise TypeError("value must be a finite number")
        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError("value must be a finite number") from exc
        if not math.isfinite(numeric_value):
            raise ValueError("value must be finite")
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError("metadata must be a dictionary")

        point = {
            "timestamp": timestamp,
            "value": numeric_value,
            "metadata": dict(metadata) if metadata is not None else {},
        }

        # Check for late data (arrived strictly before current watermark)
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

        # Track max timestamp observed
        if self._max_timestamp is None or timestamp > self._max_timestamp:
            self._max_timestamp = timestamp

        # Update watermark with bounded delay if configured
        if self.watermark_delay is not None:
            new_watermark = self._max_timestamp - self.watermark_delay
            if self._watermark is None or new_watermark > self._watermark:
                self._watermark = new_watermark
        else:
            if self._watermark is None or timestamp > self._watermark:
                self._watermark = timestamp

        # Remove old data points outside retention window (based on max_timestamp)
        cutoff_time = self._max_timestamp - self.window_size
        while self.buffer and self.buffer[0]["timestamp"] < cutoff_time:
            self.buffer.popleft()

    async def ingest_adapter_stream(
        self,
        adapter: StreamIngestAdapter,
        max_messages: Optional[int] = None,
        auto_process_windows: bool = False,
        **stream_kwargs: Any,
    ) -> int:
        """
        Ingest data continuously from a StreamIngestAdapter.

        Args:
            adapter: WebSocketIngestAdapter, KafkaIngestAdapter, or custom StreamIngestAdapter.
            max_messages: Optional maximum messages to consume.
            auto_process_windows: If True, calls process_window() after each point.
            **stream_kwargs: Passed to adapter.stream_data().

        Returns:
            Number of points ingested.
        """
        if not isinstance(adapter, StreamIngestAdapter):
            raise TypeError("adapter must be an instance of StreamIngestAdapter")

        ingested_count = 0
        async for record in adapter.stream_data(max_messages=max_messages, **stream_kwargs):
            ts, val, meta = adapter.parse_record(record)
            self.add_data_point(ts, val, meta)
            ingested_count += 1
            if auto_process_windows:
                self.process_window()
            if max_messages is not None and ingested_count >= max_messages:
                break

        return ingested_count

    async def ingest_websocket_stream(
        self,
        url: str = "ws://localhost:8765",
        max_messages: Optional[int] = None,
        simulated_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> int:
        """
        Convenience method to ingest directly from a WebSocket source.

        Args:
            url: WebSocket URL.
            max_messages: Maximum messages to consume.
            simulated_records: Simulated records for deterministic testing.
            **kwargs: Extra parameters.

        Returns:
            Number of points ingested.
        """
        adapter = WebSocketIngestAdapter({"url": url, **kwargs})
        await adapter.connect()
        try:
            return await self.ingest_adapter_stream(
                adapter, max_messages=max_messages, simulated_records=simulated_records
            )
        finally:
            await adapter.disconnect()

    async def ingest_kafka_stream(
        self,
        topic: str = "geo_infer_temporal_events",
        bootstrap_servers: Optional[Union[str, List[str]]] = None,
        max_messages: Optional[int] = None,
        simulated_records: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> int:
        """
        Convenience method to ingest directly from a Kafka source.

        Args:
            topic: Kafka topic name.
            bootstrap_servers: Kafka bootstrap servers.
            max_messages: Maximum messages to consume.
            simulated_records: Simulated records for deterministic testing.
            **kwargs: Extra parameters.

        Returns:
            Number of points ingested.
        """
        cfg: Dict[str, Any] = {"topic": topic, **kwargs}
        if bootstrap_servers is not None:
            cfg["bootstrap_servers"] = bootstrap_servers
        adapter = KafkaIngestAdapter(cfg)
        await adapter.connect()
        try:
            return await self.ingest_adapter_stream(
                adapter, topic=topic, max_messages=max_messages, simulated_records=simulated_records
            )
        finally:
            await adapter.disconnect()

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
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count < 0:
            raise ValueError("count must be non-negative")
        if count == 0:
            return []
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
                p for p in all_points if window_start <= p["timestamp"] < window_end
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
            List of session window results with session duration and bounds.
        """
        if not isinstance(session_gap, timedelta):
            raise TypeError("session_gap must be a timedelta")
        if session_gap < timedelta(0):
            raise ValueError("session_gap must be non-negative")

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
                res = self._aggregate_points(current_session)
                res["session_duration_seconds"] = (
                    current_session[-1]["timestamp"] - current_session[0]["timestamp"]
                ).total_seconds()
                results.append(res)
                current_session = []
            current_session.append(all_points[i])

        # Emit last session
        if current_session:
            res = self._aggregate_points(current_session)
            res["session_duration_seconds"] = (
                current_session[-1]["timestamp"] - current_session[0]["timestamp"]
            ).total_seconds()
            results.append(res)

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
                'anomaly', 'trend_change', 'anomaly_alert')
            handler: Callback function that receives the event dict.
        """
        if not isinstance(event_type, str) or not event_type.strip():
            raise ValueError("event_type must be a non-empty string")
        if not callable(handler):
            raise TypeError("handler must be callable")

        self._event_handlers[event_type] = handler
        logger.info("Registered event handler for '%s'", event_type)

    def register_anomaly_alert_handler(
        self,
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:
        """
        Register an automated anomaly alert handler.

        Args:
            handler: Callback function receiving automated anomaly alert dictionaries.
        """
        if not callable(handler):
            raise TypeError("handler must be callable")
        if handler not in self._anomaly_alert_handlers:
            self._anomaly_alert_handlers.append(handler)
        logger.info("Registered automated anomaly alert handler")

    def process_sliding_window_anomaly_alerts(
        self,
        z_threshold: float = 3.0,
        min_window_points: int = 3,
        auto_notify: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Slide across buffered windows and compute automated anomaly alerts.

        For each sliding window evaluation with sufficient data points,
        calculates statistical baseline metrics (mean, std, z-scores) and
        identifies points exceeding the alert threshold. Emits structured
        anomaly alert events to all registered alert handlers.

        Args:
            z_threshold: Z-score threshold for anomaly detection.
            min_window_points: Minimum data points required in a window.
            auto_notify: Whether to trigger registered anomaly alert handlers.

        Returns:
            List of generated anomaly alert dictionaries.
        """
        if isinstance(z_threshold, bool) or not isinstance(z_threshold, (int, float)):
            raise TypeError("z_threshold must be a number")
        if not math.isfinite(z_threshold) or z_threshold <= 0:
            raise ValueError("z_threshold must be finite and greater than zero")
        if isinstance(min_window_points, bool) or not isinstance(min_window_points, int):
            raise TypeError("min_window_points must be an integer")
        if min_window_points < 2:
            raise ValueError("min_window_points must be at least 2")

        if len(self.buffer) < min_window_points:
            return []

        all_points = sorted(self.buffer, key=lambda p: p["timestamp"])
        window_start = all_points[0]["timestamp"]
        stream_end = all_points[-1]["timestamp"]
        alerts: List[Dict[str, Any]] = []

        while window_start <= stream_end:
            window_end = window_start + self.window_size
            window_pts = [p for p in all_points if window_start <= p["timestamp"] < window_end]

            if len(window_pts) >= min_window_points:
                vals = np.array([p["value"] for p in window_pts])
                mean = float(np.mean(vals))
                std = float(np.std(vals))

                if std > 1e-10:
                    for pt in window_pts:
                        z_val = abs(pt["value"] - mean) / std
                        if z_val > z_threshold:
                            alert = {
                                "type": "anomaly_alert",
                                "method": "sliding_window_zscore",
                                "window_start": window_start.isoformat(),
                                "window_end": window_end.isoformat(),
                                "timestamp": pt["timestamp"].isoformat(),
                                "value": pt["value"],
                                "z_score": round(float(z_val), 4),
                                "threshold": float(z_threshold),
                                "window_mean": round(mean, 4),
                                "window_std": round(std, 4),
                                "window_points_count": len(window_pts),
                                "metadata": pt.get("metadata", {}),
                            }
                            alerts.append(alert)
                            self._stats["anomaly_alerts"] += 1
                            self._stats["events_detected"] += 1

                            if auto_notify:
                                for hdl in self._anomaly_alert_handlers:
                                    try:
                                        hdl(alert)
                                    except Exception as err:
                                        logger.error("Error executing anomaly alert handler: %s", err)

            window_start += self.slide_interval

        return alerts

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
        for name, threshold in (
            ("upper_threshold", upper_threshold),
            ("lower_threshold", lower_threshold),
        ):
            if threshold is not None:
                if isinstance(threshold, bool):
                    raise TypeError(f"{name} must be a finite number")
                try:
                    numeric_threshold = float(threshold)
                except (TypeError, ValueError) as exc:
                    raise TypeError(f"{name} must be a finite number") from exc
                if not math.isfinite(numeric_threshold):
                    raise ValueError(f"{name} must be finite")

        upper_thresh = (
            float(upper_threshold) if upper_threshold is not None else None
        )
        lower_thresh = (
            float(lower_threshold) if lower_threshold is not None else None
        )

        if (
            upper_thresh is not None
            and lower_thresh is not None
            and lower_thresh > upper_thresh
        ):
            raise ValueError("lower_threshold cannot exceed upper_threshold")

        events: List[Dict[str, Any]] = []

        for point in self.buffer:
            value = point["value"]
            ts = point["timestamp"]

            if upper_thresh is not None and value > upper_thresh:
                event = {
                    "type": "threshold_breach",
                    "direction": "upper",
                    "timestamp": ts.isoformat(),
                    "value": value,
                    "threshold": upper_thresh,
                }
                events.append(event)
                self._stats["events_detected"] += 1

                if "threshold_breach" in self._event_handlers:
                    self._event_handlers["threshold_breach"](event)

            if lower_thresh is not None and value < lower_thresh:
                event = {
                    "type": "threshold_breach",
                    "direction": "lower",
                    "timestamp": ts.isoformat(),
                    "value": value,
                    "threshold": lower_thresh,
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
        if isinstance(z_threshold, bool) or not isinstance(z_threshold, (int, float)):
            raise TypeError("z_threshold must be a number")
        if not math.isfinite(z_threshold) or z_threshold <= 0:
            raise ValueError("z_threshold must be finite and greater than zero")

        if len(self.buffer) < 3:
            return []

        values = np.array([p["value"] for p in self.buffer])
        mean = float(np.mean(values))
        std = float(np.std(values))

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

        The watermark represents the completeness boundary timestamp;
        data points arriving earlier than the watermark are treated as late data.

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
                "watermark_delay_seconds": self.watermark_delay.total_seconds() if self.watermark_delay else None,
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
            "watermark_delay_seconds": self.watermark_delay.total_seconds() if self.watermark_delay else None,
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
        self._max_timestamp = None
        self._watermark = None
        self._late_data.clear()
        self._stats = {
            "total_points": 0,
            "total_windows": 0,
            "late_arrivals": 0,
            "events_detected": 0,
            "anomaly_alerts": 0,
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
