# GEO-INFER-SPACE/tests

Tests workspace within `GEO-INFER-SPACE`.

## Contents

- `integration/`
- `reports/`
- `test_output/`
- `tools/`
- `unit/`
- `conftest.py`
- `h3_v4_framework_upgrade.py`
- `run_h3_tests.py`
- `run_tests_in_order.py`

## Public Interface

- `conftest.py:reset_and_reinstall_venvs` (function)
- `conftest.py:pytest_collection_modifyitems` (function)
- `conftest.py:test_data_dir` (function)
- `conftest.py:sample_geojson` (function)
- `conftest.py:setup_repo_environment` (function)
- `h3_v4_framework_upgrade.py:H3V4FrameworkUpgrader` (class)
- `h3_v4_framework_upgrade.py:main` (function)
- `run_h3_tests.py:run_tests` (function)
- `run_h3_tests.py:run_specific_test` (function)
- `run_h3_tests.py:run_all_tests` (function)
- `run_h3_tests.py:run_performance_tests` (function)
- `run_h3_tests.py:run_integration_tests` (function)
- `run_h3_tests.py:main` (function)
- `run_tests_in_order.py:run_test_category` (function)
- `run_tests_in_order.py:run_all_tests` (function)
- `run_tests_in_order.py:run_all_tests_in_order` (function)
- `run_tests_in_order.py:get_category_description` (function)
- `run_tests_in_order.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python -m pytest GEO-INFER-SPACE/tests`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`


## Strict Test Inventory

- Purpose: validate the `GEO-INFER-SPACE` module's current behavior through unit,
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
  GEO-INFER-SPACE/tests`, followed by
  `uv run python GEO-INFER-TEST/validate_test_contracts.py --strict`.

## Validation

```bash
uv run python -m pytest GEO-INFER-SPACE/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
