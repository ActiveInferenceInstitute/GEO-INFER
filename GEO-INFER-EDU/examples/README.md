# GEO-INFER-EDU/examples

Examples workspace within `GEO-INFER-EDU`.

## Contents

- `curriculum_design.py`
- `interactive_learning.py`

## Public Interface

- `curriculum_design.py:main` (function)
- `interactive_learning.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-EDU`
- Package: `geo_infer_edu`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EDU`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module EDU`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `pyyaml>=6.0`
- `pydantic>=2.0.0`
- `jinja2>=3.0.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EDU
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
