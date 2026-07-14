# GEO-INFER-ANT/tests

Tests workspace within `GEO-INFER-ANT`.

## Contents

- `integration/`
- `performance/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:pytest_configure` (function)
- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:distance_matrix` (function)
- `conftest.py:pheromone_grid` (function)
- `conftest.py:ant_colony_config` (function)

## Module Metadata

- Module: `GEO-INFER-ANT`
- Package: `geo_infer_ant`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ANT`
- Tests: `uv run python -m pytest GEO-INFER-ANT/tests`

## Dependencies

- `aiomqtt>=2.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `jsonschema>=4.0.0`
- `matplotlib>=3.5.0`
- `networkx>=2.8`
- `numpy>=1.21.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.1.0`
- `scipy>=1.7.0`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-ANT` module's current behavior through unit,
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
  GEO-INFER-ANT/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-ANT/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
