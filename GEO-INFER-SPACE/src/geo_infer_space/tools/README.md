# GEO-INFER-SPACE/src/geo_infer_space/tools

Tools workspace within `GEO-INFER-SPACE`.

## Contents

- `fix_double_h3.py`
- `fix_h3_calls.py`
- `fix_h3_v4_api.py`
- `fix_imports.py`
- `fix_relative_imports.py`
- `run_h3_tests_simple.py`
- `verify_h3_v4_compliance.py`

## Public Interface

- `fix_double_h3.py:fix_double_h3_lib` (function)
- `fix_h3_calls.py:fix_h3_calls_in_file` (function)
- `fix_h3_v4_api.py:fix_h3_v3_api_calls` (function)
- `fix_imports.py:fix_imports_in_file` (function)
- `fix_relative_imports.py:fix_relative_imports_in_file` (function)
- `run_h3_tests_simple.py:main` (function)
- `verify_h3_v4_compliance.py:check_file_for_v3_api` (function)
- `verify_h3_v4_compliance.py:check_file_for_v4_api` (function)

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
