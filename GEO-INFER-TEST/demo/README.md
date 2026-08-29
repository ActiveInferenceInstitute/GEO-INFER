# GEO-INFER-TEST/demo

Demo workspace within `GEO-INFER-TEST`.

## Contents

- `__init__.py`
- `crescent_city_civic_intel_demo.py`
- `test_crescent_city_civic_intel_demo.py`

## Public Interface

- `crescent_city_civic_intel_demo.py:bundled_contract_path` (function)
- `crescent_city_civic_intel_demo.py:load_bundled_contract` (function)
- `crescent_city_civic_intel_demo.py:geo_views_agree` (function)
- `crescent_city_civic_intel_demo.py:build_iso_geo_parity` (function)
- `crescent_city_civic_intel_demo.py:build_geo_parity` (function)
- `crescent_city_civic_intel_demo.py:build_summary` (function)
- `crescent_city_civic_intel_demo.py:render_summary` (function)
- `crescent_city_civic_intel_demo.py:main` (function)

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
- `h3>=4.5.0,<5`
- `hypothesis>=6.0.0`
- `jinja2>=3.1.0`
- `jsonschema>=4.0.0`
- `locust>=2.0.0`
- `matplotlib>=3.5.0`
- `memory-profiler>=0.60.0`
- `numpy>=1.20.0`


## Validation

```bash
uv sync --all-packages --all-extras
uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
