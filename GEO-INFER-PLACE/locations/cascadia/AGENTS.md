# Agent: cascadia

## Scope

Agricultural land analysis across the Cascadian bioregion (Northern California + Oregon)
using H3-indexed geospatial data fusion, real-time data acquisition, and comprehensive
visualization.

## Capabilities

- **Agricultural Analysis**: Crop suitability, land use classification, soil health assessment
- **H3 Geospatial Fusion**: Enhanced H3 v4 spatial indexing at configurable resolution
- **Real Data Acquisition**: Multi-source data fetching with intelligent caching
- **Visualization**: Comprehensive dashboards, spatial correlation maps, and reporting
- **Multi-County Support**: Configurable county selection across CA and OR

## Key Modules

- `cascadia_main.py` — Main orchestration script (68KB)
- `src/core/enhanced_data_manager.py` — Cached data management
- `src/core/enhanced_h3_fusion.py` — H3 geospatial fusion
- `src/core/real_data_acquisition.py` — API data acquisition
- `src/core/visualization/` — Dashboard generation

## Status

✅ Production — fully implemented with tests and benchmarks.

## Integration

- **Location**: `GEO-INFER-PLACE/locations/cascadia`
- **Type**: Location Node (standalone with own `src/`, `tests/`, `config/`)
- **Dependencies**: `geo_infer_place.core`, `geo_infer_space` (optional)
