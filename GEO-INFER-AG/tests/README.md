# GEO-INFER-AG/tests

Tests workspace within `GEO-INFER-AG`.

## Contents

- `data/`
- `integration/`
- `performance/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:sample_field_data` (function)
- `conftest.py:sample_soil_data` (function)
- `conftest.py:sample_weather_data` (function)
- `conftest.py:sample_management_data` (function)
- `conftest.py:sample_time_series_data` (function)
- `conftest.py:management_practices` (function)

## Module Metadata

- Module: `GEO-INFER-AG`
- Package: `geo_infer_ag`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AG`
- Tests: `uv run python -m pytest GEO-INFER-AG/tests`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `scikit-learn>=1.0.0`
- `rasterio>=1.2.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-AG/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
