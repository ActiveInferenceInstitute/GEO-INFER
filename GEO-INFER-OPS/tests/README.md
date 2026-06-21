# GEO-INFER-OPS/tests

Tests workspace within `GEO-INFER-OPS`.

## Contents

- `integration/`
- `unit/`
- `__init__.py`
- `conftest.py`
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

- `pyyaml>=6.0`
- `fastapi>=0.100.0`
- `uvicorn>=0.21.0`
- `prometheus-client>=0.16.0`
- `structlog>=23.1.0`
- `pytest>=7.3.1`
- `docker>=6.0.1`
- `kubernetes>=26.1.0`
- `black>=23.3.0`
- `isort>=5.12.0`
- `flake8>=6.0.0`
- `pytest-cov>=4.1.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-OPS/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
