# GEO-INFER-ART/docs

Docs workspace within `GEO-INFER-ART`.

## Contents

- `api_schema.yaml`
- `api_specification.md`
- `architecture.md`
- `data_schemas.md`
- `user_guide.md`

## Public Interface

- No public Python symbols are defined directly in this directory.

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
