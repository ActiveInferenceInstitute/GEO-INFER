# GEO-INFER-AI

Advanced machine learning and artificial intelligence capabilities specifically designed for geospatial analysis and decision-making.

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

- Module: `GEO-INFER-AI`
- Package: `geo_infer_ai`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AI`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module AI`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `torch>=1.9.0`
- `tensorflow>=2.6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AI
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
