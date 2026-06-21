# GEO-INFER-PEP/tests

Tests workspace within `GEO-INFER-PEP`.

## Contents

- `core/`
- `integration/`
- `models/`
- `unit/`
- `conftest.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-PEP`
- Package: `geo_infer_pep`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PEP`
- Tests: `uv run python -m pytest GEO-INFER-PEP/tests`

## Dependencies

- `fastapi>=0.100.0`
- `uvicorn[standard]>=0.23.2`
- `pydantic>=2.0`
- `pandas>=2.0`
- `matplotlib>=3.7.0`
- `seaborn>=0.13.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-PEP/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
