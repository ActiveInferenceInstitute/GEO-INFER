# GEO-INFER-ART/examples

Examples workspace within `GEO-INFER-ART`.

## Contents

- `artistic_map_generation.py`
- `run_all_examples.py`

## Public Interface

- `artistic_map_generation.py:ensure_directory` (function)
- `artistic_map_generation.py:create_sample_geo_data` (function)
- `artistic_map_generation.py:example_1_basic_geo_art` (function)
- `artistic_map_generation.py:example_2_color_palettes` (function)
- `artistic_map_generation.py:example_3_style_transfer` (function)
- `artistic_map_generation.py:example_4_generative_maps` (function)
- `artistic_map_generation.py:example_5_procedural_art` (function)
- `artistic_map_generation.py:example_6_place_art` (function)
- `artistic_map_generation.py:example_7_cultural_maps` (function)
- `artistic_map_generation.py:run_all` (function)
- `run_all_examples.py:find_example_scripts` (function)
- `run_all_examples.py:run_example` (function)
- `run_all_examples.py:run_all_examples` (function)

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
