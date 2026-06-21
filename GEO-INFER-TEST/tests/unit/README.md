# GEO-INFER-TEST/tests/unit

Unit workspace within `GEO-INFER-TEST`.

## Contents

- `test_data_domains.py`
- `test_log_integration.py`
- `test_module_health.py`
- `test_performance_monitor.py`
- `test_run_unified_tests.py`
- `test_spatial_functions.py`
- `test_test_discoverer.py`
- `test_test_orchestrator.py`
- `test_test_runner.py`
- `test_validate_h3_active_inference_contract.py`
- `test_validate_repo_contracts.py`
- `test_validate_skills.py`
- `test_validators.py`
- `test_validators_parametric.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-TEST`
- Package: `geo_infer_test`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TEST`
- Tests: `uv run python -m pytest GEO-INFER-TEST/tests/unit`

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
uv sync --all-packages --all-extras
uv run python -m pytest GEO-INFER-TEST/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
