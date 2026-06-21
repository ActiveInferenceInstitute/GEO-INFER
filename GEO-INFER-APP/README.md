# GEO-INFER-APP

Human-computer interaction layer providing accessible geospatial applications, dashboards, and UI components.

## Contents

- `.pytest_cache/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-APP`
- Package: `geo_infer_app`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-APP`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module APP`

## Dependencies

- `fastapi>=0.68.0`
- `uvicorn>=0.15.0`
- `pydantic>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module APP
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
