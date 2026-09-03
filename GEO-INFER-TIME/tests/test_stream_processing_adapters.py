"""
Tests for TIME-01: WebSocket/Kafka stream ingest adapters, bounded
watermarking, session window duration, and automated sliding-window
anomaly alert handlers for GEO-INFER-TIME's StreamProcessor.
"""

import pytest
import numpy as np
from datetime import datetime, timedelta

from geo_infer_time.core.stream_processing import (
    StreamProcessor,
    StreamIngestAdapter,
    WebSocketIngestAdapter,
    KafkaIngestAdapter,
    _import_aiokafka,
    _import_websockets,
)


def _ts(base, seconds_offset):
    """Quick helper to create a timestamp offset from a base."""
    return base + timedelta(seconds=seconds_offset)


BASE_TIME = datetime(2024, 1, 1, 0, 0, 0)


# ===================================================================
# StreamIngestAdapter / parse_record
# ===================================================================


class TestStreamIngestAdapter:
    def test_config_must_be_dict(self):
        with pytest.raises(TypeError):
            StreamIngestAdapter(config="bad")

    def test_config_defaults_to_empty_dict(self):
        adapter = StreamIngestAdapter()
        assert adapter.config == {}
        assert adapter.is_connected is False

    def test_parse_iso_datetime_record(self):
        adapter = StreamIngestAdapter()
        record = {"timestamp": "2024-01-01T00:00:00", "value": 42.5, "sensor": "a"}
        ts, value, meta = adapter.parse_record(record)
        assert ts == datetime(2024, 1, 1, 0, 0, 0)
        assert value == 42.5
        assert meta == {"sensor": "a"}

    def test_parse_json_string_record(self):
        adapter = StreamIngestAdapter()
        ts, value, meta = adapter.parse_record('{"timestamp":"2024-01-01T00:00:00","value":7}')
        assert value == 7.0
        assert meta == {}

    def test_parse_bytes_record(self):
        adapter = StreamIngestAdapter()
        ts, value, meta = adapter.parse_record(b'{"timestamp":"2024-01-01T00:00:00","value":3.0}')
        assert value == 3.0

    def test_parse_nested_data_value(self):
        adapter = StreamIngestAdapter()
        record = {"timestamp": "2024-01-01T00:00:00", "data": {"measurement": 11.0}}
        ts, value, meta = adapter.parse_record(record)
        assert value == 11.0

    def test_parse_invalid_json_raises(self):
        adapter = StreamIngestAdapter()
        with pytest.raises(ValueError):
            adapter.parse_record("{not-json")

    def test_parse_missing_value_closes_base(self):
        adapter = StreamIngestAdapter()
        with pytest.raises(ValueError):
            adapter.parse_record({"timestamp": "2024-01-01T00:00:00"})

    def test_parse_invalid_type_raises(self):
        adapter = StreamIngestAdapter()
        with pytest.raises(TypeError):
            adapter.parse_record(123)

    def test_base_stream_data_yields_nothing(self):
        adapter = StreamIngestAdapter()

        async def count_items():
            agen = adapter.stream_data()
            total = 0
            async for _item in agen:
                total += 1
            return total

        assert asyncio_run(count_items()) == 0


def asyncio_run(coro):
    """Run a coroutine to completion synchronously."""
    import asyncio

    return asyncio.run(coro)


# ===================================================================
# WebSocketIngestAdapter
# ===================================================================


