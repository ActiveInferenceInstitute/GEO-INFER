# GEO-INFER-TEST/src/geo_infer_test

Geo Infer Test workspace within `GEO-INFER-TEST`.

## Contents

- `api/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`
- `testing.py`

## Public Interface

- `testing.py:as_finite_array` (function)
- `testing.py:assert_finite` (function)
- `testing.py:assert_probability` (function)
- `testing.py:assert_stochastic_matrix` (function)
- `testing.py:assert_same_finite_values` (function)
- `testing.py:assert_no_nan_statistics` (function)
- `testing.py:assert_model_contract` (function)
- `testing.py:assert_seed_replay` (function)
- `testing.py:assert_visualization_manifest` (function)
- `testing.py:LocalService` (class)
- `testing.py:deterministic_rng` (function)
- `testing.py:local_filesystem` (function)
- `testing.py:sqlite_database` (function)
- `testing.py:local_http_server` (function)
- `testing.py:local_service` (function)

## Module Metadata

- Module: `GEO-INFER-TEST`
- Package: `geo_infer_test`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TEST`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
