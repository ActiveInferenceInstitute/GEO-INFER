# GEO-INFER-ART/tests

Tests workspace within `GEO-INFER-ART`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `run_all_tests.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:sample_image_array` (function)
- `conftest.py:spatial_art_config` (function)
- `conftest.py:color_palette` (function)
- `conftest.py:sample_terrain_data` (function)
- `run_all_tests.py:run_all_tests` (function)

## Module Metadata

- Module: `GEO-INFER-ART`
- Package: `geo_infer_art`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ART`
- Tests: `uv run python -m pytest GEO-INFER-ART/tests`

## Dependencies

- `bokeh>=2.4.0`
- `cartopy>=0.20.0`
- `colour>=0.1.5`
- `folium>=0.12.0`
- `geopandas>=0.10.0`
- `imageio>=2.9.0`
- `imageio-ffmpeg>=0.4.0`
- `kaleido>=0.2.0`
- `matplotlib>=3.4.0`
- `numpy>=1.21.0`
- `opencv-python>=4.5.0`
- `pillow>=8.3.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-ART/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
