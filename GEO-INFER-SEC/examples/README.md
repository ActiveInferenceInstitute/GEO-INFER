# GEO-INFER-SEC/examples

Examples workspace within `GEO-INFER-SEC`.

## Contents

- `anonymization_example.py`
- `comprehensive_security_example.py`
- `secure_geospatial_data.py`

## Public Interface

- `anonymization_example.py:create_sample_data` (function)
- `anonymization_example.py:plot_comparison` (function)
- `anonymization_example.py:demonstrate_location_perturbation` (function)
- `anonymization_example.py:demonstrate_spatial_k_anonymity` (function)
- `anonymization_example.py:create_admin_boundaries` (function)
- `anonymization_example.py:demonstrate_geographic_masking` (function)
- `anonymization_example.py:main` (function)
- `comprehensive_security_example.py:SecurityDemoEnvironment` (class)
- `comprehensive_security_example.py:main` (function)
- `comprehensive_security_example.py:run_demo` (function)
- `secure_geospatial_data.py:main` (function)

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
- `h3>=4.5.0,<5`
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
