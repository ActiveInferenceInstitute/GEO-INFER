# Agent: del_norte_county

## Scope

Production geospatial analysis framework for Del Norte County, California — providing
real-time environmental monitoring, infrastructure assessment, coastal resilience,
seismic hazard analysis, and interactive visualization.

## Capabilities

- **Forest Health Monitoring** (15 methods): NDVI/EVI analysis, tree mortality detection,
  climate vulnerability assessment, CAL FIRE integration
- **Coastal Resilience Analysis** (18 methods): Sea level rise scenarios, erosion rates,
  storm surge vulnerability, tsunami risk, habitat connectivity, NOAA tide gauge data
- **Fire Risk Assessment** (12 methods): Fuel load, weather, FWI calculation, WUI risk,
  topography, accessibility scoring
- **Seismic Hazard Analysis** (8 methods): USGS earthquake data, H3 hazard grid,
  Cascadia Subduction Zone scenario, tsunami inundation, liquefaction risk
- **Dashboard Generation**: Interactive HTML dashboards with cached data, map layers
- **API Integration**: CAL FIRE wrapper (7 methods), NOAA wrapper (8 methods),
  USGS Earthquake wrapper (4 methods)

## Key Files

- `run_analysis.py` — Main analysis orchestrator with auto-cleanup
- `create_del_norte_dashboard.py` — Dashboard generator
- `config/analysis_config.yaml` — Analysis parameters (304 lines)
- `requirements.txt` / `requirements_advanced.txt` — Dependencies

## Status

✅ Production — 50+ fully implemented methods, 19 API wrappers, all tests passing.

## Integration

- **Location**: `GEO-INFER-PLACE/locations/del_norte_county`
- **Type**: Location Node (production)
- **Source Code**: `src/geo_infer_place/locations/del_norte_county/`
- **Dependencies**: `geo_infer_place.utils.integration`, CAL FIRE API, NOAA API, USGS API
