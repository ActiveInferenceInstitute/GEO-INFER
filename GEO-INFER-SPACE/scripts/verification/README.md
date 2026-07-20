# GEO-INFER-SPACE/scripts/verification

Verification workspace within `GEO-INFER-SPACE`.

## Contents

- `test_core_functionality.py`
- `test_h3_basic.py`
- `test_multiple_dispatch_comprehensive.py`
- `test_refactored_structure.py`
- `verify_installation.py`

## Public Interface

- `verify_installation.py:test_core_imports` (function)
- `verify_installation.py:test_h3_functionality` (function)
- `verify_installation.py:test_vector_operations` (function)
- `verify_installation.py:test_data_models` (function)
- `verify_installation.py:test_api_schemas` (function)
- `verify_installation.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.100.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=2.0.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=2.0.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
