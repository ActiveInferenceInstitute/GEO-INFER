# GEO-INFER-EMERGENCY/examples

Examples workspace within `GEO-INFER-EMERGENCY`.

## Contents

- `emergency_response_simulation.py`
- `multi_hazard_assessment.py`

## Public Interface

- `emergency_response_simulation.py:main` (function)
- `multi_hazard_assessment.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-EMERGENCY`
- Package: `geo_infer_emergency`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EMERGENCY`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module EMERGENCY`

## Dependencies

- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EMERGENCY
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
