# GEO-INFER-API/src/geo_infer_api

Geo Infer Api workspace within `GEO-INFER-API`.

## Contents

- `core/`
- `endpoints/`
- `models/`
- `utils/`
- `__init__.py`
- `app.py`

## Public Interface

- `app.py:cors_allow_credentials` (function)
- `app.py:create_app` (function)

## Module Metadata

- Module: `GEO-INFER-API`
- Package: `geo_infer_api`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-API`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module API`

## Dependencies

- `fastapi>=0.100.0`
- `uvicorn>=0.21.0,<0.22.0`
- `pydantic>=2.0.0`
- `pydantic-settings>=2.0.0,<3.0.0`
- `python-dotenv>=1.0.0,<2.0.0`
- `python-multipart>=0.0.6,<0.1.0`
- `httpx>=0.24.0,<0.25.0`
- `pytest>=7.3.1,<7.4.0`
- `pytest-cov>=4.1.0,<4.2.0`
- `requests>=2.28.2,<2.29.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module API
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
