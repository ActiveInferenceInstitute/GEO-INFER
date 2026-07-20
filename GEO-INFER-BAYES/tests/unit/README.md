# GEO-INFER-BAYES/tests/unit

Unit workspace within `GEO-INFER-BAYES`.

## Contents

- `test_base_model.py`
- `test_data_processing.py`
- `test_diagnostics.py`
- `test_gaussian_process.py`
- `test_inference.py`
- `test_likelihoods.py`
- `test_mcmc.py`
- `test_model_comparison.py`
- `test_model_contracts.py`
- `test_posterior.py`
- `test_priors.py`
- `test_spatial_gp.py`
- `test_variational.py`
- `test_visualization_utils.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-BAYES`
- Package: `geo_infer_bayes`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BAYES`
- Tests: `uv run python -m pytest GEO-INFER-BAYES/tests/unit`

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
uv run python -m pytest GEO-INFER-BAYES/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
