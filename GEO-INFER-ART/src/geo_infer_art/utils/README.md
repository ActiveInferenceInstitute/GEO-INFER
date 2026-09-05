# GEO-INFER-ART/src/geo_infer_art/utils

Utils workspace within `GEO-INFER-ART`.

## Contents

- `__init__.py`
- `animation.py`
- `validators.py`

## Public Interface

- `animation.py:save_animation_with_fallback` (function)
- `validators.py:validate_file_path` (function)
- `validators.py:validate_geospatial_data` (function)
- `validators.py:validate_coordinates` (function)
- `validators.py:validate_bbox` (function)
- `validators.py:validate_color` (function)
- `validators.py:validate_style_name` (function)
- `validators.py:validate_numeric_range` (function)
- `validators.py:validate_image_array` (function)
- `validators.py:validate_resolution` (function)
- `validators.py:validate_file_format` (function)

## Module Metadata

- Module: `GEO-INFER-ART`
- Package: `geo_infer_art`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ART`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ART`

## Dependencies

- `geopandas>=0.10.0`
- `matplotlib>=3.4.0`
- `numpy>=1.21.0`
- `pillow>=8.3.0`
- `rasterio>=1.2.0`
- `scipy>=1.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ART
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
