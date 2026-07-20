"""
Tests for stream connectors in geo_infer_data.connectors.stream.
"""

import asyncio
import pytest

from geo_infer_data.connectors.stream import (
    StreamConnector,
    MQTTConnector,
    KafkaConnector,
    WebSocketConnector,
)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# StreamConnector base class
# ---------------------------------------------------------------------------


class TestStreamConnectorBase:
    def test_connect_raises_not_implemented(self):
        connector = StreamConnector()
        with pytest.raises(RuntimeError):
            _run(connector.connect())

    def test_stream_data_raises_not_implemented(self):
        connector = StreamConnector()
        with pytest.raises(RuntimeError):
            _run(connector.stream_data())

    def test_disconnect_does_not_raise(self):
        connector = StreamConnector()
        _run(connector.disconnect())


# ---------------------------------------------------------------------------
# MQTTConnector
# ---------------------------------------------------------------------------


class TestMQTTConnector:
    def test_init_defaults(self):
        connector = MQTTConnector({})
        assert connector.host == "localhost"
        assert connector.port == 1883
        assert connector.client_id == "geo_infer_data"

    def test_init_custom(self):
        config = {"host": "broker.example.com", "port": 8883, "client_id": "custom"}
        connector = MQTTConnector(config)
        assert connector.host == "broker.example.com"
        assert connector.port == 8883
        assert connector.client_id == "custom"

    def test_connect(self):
        connector = MQTTConnector({})
        assert _run(connector.connect()) is True

    def test_stream_data_yields_messages(self):
        connector = MQTTConnector({})

        async def collect_messages():
            messages = []
            async for msg in connector.stream_data(topic="sensors/temperature"):
                messages.append(msg)
                if len(messages) >= 3:
                    break
            return messages

        messages = _run(collect_messages())
        assert len(messages) >= 3
        assert all("topic" in m for m in messages)
        assert all("data" in m for m in messages)
        assert messages[0]["topic"] == "sensors/temperature"


# ---------------------------------------------------------------------------
# KafkaConnector
# ---------------------------------------------------------------------------


class TestKafkaConnector:
    def test_init(self):
        config = {"bootstrap_servers": ["kafka:9092"], "group_id": "test-group"}
        connector = KafkaConnector(config)
        assert connector.bootstrap_servers == ["kafka:9092"]
        assert connector.group_id == "test-group"

    def test_connect(self):
        connector = KafkaConnector({})
        assert _run(connector.connect()) is True

    def test_stream_data_yields_messages(self):
        connector = KafkaConnector({})

        async def collect_messages():
            messages = []
            async for msg in connector.stream_data(topic="geo-events"):
                messages.append(msg)
                if len(messages) >= 3:
                    break
            return messages

        messages = _run(collect_messages())
        assert len(messages) >= 3
        assert all("partition" in m for m in messages)
        assert all("offset" in m for m in messages)


# ---------------------------------------------------------------------------
# WebSocketConnector
# ---------------------------------------------------------------------------


class TestWebSocketConnector:
    def test_init(self):
        config = {"url": "ws://example.com:8080", "reconnect_interval": 10}
        connector = WebSocketConnector(config)
        assert connector.url == "ws://example.com:8080"
        assert connector.reconnect_interval == 10

    def test_connect(self):
        connector = WebSocketConnector({})
        assert _run(connector.connect()) is True

    def test_stream_data_yields_messages(self):
        connector = WebSocketConnector({})

        async def collect_messages():
            messages = []
            async for msg in connector.stream_data():
                messages.append(msg)
                if len(messages) >= 3:
                    break
            return messages

        messages = _run(collect_messages())
        assert len(messages) >= 3
        assert all("type" in m for m in messages)
        assert all("data" in m for m in messages)
        assert all("latitude" in m["data"] for m in messages)
