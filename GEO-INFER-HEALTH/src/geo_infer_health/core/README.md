# GEO-INFER-HEALTH/src/geo_infer_health/core

Core workspace within `GEO-INFER-HEALTH`.

## Contents

- `__init__.py`
- `disease_surveillance.py`
- `enhanced_disease_surveillance.py`
- `environmental_health.py`
- `healthcare_accessibility.py`

## Public Interface

- `disease_surveillance.py:DiseaseHotspotAnalyzer` (class)
- `enhanced_disease_surveillance.py:ActiveInferenceDiseaseAnalyzer` (class)
- `environmental_health.py:EnvironmentalHealthAnalyzer` (class)
- `healthcare_accessibility.py:HealthcareAccessibilityAnalyzer` (class)

## Module Metadata

- Module: `GEO-INFER-HEALTH`
- Package: `geo_infer_health`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-HEALTH`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module HEALTH`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module HEALTH
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
