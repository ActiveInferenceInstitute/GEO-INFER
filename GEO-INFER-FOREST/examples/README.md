# GEO-INFER-FOREST/examples

Examples workspace within `GEO-INFER-FOREST`.

## Contents

- `__init__.py`
- `basic_forest_analysis.py`
- `wildfire_risk_management.py`

## Public Interface

- `basic_forest_analysis.py:main` (function)
- `wildfire_risk_management.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-FOREST`
- Package: `geo_infer_forest`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-FOREST`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module FOREST`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module FOREST
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
