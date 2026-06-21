# GEO-INFER-OPS/config

Config workspace within `GEO-INFER-OPS`.

## Contents

- `example.yaml`
- `local.yaml`

## Public Interface

- No public Python symbols are defined directly in this directory.

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
