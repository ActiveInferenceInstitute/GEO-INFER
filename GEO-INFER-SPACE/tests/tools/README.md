# GEO-INFER-SPACE/tests/tools

Tools workspace within `GEO-INFER-SPACE`.

## Contents

- `conftest.py`
- `test_fix_double_h3.py`
- `test_fix_h3_calls.py`
- `test_fix_h3_v4_api.py`
- `test_fix_imports.py`
- `test_fix_relative_imports.py`
- `test_run_h3_tests_simple.py`
- `test_verify_h3_v4_compliance.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python -m pytest GEO-INFER-SPACE/tests/tools`

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
uv run python -m pytest GEO-INFER-SPACE/tests/tools
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
