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

- `comprehensive_test.py:ComprehensiveTestSuite` (class)
- `comprehensive_test.py:main` (function)
- `focused_framework_test.py:test_main_script_functionality` (function)
- `focused_framework_test.py:test_backend_with_mocked_dependencies` (function)
- `focused_framework_test.py:test_module_functionality` (function)
- `focused_framework_test.py:test_h3_utilities` (function)
- `focused_framework_test.py:run_focused_tests` (function)
- `run_comprehensive_validation.py:test_main_script_syntax` (function)
- `run_comprehensive_validation.py:test_configuration_files` (function)
- `run_comprehensive_validation.py:test_module_structure` (function)
- `run_comprehensive_validation.py:test_h3_integration` (function)
- `run_comprehensive_validation.py:test_backend_initialization` (function)
- `run_comprehensive_validation.py:test_module_imports` (function)
- `run_comprehensive_validation.py:test_main_script_functionality` (function)
- `run_comprehensive_validation.py:run_comprehensive_validation` (function)

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
- `folium>=0.14.0`
- `plotly>=5.0.0`
- `matplotlib>=3.5.0`
- `seaborn>=0.12.0`
- `branca>=0.6.0`
- `requests>=2.28.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-PLACE/locations/cascadia/tests/integration
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
