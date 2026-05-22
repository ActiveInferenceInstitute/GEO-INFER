# GEO-INFER-OPS/src/geo_infer_ops/utils

Utils workspace within `GEO-INFER-OPS`.

## Contents

- `__init__.py`
- `config.py`
- `error_handling.py`
- `logger.py`
- `shared_logging.py`

## Public Interface

- `config.py:find_config_file` (function)
- `config.py:load_config` (function)
- `error_handling.py:ErrorSeverity` (class)
- `error_handling.py:ErrorCategory` (class)
- `error_handling.py:GeoInferError` (class)
- `error_handling.py:NetworkError` (class)
- `error_handling.py:AuthenticationError` (class)
- `error_handling.py:PermissionError` (class)
- `error_handling.py:FilesystemError` (class)
- `error_handling.py:ConfigurationError` (class)
- `error_handling.py:ValidationError` (class)
- `error_handling.py:ProcessingError` (class)
- `error_handling.py:DataError` (class)
- `error_handling.py:RetryConfig` (class)
- `error_handling.py:classify_error` (function)
- `error_handling.py:handle_error` (function)
- `error_handling.py:retry_on_error` (function)
- `error_handling.py:with_error_handling` (function)
- `logger.py:configure_logging` (function)
- `logger.py:get_logger` (function)

## Module Metadata

- Module: `GEO-INFER-OPS`
- Package: `geo_infer_ops`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-OPS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module OPS`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module OPS
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
