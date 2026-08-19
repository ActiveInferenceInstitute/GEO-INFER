# GEO-INFER-BAYES/src/geo_infer_bayes/models

Models workspace within `GEO-INFER-BAYES`.

## Contents

- `__init__.py`
- `_model_utils.py`
- `base.py`
- `bayesian_network.py`
- `bayesian_timeseries.py`
- `dirichlet_process.py`
- `dynamic_spatial.py`
- `hierarchical.py`
- `multilevel.py`
- `spatial_causal.py`
- `spatial_clustering.py`
- `spatial_gp.py`
- `spatiotemporal_gp.py`

## Public Interface

- `_model_utils.py:observations_from` (function)
- `_model_utils.py:features_from` (function)
- `_model_utils.py:signal_from` (function)
- `_model_utils.py:posterior_values` (function)
- `_model_utils.py:posterior_vector` (function)
- `_model_utils.py:scalar_parameter` (function)
- `_model_utils.py:parameter_array` (function)
- `_model_utils.py:gaussian_log_likelihood` (function)
- `_model_utils.py:log_prior_from_parameters` (function)
- `_model_utils.py:predictive_samples` (function)
- `_model_utils.py:posterior_draw_indices` (function)
- `base.py:BayesianModel` (class)
- `bayesian_network.py:BayesianNetwork` (class)
- `bayesian_timeseries.py:BayesianTimeSeriesModel` (class)
- `dirichlet_process.py:DirichletProcessMixture` (class)
- `dynamic_spatial.py:DynamicSpatialModel` (class)
- `hierarchical.py:HierarchicalBayesianModel` (class)
- `multilevel.py:MultilevelModel` (class)
- `spatial_causal.py:SpatialCausalModel` (class)
- `spatial_clustering.py:SpatialClusteringModel` (class)

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
