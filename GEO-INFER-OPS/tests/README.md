# GEO-INFER-OPS/tests

Tests workspace within `GEO-INFER-OPS`.

## Contents

- `integration/`
- `unit/`
- `__init__.py`
- `conftest.py`
- `test_acceptance_ops.py`
- `test_cache.py`
- `test_config.py`
- `test_deployment.py`
- `test_framework.py`
- `test_logging.py`
- `test_monitoring.py`
- `test_security.py`
- `test_testing.py`

## Public Interface

- `conftest.py:test_dir` (function)
- `conftest.py:temp_dir` (function)
- `conftest.py:mock_config_dict` (function)
- `conftest.py:config` (function)
- `conftest.py:mock_app` (function)
- `conftest.py:test_client` (function)
- `conftest.py:test_registry` (function)
- `conftest.py:mock_redis` (function)
- `conftest.py:test_logger` (function)

## Module Metadata

- Module: `GEO-INFER-OPS`
- Package: `geo_infer_ops`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-OPS`
- Tests: `uv run python -m pytest GEO-INFER-OPS/tests`

## Dependencies

- `fastapi>=0.100.0`
- `prometheus-client>=0.16.0`
- `prometheus-fastapi-instrumentator>=5.7.0`
- `pydantic>=2.0.0`
- `structlog>=23.1.0`
- `pytest>=7.3.1`
- `pytest-timeout>=2.0.0`
- `kubernetes>=26.1.0`
- `black>=23.3.0`
- `pytest-cov>=4.1.0`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-OPS` module's current behavior through unit,
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
  GEO-INFER-OPS/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-OPS/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
