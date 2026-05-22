# GEO-INFER-TEST/tests

Tests workspace within `GEO-INFER-TEST`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:PerformanceMonitor` (class)
- `conftest.py:test_data_dir` (function)
- `conftest.py:sample_geojson` (function)
- `conftest.py:sample_h3_indices` (function)
- `conftest.py:sample_time_series` (function)
- `conftest.py:sample_remote_sensing` (function)
- `conftest.py:sample_iot_data` (function)
- `conftest.py:sample_health_data` (function)
- `conftest.py:sample_economic_data` (function)
- `conftest.py:sample_agricultural_data` (function)
- `conftest.py:sample_logistics_data` (function)
- `conftest.py:sample_bioinformatics_data` (function)
- `conftest.py:performance_monitor` (function)
- `conftest.py:test_config` (function)
- `conftest.py:mock_external_apis` (function)
- `conftest.py:spatial_test_data` (function)
- `conftest.py:temporal_test_data` (function)
- `conftest.py:pytest_configure` (function)
- `conftest.py:pytest_collection_modifyitems` (function)
- `conftest.py:pytest_terminal_summary` (function)

## Module Metadata

- Module: `GEO-INFER-TEST`
- Package: `geo_infer_test`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TEST`
- Tests: `uv run python -m pytest GEO-INFER-TEST/tests`

## Dependencies

- `coverage[toml]>=7.0.0`
- `factory-boy>=3.2.0`
- `faker>=18.0.0`
- `geopandas>=0.10.0`
- `hypothesis>=6.0.0`
- `jinja2>=3.1.0`
- `jsonschema>=4.0.0`
- `locust>=2.0.0`
- `matplotlib>=3.5.0`
- `memory-profiler>=0.60.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-TEST/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
