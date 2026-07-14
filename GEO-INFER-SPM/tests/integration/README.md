# GEO-INFER-SPM/tests/integration

Integration workspace within `GEO-INFER-SPM`.

## Contents

- `test_correctness.py`
- `test_full_pipeline.py`
- `test_real_data.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-SPM`
- Package: `geo_infer_spm`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPM`
- Tests: `uv run python -m pytest GEO-INFER-SPM/tests/integration`

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
uv run python -m pytest GEO-INFER-SPM/tests/integration
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
