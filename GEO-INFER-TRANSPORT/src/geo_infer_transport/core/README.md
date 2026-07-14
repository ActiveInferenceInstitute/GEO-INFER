# GEO-INFER-TRANSPORT/src/geo_infer_transport/core

Core workspace within `GEO-INFER-TRANSPORT`.

## Contents

- `__init__.py`
- `accessibility.py`
- `network.py`
- `routing.py`
- `traffic.py`
- `transit.py`

## Public Interface

- `accessibility.py:Isochrone` (class)
- `accessibility.py:ServiceArea` (class)
- `accessibility.py:AccessibilityAnalyzer` (class)
- `network.py:RoadClass` (class)
- `network.py:TransportMode` (class)
- `network.py:NetworkNode` (class)
- `network.py:NetworkEdge` (class)
- `network.py:TransportNetwork` (class)
- `routing.py:RoutingAlgorithm` (class)
- `routing.py:OptimizationCriteria` (class)
- `routing.py:Route` (class)
- `routing.py:RoutingEngine` (class)
- `traffic.py:TrafficCondition` (class)
- `traffic.py:TrafficCount` (class)
- `traffic.py:FlowResult` (class)
- `traffic.py:TrafficAnalyzer` (class)
- `transit.py:TransitMode` (class)
- `transit.py:TransitStop` (class)
- `transit.py:TransitRoute` (class)
- `transit.py:TransitOptimizer` (class)

## Module Metadata

- Module: `GEO-INFER-TRANSPORT`
- Package: `geo_infer_transport`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TRANSPORT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module TRANSPORT`

## Dependencies

- Dependencies are declared in `pyproject.toml` or inherited from the workspace.


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module TRANSPORT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
