# GEO-INFER-TEST/tests/integration

Integration workspace within `GEO-INFER-TEST`.

## Contents

- `test_act_agent_ant_coordination.py`
- `test_ai_space_domain_integration.py`
- `test_cross_module.py`
- `test_cross_module_workflows.py`
- `test_ecosystem_health.py`
- `test_module_imports.py`
- `test_sec_api_app_security.py`
- `test_space_time_data_integration.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-TEST`
- Package: `geo_infer_test`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TEST`
- Tests: `uv run python -m pytest GEO-INFER-TEST/tests/integration`

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
uv run python -m pytest GEO-INFER-TEST/tests/integration
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
