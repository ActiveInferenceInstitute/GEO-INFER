# GEO-INFER-PLACE/src/geo_infer_place/core

Core workspace within `GEO-INFER-PLACE`.

## Contents

- `dashboard/`
- `__init__.py`
- `api_clients.py`
- `base_module.py`
- `bioregion_visualization.py`
- `comprehensive_dashboard.py`
- `module_bridge.py`
- `place_interface.py`
- `unified_backend.py`
- `visualization_engine.py`

## Public Interface

- `api_clients.py:CALFIREClient` (class)
- `api_clients.py:NOAAClient` (class)
- `api_clients.py:USGSClient` (class)
- `api_clients.py:USGSEarthquakeClient` (class)
- `api_clients.py:CDECClient` (class)
- `api_clients.py:CaliforniaAPIManager` (class)
- `base_module.py:BaseAnalysisModule` (class)
- `bioregion_visualization.py:create_bioregion_map` (function)
- `module_bridge.py:PlaceDataManager` (class)
- `module_bridge.py:PlaceTemporalAnalyzer` (class)
- `place_interface.py:PlaceInterface` (class)
- `unified_backend.py:CascadianAgriculturalH3Backend` (class)
- `visualization_engine.py:InteractiveVisualizationEngine` (class)

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
