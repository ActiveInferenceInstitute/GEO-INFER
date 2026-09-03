# GEO-INFER-LOG/src/geo_infer_log/core

Core workspace within `GEO-INFER-LOG`.

## Contents

- `__init__.py`
- `delivery.py`
- `routing.py`
- `supply_chain.py`
- `transport.py`

## Public Interface

- `delivery.py:LastMileRouter` (class)
- `delivery.py:DeliveryScheduler` (class)
- `delivery.py:ServiceAreaAnalyzer` (class)
- `routing.py:VehicleType` (class)
- `routing.py:Vehicle` (class)
- `routing.py:RoutingParameters` (class)
- `routing.py:RouteOptimizer` (class)
- `routing.py:FleetManager` (class)
- `routing.py:VehicleRouter` (class)
- `routing.py:TravelTimeEstimator` (class)
- `routing.py:MultiObjectiveOptimizer` (class)
- `routing.py:RealTimeTracker` (class)
- `supply_chain.py:SupplyChainModel` (class)
- `supply_chain.py:ResilienceAnalyzer` (class)
- `supply_chain.py:NetworkOptimizer` (class)
- `supply_chain.py:FacilityLocator` (class)
- `supply_chain.py:InventoryManager` (class)
- `transport.py:MultiModalPlanner` (class)
- `transport.py:TransportationNetworkAnalyzer` (class)
- `transport.py:TrafficSimulator` (class)

## Module Metadata

- Module: `GEO-INFER-LOG`
- Package: `geo_infer_log`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-LOG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG`

## Dependencies

- `pandas>=1.3.0`
- `geopandas>=0.10.0`
- `networkx>=2.6.0`
- `pulp>=2.7.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
