# GEO-INFER-COMMS/src/geo_infer_comms/api

Api workspace within `GEO-INFER-COMMS`.

## Contents

- `__init__.py`
- `rest_api.py`
- `websocket_api.py`

## Public Interface

- `rest_api.py:CommunicationAPI` (class)
- `rest_api.py:create_api_server` (function)
- `websocket_api.py:WebSocketManager` (class)
- `websocket_api.py:WebSocketConnection` (class)
- `websocket_api.py:WebSocketServer` (class)
- `websocket_api.py:GeospatialWebSocketHandler` (class)
- `websocket_api.py:RealTimeMessageBroadcaster` (class)
- `websocket_api.py:WebSocketAPIManager` (class)

## Module Metadata

- Module: `GEO-INFER-COMMS`
- Package: `geo_infer_comms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-COMMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS`

## Dependencies

- `fastapi>=0.68.0`
- `pydantic>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
