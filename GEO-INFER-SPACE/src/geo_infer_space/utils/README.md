# GEO-INFER-SPACE/src/geo_infer_space/utils

Utils workspace within `GEO-INFER-SPACE`.

## Contents

- `__init__.py`
- `config_loader.py`
- `h3_utils.py`

## Public Interface

- `config_loader.py:LocationBounds` (class)
- `config_loader.py:LocationConfigLoader` (class)
- `h3_utils.py:latlng_to_cell` (function)
- `h3_utils.py:cell_to_latlng` (function)
- `h3_utils.py:cell_to_latlng_boundary` (function)
- `h3_utils.py:polygon_to_cells` (function)
- `h3_utils.py:cell_to_latlngjson` (function)
- `h3_utils.py:geojson_to_h3` (function)
- `h3_utils.py:geo_to_cells` (function)
- `h3_utils.py:grid_disk` (function)
- `h3_utils.py:grid_distance` (function)
- `h3_utils.py:compact_cells` (function)
- `h3_utils.py:uncompact_cells` (function)
- `h3_utils.py:cell_area` (function)
- `h3_utils.py:get_resolution` (function)
- `h3_utils.py:is_valid_cell` (function)
- `h3_utils.py:are_neighbor_cells` (function)

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
