# GEO-INFER-SEC/src/geo_infer_sec/api

Api workspace within `GEO-INFER-SEC`.

## Contents

- `__init__.py`
- `security_api.py`

## Public Interface

- `security_api.py:init_security_api` (function)
- `security_api.py:token_required` (function)
- `security_api.py:get_token` (function)
- `security_api.py:get_roles` (function)
- `security_api.py:anonymize_data` (function)
- `security_api.py:check_location_access` (function)
- `security_api.py:check_compliance` (function)
- `security_api.py:filter_data` (function)

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
