# GEO-INFER-COMMS

Communications infrastructure for geospatial systems enabling data exchange, messaging, networking, and outreach across distributed applications.

## Contents

- `.pytest_cache/`
- `config/`
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

- Module: `GEO-INFER-COMMS`
- Package: `geo_infer_comms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-COMMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS`

## Dependencies

- `fastapi>=0.68.0`
- `pydantic>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module COMMS
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
