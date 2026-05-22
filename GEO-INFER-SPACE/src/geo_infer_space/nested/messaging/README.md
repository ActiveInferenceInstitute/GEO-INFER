# GEO-INFER-SPACE/src/geo_infer_space/nested/messaging

Messaging workspace within `GEO-INFER-SPACE`.

## Contents

- `__init__.py`
- `message_broker.py`
- `protocols.py`
- `routing.py`

## Public Interface

- `message_broker.py:MessageType` (class)
- `message_broker.py:MessagePriority` (class)
- `message_broker.py:MessageStatus` (class)
- `message_broker.py:Message` (class)
- `message_broker.py:MessageHandler` (class)
- `message_broker.py:H3MessageBroker` (class)
- `protocols.py:ProtocolType` (class)
- `protocols.py:MessageFormat` (class)
- `protocols.py:ProtocolConfig` (class)
- `protocols.py:MessageProtocol` (class)
- `protocols.py:RequestResponseProtocol` (class)
- `protocols.py:PublishSubscribeProtocol` (class)
- `protocols.py:FireAndForgetProtocol` (class)
- `protocols.py:StreamingProtocol` (class)
- `protocols.py:BatchProtocol` (class)
- `routing.py:RoutingStrategy` (class)
- `routing.py:RouteMetric` (class)
- `routing.py:RouteSegment` (class)
- `routing.py:Route` (class)
- `routing.py:MessageRouter` (class)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.0.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
