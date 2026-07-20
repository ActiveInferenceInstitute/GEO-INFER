# GEO-INFER-SPACE/src/geo_infer_space

Geo Infer Space workspace within `GEO-INFER-SPACE`.

## Contents

- `analytics/`
- `api/`
- `backends/`
- `core/`
- `gis/`
- `io/`
- `models/`
- `nested/`
- `tools/`
- `utils/`
- `__init__.py`
- `place_analyzer.py`
- `spatial_utils.py`

## Public Interface

- `place_analyzer.py:PlaceAnalyzer` (class)
- `spatial_utils.py:SpatialUtils` (class)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