class TestWebSocketIngestAdapter:
    def test_init_defaults(self):
        adapter = WebSocketIngestAdapter()
        assert adapter.url == "ws://localhost:8765"
        assert adapter.is_connected is False

    def test_connect_and_disconnect(self):
        adapter = WebSocketIngestAdapter(
            {"url": "ws://example.com:8080"}, allow_simulated=True
        )
        assert adapter.url == "ws://example.com:8080"
        assert asyncio_run(adapter.connect()) is True
        assert adapter.is_connected is True
        asyncio_run(adapter.disconnect())
        assert adapter.is_connected is False

    def test_stream_simulated_records_with_limit(self):
        adapter = WebSocketIngestAdapter(allow_simulated=True)
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0},
            {"timestamp": "2024-01-01T00:00:02", "value": 3.0},
        ]

        async def collect():
            out = []
            async for rec in adapter.stream_data(simulated_records=records, max_messages=2):
                out.append(rec)
            return out

        result = asyncio_run(collect())
        assert len(result) == 2

    def test_stream_default_generator_yields_records(self):
        adapter = WebSocketIngestAdapter(allow_simulated=True)

        async def collect():
            out = []
            async for rec in adapter.stream_data(max_messages=3):
                out.append(rec)
            return out

        result = asyncio_run(collect())
        assert len(result) == 3
        assert all("timestamp" in r for r in result)
        assert all("value" in r for r in result)


    def test_real_websocket_transport_contract(self):
        """Real transport: in-process WS server -> adapter.parse_record.

        With ``websockets`` installed this spins a real server on an
        ephemeral port, pushes three JSON records, and asserts the adapter
        parses each through ``parse_record``. Without it, the gate itself
        is verified instead: lazy import reports absence and ``connect``
        raises the documented error without flipping ``is_connected``.
        """
        import importlib.util
        import json as _json

        if importlib.util.find_spec("websockets") is None:
            websockets = _import_websockets()
            assert websockets is None
            adapter = WebSocketIngestAdapter({"url": "ws://127.0.0.1:9"})
            with pytest.raises(RuntimeError, match="websockets not installed"):
                asyncio_run(adapter.connect())
            assert adapter.is_connected is False
            return

        import websockets

        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0, "sensor": "ws-a"},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0, "sensor": "ws-b"},
            {"timestamp": "2024-01-01T00:00:02", "value": 3.0, "sensor": "ws-c"},
        ]

        async def handler(websocket):
            for record in records:
                await websocket.send(_json.dumps(record))
            # Returning closes the connection: the adapter's async-for then
            # sees a clean end-of-stream instead of waiting for a fourth
            # message that never arrives.

        async def run():
            server = await websockets.serve(handler, "127.0.0.1", 0)
            port = server.sockets[0].getsockname()[1]
            adapter = WebSocketIngestAdapter({"url": f"ws://127.0.0.1:{port}"})
            out = []
            try:
                await adapter.connect()
                assert adapter.is_connected is True
                async for rec in adapter.stream_data():
                    out.append(adapter.parse_record(rec))
            finally:
                await adapter.disconnect()
                server.close()
                await server.wait_closed()
            return out

        result = asyncio_run(run())
        assert len(result) == 3
        assert [value for _ts, value, _meta in result] == [1.0, 2.0, 3.0]
        assert [meta["sensor"] for _ts, _value, meta in result] == [
            "ws-a",
            "ws-b",
            "ws-c",
        ]
        assert result[0][0] == datetime(2024, 1, 1, 0, 0, 0)

    def test_real_mode_rejects_simulated_records(self):
        """A real-mode adapter refuses simulated_records outright."""
        adapter = WebSocketIngestAdapter()
        adapter.is_connected = True  # simulate an established connection
        with pytest.raises(ValueError):
            asyncio_run(
                adapter.stream_data(simulated_records=[{"value": 1.0}]).__anext__()
            )


# ===================================================================
# KafkaIngestAdapter
# ===================================================================


class TestKafkaIngestAdapter:
    def test_init_defaults(self):
        adapter = KafkaIngestAdapter()
        assert adapter.bootstrap_servers == ["localhost:9092"]
        assert adapter.group_id == "geo_infer_time_group"
        assert adapter.topic == "geo_infer_temporal_events"

    def test_bootstrap_servers_string_normalization(self):
        adapter = KafkaIngestAdapter({"bootstrap_servers": "kafka:9092"})
        assert adapter.bootstrap_servers == ["kafka:9092"]

    def test_connect_and_disconnect(self):
        adapter = KafkaIngestAdapter({}, allow_simulated=True)
        assert asyncio_run(adapter.connect()) is True
        assert adapter.is_connected is True
        asyncio_run(adapter.disconnect())
        assert adapter.is_connected is False

    def test_stream_simulated_records_sets_topic(self):
        adapter = KafkaIngestAdapter({"topic": "events-topic"}, allow_simulated=True)
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0},
        ]

        async def collect():
            out = []
            async for rec in adapter.stream_data(simulated_records=records):
                out.append(rec)
            return out

        result = asyncio_run(collect())
        assert len(result) == 2
        assert result[0]["topic"] == "events-topic"

    def test_real_kafka_transport_import_gated(self):
        """Real Kafka mode is gated on the optional aiokafka dependency.

        With ``aiokafka`` absent, the lazy import reports ``None``/flag-off
        and ``connect`` raises the documented RuntimeError. With it
        present, the adapter constructs in real mode and refuses
        ``simulated_records`` (no broker needed for the gate contract).
        """
        import importlib.util

        if importlib.util.find_spec("aiokafka") is None:
            aiokafka = _import_aiokafka()
            assert aiokafka is None
            adapter = KafkaIngestAdapter({"topic": "real-topic"})
            with pytest.raises(RuntimeError, match="aiokafka not installed"):
                asyncio_run(adapter.connect())
            assert adapter.is_connected is False
            return

        adapter = KafkaIngestAdapter({"topic": "real-topic"})
        assert adapter.topic == "real-topic"
        adapter.is_connected = True  # simulate an established consumer
        with pytest.raises(ValueError):
            asyncio_run(
                adapter.stream_data(simulated_records=[{"value": 1.0}]).__anext__()
            )


