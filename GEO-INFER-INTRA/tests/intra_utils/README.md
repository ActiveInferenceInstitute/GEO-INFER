# GEO-INFER-INTRA/tests/intra_utils

Intra Utils workspace within `GEO-INFER-INTRA`.

## Contents

- `__init__.py`
- `geospatial.py`
- `time_series.py`

## Public Interface

- `__init__.py:collect_test_modules` (function)
- `__init__.py:import_module_by_path` (function)
- `__init__.py:find_modules_by_name` (function)
- `geospatial.py:create_point` (function)
- `geospatial.py:create_bbox` (function)
- `geospatial.py:create_polygon` (function)
- `geospatial.py:create_feature` (function)
- `geospatial.py:create_feature_collection` (function)
- `geospatial.py:is_valid_geojson` (function)
- `geospatial.py:load_geojson_file` (function)
- `geospatial.py:save_geojson_file` (function)
- `geospatial.py:haversine_distance` (function)
- `geospatial.py:create_sample_h3_data` (function)
- `time_series.py:create_iso8601_timestamp` (function)
- `time_series.py:create_timestamp_range` (function)
- `time_series.py:create_daily_timestamps` (function)
- `time_series.py:create_hourly_timestamps` (function)
- `time_series.py:create_time_series_data` (function)
- `time_series.py:random_walk_generator` (function)
- `time_series.py:seasonal_generator` (function)

## Module Metadata

- Module: `GEO-INFER-INTRA`
- Package: `geo_infer_intra`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-INTRA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA`

## Dependencies

- `fastapi>=0.100.0`
- `h3>=4.5.0,<5`
- `pydantic>=2.0.0`
- `sqlalchemy>=2.0.0`
- `elasticsearch>=8.0.0`
- `rdflib>=6.0.0`
- `mkdocs>=1.4.0`
- `celery>=5.2.0`
- `pyyaml>=6.0`
- `jsonschema>=4.0.0`
- `typer>=0.7.0`
- `rich>=12.0.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
