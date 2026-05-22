# GEO-INFER-BAYES/tests

Tests workspace within `GEO-INFER-BAYES`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:gp_kernel_config` (function)
- `conftest.py:mcmc_samples` (function)
- `conftest.py:prior_params` (function)
- `conftest.py:synthetic_spatial_data` (function)

## Module Metadata

- Module: `GEO-INFER-BAYES`
- Package: `geo_infer_bayes`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-BAYES`
- Tests: `uv run python -m pytest GEO-INFER-BAYES/tests`

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
uv run python -m pytest GEO-INFER-BAYES/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
