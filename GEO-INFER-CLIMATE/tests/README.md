# GEO-INFER-CLIMATE/tests

Tests workspace within `GEO-INFER-CLIMATE`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_extreme_events.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:temperature_time_series` (function)
- `conftest.py:climate_grid` (function)
- `conftest.py:reference_period_data` (function)

## Module Metadata

- Module: `GEO-INFER-CLIMATE`
- Package: `geo_infer_climate`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-CLIMATE`
- Tests: `uv run python -m pytest GEO-INFER-CLIMATE/tests`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `netcdf4>=1.5.8`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`
- `h3>=4.5.0,<5`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-CLIMATE` module's current behavior through unit,
  integration, system, and performance test surfaces.
- Primary marker: tests receive exactly one primary marker from their canonical
  directory; additive domain markers remain allowed.
- Required fixtures: local `tests/conftest.py` fixtures and shared
  `geo_infer_test.testing` fixtures for deterministic RNG, filesystem, HTTP,
  SQLite, service, model, and artifact boundaries.
- Dependencies: required test/runtime dependencies are installed by
  `uv sync --all-packages --all-extras`; missing backends are failures.
- Expected artifacts: JUnit XML under `.geo-infer-test-results/`; model and
  visualization outputs require finite statistics, sidecars, hashes, and a
  manifest.
- Failure triage: `env -u VIRTUAL_ENV uv run pytest -c pyproject.toml -q
  GEO-INFER-CLIMATE/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-CLIMATE/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
