# GEO-INFER-INSURANCE

Underwriting, policy, claims, and pricing operations for geospatial insurance workflows within the GEO-INFER framework.

## Contents

- `outputs/`
- `src/`
- `tests/`
- `setup.py`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-INSURANCE`
- Package: `geo_infer_insurance`
- Version: `0.1.0`
- Install: `uv pip install -e ./GEO-INFER-INSURANCE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module INSURANCE`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INSURANCE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
