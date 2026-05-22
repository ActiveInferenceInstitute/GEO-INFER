# GEO-INFER-CLIMATE/src

Src workspace within `GEO-INFER-CLIMATE`.

## Contents

- `geo_infer_climate.egg-info/`
- `geo_infer_climate/`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-CLIMATE`
- Package: `geo_infer_climate`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-CLIMATE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module CLIMATE`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `netcdf4>=1.5.8`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module CLIMATE
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
