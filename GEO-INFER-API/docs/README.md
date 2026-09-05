# GEO-INFER-API/docs

Docs workspace within `GEO-INFER-API`.

## Contents

- `algorithms_api.md`
- `geojson_api.md`
- `openapi_spec.yaml`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-API`
- Package: `geo_infer_api`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-API`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module API`

## Dependencies

- `fastapi>=0.100.0`
- `httpx>=0.24.0`
- `pydantic>=2.0.0`
- `pydantic-settings>=2.0.0`
- `python-dotenv>=1.0.0`
- `python-multipart>=0.0.6`
- `requests>=2.28.2`
- `uvicorn>=0.21.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module API
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
