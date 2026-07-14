# GEO-INFER-DATA/tests/unit

Unit workspace within `GEO-INFER-DATA`.

## Contents

- `test_api.py`
- `test_caching.py`
- `test_cloud_connectors.py`
- `test_compression.py`
- `test_error_handling.py`
- `test_file_connector.py`
- `test_format_detection.py`
- `test_geospatial_validation.py`
- `test_indexing.py`
- `test_ingestion.py`
- `test_performance.py`
- `test_pipeline.py`
- `test_schemas.py`
- `test_storage.py`
- `test_stream_connectors.py`
- `test_validation.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-DATA`
- Package: `geo_infer_data`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-DATA`
- Tests: `uv run python -m pytest GEO-INFER-DATA/tests/unit`

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
uv run python -m pytest GEO-INFER-DATA/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
