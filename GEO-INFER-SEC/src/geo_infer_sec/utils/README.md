# GEO-INFER-SEC/src/geo_infer_sec/utils

Utils workspace within `GEO-INFER-SEC`.

## Contents

- `__init__.py`
- `security_utils.py`

## Public Interface

- `security_utils.py:SecurityConfig` (class)
- `security_utils.py:SecurityUtils` (class)
- `security_utils.py:create_security_utils` (function)
- `security_utils.py:hash_password_simple` (function)
- `security_utils.py:verify_password_simple` (function)

## Module Metadata

- Module: `GEO-INFER-SEC`
- Package: `geo_infer_sec`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SEC`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SEC`

## Dependencies

- `cryptography>=36.0.0`
- `pyjwt>=2.3.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `pandas>=1.3.0`
- `numpy>=1.20.0`
- `pyyaml>=6.0`
- `h3>=4.0.0`
- `pyproj>=3.0.0`
- `flask>=2.0.0`
- `sqlalchemy>=1.4.0`
- `bcrypt>=3.2.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SEC
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
