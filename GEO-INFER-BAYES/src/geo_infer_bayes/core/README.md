# GEO-INFER-BAYES/src/geo_infer_bayes/core

Core workspace within `GEO-INFER-BAYES`.

## Contents

- `__init__.py`
- `abc.py`
- `hmc.py`
- `inference.py`
- `mcmc.py`
- `model_comparison.py`
- `posterior.py`
- `smc.py`
- `variational.py`

## Public Interface

- `abc.py:ApproximateBayesianComputation` (class)
- `hmc.py:HMC` (class)
- `inference.py:BayesianInference` (class)
- `mcmc.py:MCMC` (class)
- `model_comparison.py:ModelComparison` (class)
- `posterior.py:PosteriorAnalysis` (class)
- `smc.py:SequentialMonteCarlo` (class)
- `variational.py:VariationalInference` (class)

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
