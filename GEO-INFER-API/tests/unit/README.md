# GEO-INFER-API/tests/unit

Unit workspace within `GEO-INFER-API`.

## Contents

- `test_algorithms_router.py`
- `test_config.py`
- `test_exceptions.py`
- `test_geojson_helpers.py`
- `test_geojson_helpers_extended.py`
- `test_geojson_router.py`
- `test_geojson_visualization.py`
- `test_middleware.py`
- `test_models_geojson.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-API`
- Package: `geo_infer_api`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-API`
- Tests: `uv run python -m pytest GEO-INFER-API/tests/unit`

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
uv run python -m pytest GEO-INFER-API/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
