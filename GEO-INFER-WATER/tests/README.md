# GEO-INFER-WATER/tests

Tests workspace within `GEO-INFER-WATER`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_water_quality.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:watershed_gdf` (function)
- `conftest.py:streamflow_series` (function)
- `conftest.py:water_quality_data` (function)

## Module Metadata

- Module: `GEO-INFER-WATER`
- Package: `geo_infer_water`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-WATER`
- Tests: `uv run python -m pytest GEO-INFER-WATER/tests`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-WATER/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
