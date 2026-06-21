# GEO-INFER-LOG/src/geo_infer_log/models

Models workspace within `GEO-INFER-LOG`.

## Contents

- `__init__.py`
- `schemas.py`

## Public Interface

- `schemas.py:VehicleType` (class)
- `schemas.py:FuelType` (class)
- `schemas.py:DeliveryStatus` (class)
- `schemas.py:Vehicle` (class)
- `schemas.py:Location` (class)
- `schemas.py:Shipment` (class)
- `schemas.py:Route` (class)
- `schemas.py:RoutingParameters` (class)
- `schemas.py:FacilityLocation` (class)
- `schemas.py:SupplyChainNetwork` (class)

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
