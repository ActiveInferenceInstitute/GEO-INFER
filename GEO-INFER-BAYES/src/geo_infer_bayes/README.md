# GEO-INFER-BAYES/src/geo_infer_bayes

Geo Infer Bayes workspace within `GEO-INFER-BAYES`.

## Contents

- `api/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`

## Public Interface

- `__init__.py:GaussianProcess` (class)

## Module Metadata

- Module: `GEO-INFER-BAYES`
- Package: `geo_infer_bayes`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BAYES`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module BAYES`

## Dependencies

- `arviz`
- `cmdstanpy`
- `geopandas`
- `matplotlib`
- `numpy`
- `pandas`
- `pymc`
- `rasterio`
- `scipy`
- `tensorflow-probability`
- `xarray`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module BAYES
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
