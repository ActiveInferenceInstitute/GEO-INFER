# GEO-INFER-ENERGY/tests

Tests workspace within `GEO-INFER-ENERGY`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_renewable_resources.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:solar_irradiance_grid` (function)
- `conftest.py:wind_speed_grid` (function)
- `conftest.py:energy_config` (function)

## Module Metadata

- Module: `GEO-INFER-ENERGY`
- Package: `geo_infer_energy`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ENERGY`
- Tests: `uv run python -m pytest GEO-INFER-ENERGY/tests`

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
uv run python -m pytest GEO-INFER-ENERGY/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
