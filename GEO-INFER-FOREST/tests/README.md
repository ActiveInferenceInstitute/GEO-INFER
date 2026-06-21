# GEO-INFER-FOREST/tests

Tests workspace within `GEO-INFER-FOREST`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_wildfire_risk.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:forest_stand_gdf` (function)
- `conftest.py:biomass_allometric_params` (function)
- `conftest.py:forest_config` (function)

## Module Metadata

- Module: `GEO-INFER-FOREST`
- Package: `geo_infer_forest`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-FOREST`
- Tests: `uv run python -m pytest GEO-INFER-FOREST/tests`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-FOREST/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
