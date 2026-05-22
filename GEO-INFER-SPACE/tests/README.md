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
- `h3>=4.0.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-SPACE/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
