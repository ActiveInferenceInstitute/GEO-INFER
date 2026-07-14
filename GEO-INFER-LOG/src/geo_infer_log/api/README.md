# GEO-INFER-LOG/src/geo_infer_log/api

Api workspace within `GEO-INFER-LOG`.

## Contents

- `__init__.py`
- `delivery.py`
- `routes.py`
- `supply_chain.py`
- `transport.py`

## Public Interface

- `delivery.py:DeliveryOptimizationRequest` (class)
- `delivery.py:ScheduleRequest` (class)
- `delivery.py:ServiceAreaRequest` (class)
- `delivery.py:CoverageAnalysisRequest` (class)
- `delivery.py:RescheduleRequest` (class)
- `delivery.py:get_last_mile_router` (function)
- `delivery.py:get_delivery_scheduler` (function)
- `delivery.py:get_service_area_analyzer` (function)
- `delivery.py:optimize_deliveries` (function)
- `delivery.py:create_schedule` (function)
- `delivery.py:get_daily_schedule` (function)
- `delivery.py:get_vehicle_schedule` (function)
- `delivery.py:reschedule_delivery` (function)
- `delivery.py:create_service_area` (function)
- `delivery.py:analyze_coverage` (function)
- `routes.py:RouteRequest` (class)
- `routes.py:VehicleRegistration` (class)
- `routes.py:VRPRequest` (class)
- `routes.py:get_route_optimizer` (function)
- `routes.py:get_fleet_manager` (function)

## Module Metadata

- Module: `GEO-INFER-LOG`
- Package: `geo_infer_log`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-LOG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG`

## Dependencies

- `pandas>=1.3.0`
- `geopandas>=0.10.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
