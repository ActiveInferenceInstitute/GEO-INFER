# GEO-INFER-INTRA/tests

Tests workspace within `GEO-INFER-INTRA`.

## Contents

- `integration/`
- `intra_utils/`
- `performance/`
- `system/`
- `unit/`
- `utils/`
- `conftest.py`
- `run_tests.py`

## Public Interface

- `conftest.py:LoggingConfig` (class)
- `conftest.py:Config` (class)
- `conftest.py:load_config` (function)
- `conftest.py:setup_logging` (function)
- `conftest.py:test_env` (function)
- `conftest.py:temp_dir` (function)
- `conftest.py:test_log_dir` (function)
- `conftest.py:test_config_dir` (function)
- `conftest.py:test_data_dir` (function)
- `conftest.py:test_config_factory` (function)
- `conftest.py:test_config_file_factory` (function)
- `conftest.py:test_geojson_point` (function)
- `conftest.py:test_geojson_polygon` (function)
- `conftest.py:test_geojson_feature` (function)
- `conftest.py:test_geojson_feature_collection` (function)
- `conftest.py:test_h3_indexes` (function)
- `conftest.py:test_time_series_data` (function)
- `conftest.py:space_config_file` (function)
- `conftest.py:time_config_file` (function)
- `conftest.py:api_config_file` (function)

## Module Metadata

- Module: `GEO-INFER-INTRA`
- Package: `geo_infer_intra`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-INTRA`
- Tests: `uv run python -m pytest GEO-INFER-INTRA/tests`

## Dependencies

- `fastapi>=0.95.0`
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
- `uvicorn>=0.20.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-INTRA/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
