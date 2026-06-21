# GEO-INFER-REQ

Requirements engineering using P3IF framework for geospatial systems, user stories, and specification management.

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

- Module: `GEO-INFER-REQ`
- Package: `geo_infer_req`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-REQ`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module REQ`

## Dependencies

- `pydantic>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module REQ
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
