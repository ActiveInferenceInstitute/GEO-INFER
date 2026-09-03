# GEO-INFER-SEC/tests/unit

Unit workspace within `GEO-INFER-SEC`.

## Contents

- `test_acceptance_sec.py`
- `test_access_control.py`
- `test_audit.py`
- `test_audit_logging.py`
- `test_authentication.py`
- `test_authorization.py`
- `test_encryption.py`
- `test_input_validation.py`
- `test_token_lifecycle.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-SEC`
- Package: `geo_infer_sec`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SEC`
- Tests: `uv run python -m pytest GEO-INFER-SEC/tests/unit`

## Dependencies

- `cryptography>=36.0.0`
- `pyjwt>=2.3.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `pandas>=1.3.0`
- `numpy>=1.20.0`
- `pyyaml>=6.0`
- `h3>=4.5.0,<5`
- `pyproj>=3.0.0`


## Validation

```bash
uv run python -m pytest GEO-INFER-SEC/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
