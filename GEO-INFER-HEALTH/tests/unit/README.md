# GEO-INFER-HEALTH/tests/unit

Unit workspace within `GEO-INFER-HEALTH`.

## Contents

- `test_advanced_geospatial.py`
- `test_config.py`
- `test_disease_surveillance.py`
- `test_environmental_health.py`
- `test_geospatial_utils.py`
- `test_healthcare_accessibility.py`
- `test_models.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-HEALTH`
- Package: `geo_infer_health`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-HEALTH`
- Tests: `uv run python -m pytest GEO-INFER-HEALTH/tests/unit`

## Dependencies

- `fastapi>=0.104.0`
- `uvicorn>=0.24.0`
- `pydantic>=2.5.0`
- `pydantic-settings>=2.1.0`
- `geopandas>=0.14.0`
- `shapely>=2.0.0`
- `pyproj>=3.6.0`
- `rasterio>=1.3.0`
- `fiona>=1.9.0`
- `numpy>=1.24.0`
- `scipy>=1.11.0`
- `pandas>=2.1.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-HEALTH/tests/unit
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
