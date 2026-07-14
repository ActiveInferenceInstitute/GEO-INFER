# GEO-INFER-LOG/examples

Examples workspace within `GEO-INFER-LOG`.

## Contents

- `basic_routing_example.py`
- `last_mile_delivery.py`

## Public Interface

- `basic_routing_example.py:create_sample_vehicles` (function)
- `basic_routing_example.py:create_sample_destinations` (function)
- `basic_routing_example.py:main` (function)
- `last_mile_delivery.py:main` (function)

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
