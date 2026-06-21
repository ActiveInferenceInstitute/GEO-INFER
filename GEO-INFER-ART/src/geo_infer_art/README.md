# GEO-INFER-ART/src/geo_infer_art

Geo Infer Art workspace within `GEO-INFER-ART`.

## Contents

- `api/`
- `core/`
- `models/`
- `utils/`
- `__init__.py`
- `cli.py`

## Public Interface

- `cli.py:ensure_directory` (function)
- `cli.py:process_geo_art` (function)
- `cli.py:process_style_transfer` (function)
- `cli.py:process_place_art` (function)
- `cli.py:process_generative_map` (function)
- `cli.py:process_procedural_art` (function)
- `cli.py:process_cultural_map` (function)
- `cli.py:process_map_style` (function)
- `cli.py:process_animation` (function)
- `cli.py:process_custom_algorithm` (function)
- `cli.py:process_performance` (function)
- `cli.py:process_3d_viz` (function)
- `cli.py:process_realtime` (function)
- `cli.py:process_web_map` (function)
- `cli.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-ART`
- Package: `geo_infer_art`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ART`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ART`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module ART
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
