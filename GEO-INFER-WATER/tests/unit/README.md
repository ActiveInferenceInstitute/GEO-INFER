# GEO-INFER-WATER/tests/unit

Unit workspace within `GEO-INFER-WATER`.

## Contents

- `test_flood_drought.py`
- `test_hydrology.py`
- `test_water_balance.py`
- `test_water_quality.py`
- `test_watershed_delineation.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-WATER`
- Package: `geo_infer_water`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-WATER`
- Tests: `uv run python -m pytest GEO-INFER-WATER/tests/unit`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-WATER/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