# ===================================================================
# StreamProcessor ingest adapters
# ===================================================================


class TestStreamProcessorAdapterIngest:
    def test_ingest_adapter_stream_counts_points(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        adapter = WebSocketIngestAdapter(allow_simulated=True)
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0, "sensor": "a"},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0, "sensor": "b"},
            {"timestamp": "2024-01-01T00:00:02", "value": 3.0},
        ]

        count = asyncio_run(
            processor.ingest_adapter_stream(adapter, simulated_records=records)
        )
        assert count == 3
        assert processor.get_stats()["total_points"] == 3
        assert len(processor.buffer) == 3

    def test_ingest_adapter_stream_auto_process_windows(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        adapter = KafkaIngestAdapter(allow_simulated=True)
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0},
        ]

        asyncio_run(
            processor.ingest_adapter_stream(
                adapter, simulated_records=records, auto_process_windows=True
            )
        )
        assert processor.get_stats()["total_windows"] == 2

    def test_ingest_adapter_stream_rejects_non_adapter(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        with pytest.raises(TypeError):
            asyncio_run(processor.ingest_adapter_stream("not-an-adapter"))

    def test_ingest_websocket_stream_convenience(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 1.0},
            {"timestamp": "2024-01-01T00:00:01", "value": 2.0},
            {"timestamp": "2024-01-01T00:00:02", "value": 3.0},
        ]
        count = asyncio_run(
            processor.ingest_websocket_stream(
                url="ws://localhost:9000", simulated_records=records
            )
        )
        assert count == 3
        assert [p["value"] for p in processor.buffer] == [1.0, 2.0, 3.0]

    def test_ingest_kafka_stream_convenience(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        records = [
            {"timestamp": "2024-01-01T00:00:00", "value": 5.0},
            {"timestamp": "2024-01-01T00:00:01", "value": 6.0},
        ]
        count = asyncio_run(
            processor.ingest_kafka_stream(
                topic="telemetry", simulated_records=records
            )
        )
        assert count == 2
        assert processor.get_stats()["total_points"] == 2


# ===================================================================
# Bounded watermarking
# ===================================================================


class TestBoundedWatermarking:
    def test_watermark_advances_with_delay(self):
        processor = StreamProcessor(
            window_size=timedelta(minutes=5), watermark_delay=timedelta(seconds=10)
        )
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 30), 2.0)
        # max_timestamp = t+30, watermark = t+30 - 10s = t+20
        assert processor.get_watermark() == _ts(BASE_TIME, 20)

    def test_late_data_beyond_watermark_delay(self):
        processor = StreamProcessor(
            window_size=timedelta(minutes=5), watermark_delay=timedelta(seconds=10)
        )
        processor.add_data_point(_ts(BASE_TIME, 100), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 5), 2.0)
        # After t+100, watermark = t+90. t+5 < t+90 => late.
        assert processor.get_watermark() == _ts(BASE_TIME, 90)
        assert [p["value"] for p in processor.get_late_data()] == [2.0]

    def test_within_delay_is_not_late(self):
        processor = StreamProcessor(
            window_size=timedelta(minutes=5), watermark_delay=timedelta(seconds=10)
        )
        processor.add_data_point(_ts(BASE_TIME, 100), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 95), 2.0)
        # watermark = t+90, so t+95 >= t+90 is not late.
        assert processor.get_late_data() == []
        assert processor.get_stats()["late_arrivals"] == 0

    def test_zero_delay_bounds_watermark_to_max(self):
        processor = StreamProcessor(
            window_size=timedelta(minutes=5), watermark_delay=timedelta(0)
        )
        processor.add_data_point(_ts(BASE_TIME, 100), 1.0)
        assert processor.get_watermark() == _ts(BASE_TIME, 100)

    def test_watermark_delay_validation(self):
        with pytest.raises(TypeError):
            StreamProcessor(
                window_size=timedelta(minutes=5), watermark_delay="10"
            )
        with pytest.raises(ValueError):
            StreamProcessor(
                window_size=timedelta(minutes=5), watermark_delay=timedelta(seconds=-1)
            )

    def test_buffer_retention_uses_max_timestamp(self):
        processor = StreamProcessor(
            window_size=timedelta(seconds=10), watermark_delay=timedelta(seconds=3)
        )
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 100), 2.0)
        # Old point at t=0 evicted (max timestamp t=100 - 10s = t+90).
        assert len(processor.buffer) == 1


