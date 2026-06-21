# GEO-INFER-SPM/tests

Tests workspace within `GEO-INFER-SPM`.

## Contents

- `integration/`
- `performance/`
- `unit/`
- `conftest.py`
- `requirements-test.txt`
- `run_tests.sh`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:spatial_model_params` (function)
- `conftest.py:latent_variables` (function)
- `conftest.py:spm_config` (function)
- `conftest.py:synthetic_spm_data` (function)

## Module Metadata

- Module: `GEO-INFER-SPM`
- Package: `geo_infer_spm`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPM`
- Tests: `uv run python -m pytest GEO-INFER-SPM/tests`

## Dependencies

- `numpy>=1.20.0`
- `scipy>=1.7.0`
- `pandas>=1.3.0`
- `geopandas>=0.10.0`
- `xarray>=0.20.0`
- `scikit-learn>=1.0.0`
- `matplotlib>=3.5.0`
- `plotly>=5.0.0`
- `h5py>=3.6.0`
- `rasterio>=1.2.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-SPM/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
