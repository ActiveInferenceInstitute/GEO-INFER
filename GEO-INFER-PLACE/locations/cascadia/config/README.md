# GEO-INFER-PLACE/locations/cascadia/config

Config workspace within `GEO-INFER-PLACE`.

## Contents

- `county_boundary_loader.py`
- `analysis_config.yaml`
- `ca_del_norte_boundary.geojson`
- `ca_humboldt_boundary.geojson`
- `ca_lassen_boundary.geojson`
- `cascadia_climate_zones.yaml`
- `cascadia_config.yaml`
- `cascadia_ecoregions.yaml`
- `cascadia_indigenous_territories.yaml`
- `cascadia_salmon_esus.yaml`
- `county_boundaries.yaml`
- `data_cleanup_config.json`
- `data_urls.json`

## Public Interface

- `county_boundary_loader.py:CountyBoundaryLoader` (class)
- `county_boundary_loader.py:create_county_boundary_loader` (function)

## Module Metadata

- Module: `GEO-INFER-PLACE`
- Package: `geo_infer_place`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PLACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE`

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
- `seaborn>=0.12.0`
- `branca>=0.6.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
