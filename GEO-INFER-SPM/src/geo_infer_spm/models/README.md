# GEO-INFER-SPM/src/geo_infer_spm/models

Models workspace within `GEO-INFER-SPM`.

## Contents

- `__init__.py`
- `data_models.py`

## Public Interface

- `data_models.py:SPMData` (class)
- `data_models.py:DesignMatrix` (class)
- `data_models.py:ContrastResult` (class)
- `data_models.py:SPMResult` (class)

## Module Metadata

- Module: `GEO-INFER-SPM`
- Package: `geo_infer_spm`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPM`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPM`

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
- `statsmodels>=0.13.0  # Time series analysis`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPM
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
