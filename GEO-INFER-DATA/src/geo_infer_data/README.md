# GEO-INFER-DATA/src/geo_infer_data

Geo Infer Data workspace within `GEO-INFER-DATA`.

## Contents

- `api/`
- `connectors/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`

## Public Interface

- `__init__.py:initialize_data_system` (function)
- `__init__.py:validate_data_integrity` (function)
- `__init__.py:optimize_storage_performance` (function)

## Module Metadata

- Module: `GEO-INFER-DATA`
- Package: `geo_infer_data`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-DATA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module DATA`

## Dependencies

- `geopandas>=0.13.0`
- `pandas>=2.0.0`
- `numpy>=1.24.0`
- `shapely>=2.0.0`
- `rasterio>=1.3.0`
- `fiona>=1.9.0`
- `pyproj>=3.5.0`
- `scipy>=1.10.0`
- `scikit-learn>=1.3.0`
- `pyyaml>=6.0.0`
- `openpyxl>=3.1.0`
- `xlrd>=2.0.1`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module DATA
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
