# GEO-INFER-OPS/src/geo_infer_ops/core/backup

Backup workspace within `GEO-INFER-OPS`.

## Contents

- `config.py`
- `logging.py`
- `monitoring.py`
- `security.py`
- `testing.py`

## Public Interface

- `config.py:LoggingConfig` (class)
- `config.py:MonitoringConfig` (class)
- `config.py:TestingConfig` (class)
- `config.py:DockerConfig` (class)
- `config.py:KubernetesConfig` (class)
- `config.py:DeploymentConfig` (class)
- `config.py:TLSConfig` (class)
- `config.py:AuthConfig` (class)
- `config.py:SecurityConfig` (class)
- `config.py:Config` (class)
- `config.py:load_config` (function)
- `config.py:get_config` (function)
- `config.py:update_config` (function)
- `logging.py:configure_stdlib_logging` (function)
- `logging.py:setup_logging` (function)
- `logging.py:get_logger` (function)
- `monitoring.py:reset_metrics` (function)
- `monitoring.py:record_request` (function)
- `monitoring.py:record_error` (function)
- `monitoring.py:record_metric` (function)

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
