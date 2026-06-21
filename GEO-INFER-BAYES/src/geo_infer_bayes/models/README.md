# GEO-INFER-BAYES/src/geo_infer_bayes/models

Models workspace within `GEO-INFER-BAYES`.

## Contents

- `__init__.py`
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

- `base.py:BayesianModel` (class)
- `bayesian_network.py:BayesianNetwork` (class)
- `bayesian_timeseries.py:BayesianTimeSeriesModel` (class)
- `dirichlet_process.py:DirichletProcessMixture` (class)
- `dynamic_spatial.py:DynamicSpatialModel` (class)
- `hierarchical.py:HierarchicalBayesianModel` (class)
- `multilevel.py:MultilevelModel` (class)
- `spatial_causal.py:SpatialCausalModel` (class)
- `spatial_clustering.py:SpatialClusteringModel` (class)
- `spatial_gp.py:SpatialGP` (class)
- `spatiotemporal_gp.py:SpatioTemporalConfig` (class)
- `spatiotemporal_gp.py:SpatioTemporalGP` (class)
- `spatiotemporal_gp.py:create_spatiotemporal_gp` (function)

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
