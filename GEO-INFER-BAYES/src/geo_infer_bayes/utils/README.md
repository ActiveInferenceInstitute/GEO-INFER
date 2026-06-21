# GEO-INFER-BAYES/src/geo_infer_bayes/utils

Utils workspace within `GEO-INFER-BAYES`.

## Contents

- `__init__.py`
- `data_processing.py`
- `diagnostics.py`
- `likelihoods.py`
- `priors.py`
- `visualization.py`

## Public Interface

- `data_processing.py:prepare_spatial_data` (function)
- `data_processing.py:load_geospatial_data` (function)
- `data_processing.py:validate_spatial_data` (function)
- `data_processing.py:create_spatial_grid` (function)
- `data_processing.py:sample_spatial_data` (function)
- `data_processing.py:save_processed_data` (function)
- `diagnostics.py:mcmc_diagnostics` (function)
- `diagnostics.py:convergence_metrics` (function)
- `likelihoods.py:SpatialLikelihood` (class)
- `likelihoods.py:PoissonProcess` (class)
- `likelihoods.py:GaussianLikelihood` (class)
- `priors.py:SpatialPrior` (class)
- `priors.py:TemporalPrior` (class)
- `priors.py:GaussianProcessPrior` (class)
- `visualization.py:plot_posterior` (function)
- `visualization.py:plot_spatial_prediction` (function)
- `visualization.py:plot_uncertainty` (function)
- `visualization.py:plot_model_comparison` (function)

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