# ===================================================================
# Session windowing
# ===================================================================


class TestSessionWindowing:
    def test_session_duration_seconds_present(self):
        processor = StreamProcessor(window_size=timedelta(minutes=5))
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 5), 2.0)
        processor.add_data_point(_ts(BASE_TIME, 100), 3.0)  # new session

        sessions = processor.process_session_windows(timedelta(seconds=15))
        assert [s["count"] for s in sessions] == [2, 1]
        assert sessions[0]["session_duration_seconds"] == 5.0
        assert sessions[1]["session_duration_seconds"] == 0.0

    def test_single_session_duration(self):
        processor = StreamProcessor(window_size=timedelta(minutes=1))
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 5), 2.0)
        processor.add_data_point(_ts(BASE_TIME, 10), 3.0)

        sessions = processor.process_session_windows(timedelta(minutes=1))
        assert len(sessions) == 1
        assert sessions[0]["session_duration_seconds"] == 10.0


# ===================================================================
# Automated sliding-window anomaly alert handlers
# ===================================================================


class TestSlidingWindowAnomalyAlerts:
    def test_alert_emitted_for_spike(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        for i in range(40):
            processor.add_data_point(_ts(BASE_TIME, i), 1.0 if i != 25 else 100.0)

        handled = []
        processor.register_anomaly_alert_handler(handled.append)

        alerts = processor.process_sliding_window_anomaly_alerts(z_threshold=3.0)
        assert len(alerts) >= 1
        assert alerts[0]["type"] == "anomaly_alert"
        assert "window_start" in alerts[0]
        assert "window_end" in alerts[0]
        assert alerts[0]["method"] == "sliding_window_zscore"
        # The alert handler was invoked with the same alert payload.
        assert handled == alerts

    def test_alert_handler_stats_incremented(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        for i in range(40):
            processor.add_data_point(_ts(BASE_TIME, i), 1.0 if i != 25 else 100.0)

        processor.process_sliding_window_anomaly_alerts(z_threshold=3.0)
        stats = processor.get_stats()
        assert stats["anomaly_alerts"] >= 1
        assert stats["events_detected"] >= stats["anomaly_alerts"]

    def test_no_alerts_for_flat_series(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        for i in range(40):
            processor.add_data_point(_ts(BASE_TIME, i), 1.0)

        alerts = processor.process_sliding_window_anomaly_alerts(z_threshold=3.0)
        assert alerts == []

    def test_insufficient_points_returns_empty(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        processor.add_data_point(_ts(BASE_TIME, 1), 2.0)

        alerts = processor.process_sliding_window_anomaly_alerts(min_window_points=3)
        assert alerts == []

    def test_alert_validation_of_threshold(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        processor.add_data_point(_ts(BASE_TIME, 0), 1.0)
        with pytest.raises(ValueError):
            processor.process_sliding_window_anomaly_alerts(z_threshold=0)
        with pytest.raises(TypeError):
            processor.process_sliding_window_anomaly_alerts(z_threshold="high")
        with pytest.raises(ValueError):
            processor.process_sliding_window_anomaly_alerts(min_window_points=1)
        with pytest.raises(TypeError):
            processor.process_sliding_window_anomaly_alerts(min_window_points="three")

    def test_multiple_handlers_all_invoked(self):
        processor = StreamProcessor(window_size=timedelta(seconds=30))
        for i in range(40):
            processor.add_data_point(_ts(BASE_TIME, i), 1.0 if i != 25 else 100.0)

        first = []
        second = []
        processor.register_anomaly_alert_handler(first.append)
        processor.register_anomaly_alert_handler(second.append)

        processor.process_sliding_window_anomaly_alerts(z_threshold=3.0)
        assert len(first) == len(second)
        assert len(first) >= 1