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
- `h3>=4.5.0,<5`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-ENERGY` module's current behavior through unit,
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
  GEO-INFER-ENERGY/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-ENERGY/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
