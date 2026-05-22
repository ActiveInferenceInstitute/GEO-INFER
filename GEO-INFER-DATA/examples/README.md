# GEO-INFER-DATA/examples

Examples workspace within `GEO-INFER-DATA`.

## Contents

- `api_example.py`
- `basic_ingestion_example.py`
- `etl_pipeline_example.py`
- `storage_example.py`
- `validation_example.py`

## Public Interface

- `api_example.py:DataAPIClient` (class)
- `api_example.py:start_api_server` (function)
- `api_example.py:main` (function)
- `api_example.py:demonstrate_api_usage` (function)
- `basic_ingestion_example.py:main` (function)
- `etl_pipeline_example.py:create_raw_environmental_data` (function)
- `etl_pipeline_example.py:main` (function)
- `etl_pipeline_example.py:demonstrate_pipeline_config` (function)
- `storage_example.py:create_sample_geodataframe` (function)
- `storage_example.py:create_sample_dataframe` (function)
- `storage_example.py:main` (function)

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
