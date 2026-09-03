# GEO-INFER-APP

Human-computer interaction layer providing accessible geospatial applications, dashboards, and UI components.

## Contents

- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
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

- `fastapi>=0.100.0`
- `uvicorn>=0.15.0`
- `pydantic>=2.0.0`
- `jsonschema>=4.0.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module APP
```


## Visualization Contracts

- Agent map features validate finite longitude/latitude values and geographic
  bounds, and normalize metadata to JSON-safe values.
- Active-inference prediction and reinforcement-learning reward series are
  exposed in dashboard widgets when present in agent metadata.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
