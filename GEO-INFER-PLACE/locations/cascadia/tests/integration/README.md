# GEO-INFER-PLACE/locations/cascadia/tests/integration

Integration workspace within `GEO-INFER-PLACE`.

## Contents

- `comprehensive_test.py`
- `focused_framework_test.py`
- `run_comprehensive_validation.py`
- `test_bioregion_pipeline.py`
- `test_enhanced_h3_fusion.py`
- `test_modules.py`
- `test_real_data_processing.py`

## Public Interface

- `run_comprehensive_validation.py:check_main_script_contract` (function)
- `run_comprehensive_validation.py:check_configuration_contract` (function)
- `run_comprehensive_validation.py:check_module_structure` (function)
- `run_comprehensive_validation.py:check_h3_integration` (function)
- `run_comprehensive_validation.py:check_backend_initialization` (function)
- `run_comprehensive_validation.py:check_data_module_initialization` (function)
- `run_comprehensive_validation.py:run_checks` (function)
- `run_comprehensive_validation.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-PLACE`
- Package: `geo_infer_place`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PLACE`
- Tests: `uv run python -m pytest GEO-INFER-PLACE/locations/cascadia/tests/integration`

## Dependencies

- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `h3>=4.5.0,<5`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `pyyaml>=6.0`
- `geo-infer-space`
- `folium>=0.14.0`
- `plotly>=5.0.0`
- `matplotlib>=3.5.0`
- `branca>=0.6.0`
- `requests>=2.28.0`


## Validation

```bash
uv run python -m pytest GEO-INFER-PLACE/locations/cascadia/tests/integration
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
