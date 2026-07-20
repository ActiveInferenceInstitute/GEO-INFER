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

- `fastapi>=0.100.0`
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


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-INTRA` module's current behavior through unit,
  integration, system, and performance test surfaces.
- Primary marker: tests receive exactly one primary marker from their canonical
  directory; additive domain markers remain allowed.
- Required fixtures: local `tests/conftest.py` fixtures and shared
  `geo_infer_test.testing` fixtures for deterministic RNG, filesystem, HTTP,
  SQLite, service, model, and artifact boundaries.
- Dependencies: required test/runtime dependencies are installed by
  `uv sync --all-packages --all-extras`; missing backends are failures.
- Expected artifacts: JUnit XML under `.geo-infer-test-results/`; model and
  visualization outputs require finite statistics, sidecars, hashes, and a
  manifest.
- Failure triage: `env -u VIRTUAL_ENV uv run pytest -c pyproject.toml -q
  GEO-INFER-INTRA/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-INTRA/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
