# GEO-INFER-NORMS/examples

Examples workspace within `GEO-INFER-NORMS`.

## Contents

- `output/`
- `minimal_zoning_example.py`
- `zoning_analysis_example.py`

## Public Interface

- `minimal_zoning_example.py:generate_color_palette` (function)
- `minimal_zoning_example.py:create_custom_colormap` (function)
- `minimal_zoning_example.py:get_current_timestamp` (function)
- `minimal_zoning_example.py:format_dict_for_display` (function)
- `minimal_zoning_example.py:save_plot` (function)
- `minimal_zoning_example.py:calculate_area` (function)
- `minimal_zoning_example.py:wrap_labels` (function)
- `minimal_zoning_example.py:ZoningCode` (class)
- `minimal_zoning_example.py:ZoningDistrict` (class)
- `minimal_zoning_example.py:LandUseType` (class)
- `minimal_zoning_example.py:Parcel` (class)
- `minimal_zoning_example.py:EnvironmentalAssessment` (class)
- `minimal_zoning_example.py:ZoningAnalyzer` (class)
- `minimal_zoning_example.py:LandUseClassifier` (class)
- `minimal_zoning_example.py:create_sample_data` (function)
- `minimal_zoning_example.py:main` (function)
- `zoning_analysis_example.py:generate_color_palette` (function)
- `zoning_analysis_example.py:create_custom_colormap` (function)
- `zoning_analysis_example.py:get_current_timestamp` (function)
- `zoning_analysis_example.py:format_dict_for_display` (function)

## Module Metadata

- Module: `GEO-INFER-NORMS`
- Package: `geo_infer_norms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-NORMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS`

## Dependencies

- `geopandas>=0.10.0`
- `matplotlib>=3.4.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `shapely>=1.8.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
