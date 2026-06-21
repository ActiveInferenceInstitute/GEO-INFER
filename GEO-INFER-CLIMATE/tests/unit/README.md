# GEO-INFER-CLIMATE/tests/unit

Unit workspace within `GEO-INFER-CLIMATE`.

## Contents

- `test_classification.py`
- `test_climate_data.py`
- `test_climate_indices.py`
- `test_extreme_events.py`
- `test_precipitation_analysis.py`
- `test_temperature_trends.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-CLIMATE`
- Package: `geo_infer_climate`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-CLIMATE`
- Tests: `uv run python -m pytest GEO-INFER-CLIMATE/tests/unit`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `netcdf4>=1.5.8`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-CLIMATE/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
