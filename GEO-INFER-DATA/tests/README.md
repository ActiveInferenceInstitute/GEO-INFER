# GEO-INFER-DATA/tests

Tests workspace within `GEO-INFER-DATA`.

## Contents

- `fixtures/`
- `integration/`
- `performance/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:ensure_event_loop` (function)
- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:sample_csv_path` (function)
- `conftest.py:sample_geojson_path` (function)
- `conftest.py:data_source_config` (function)

## Module Metadata

- Module: `GEO-INFER-DATA`
- Package: `geo_infer_data`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-DATA`
- Tests: `uv run python -m pytest GEO-INFER-DATA/tests`

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
uv run python -m pytest GEO-INFER-DATA/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
