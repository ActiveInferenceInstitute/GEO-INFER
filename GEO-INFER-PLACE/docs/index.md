# GEO-INFER-PLACE Documentation

GEO-INFER-PLACE provides place-based geospatial analysis for the GEO-INFER framework. It combines location-specific data integration, multi-domain analysis, real-time data acquisition, and interactive visualization to create deep, place-specific insights.

## Module Architecture

The module is organized around a unified `PlaceInterface` that orchestrates location-specific analyzers, data acquisition pipelines, temporal analysis, and quality management.

| Component | Class | Purpose |
|-----------|-------|---------|
| Unified Interface | `PlaceInterface` | Primary entry point for all place-based analysis |
| Data Manager | `PlaceDataManager` | Data quality validation and provenance tracking (bridges GEO-INFER-DATA) |
| Temporal Analyzer | `PlaceTemporalAnalyzer` | Trend detection and anomaly analysis (bridges GEO-INFER-TIME) |
| Visualization | `InteractiveVisualizationEngine` | H3 hexagonal maps and interactive dashboards |
| API Clients | `CaliforniaAPIManager`, `NOAAClient`, `USGSClient`, `CALFIREClient` | Real-time data from federal and state agencies |
| H3 Backend | `CascadianAgriculturalH3Backend` | Cascadia-specific agricultural analysis on H3 grid |

### Supported Locations

| Location | Key | Analyzers | Data Sources |
|----------|-----|-----------|-------------|
| Del Norte County, CA | `del_norte` | Forest health, coastal resilience, fire risk, seismic hazard | CAL FIRE, NOAA, USGS |
| Cascadia Bioregion | `cascadia` | Seismic hazard, forest health, salmon habitat, volcanic hazard | USGS, NOAA, CAL FIRE |

## Data Flow

```
PlaceInterface("del_norte")
        |
        +--> API Clients (NOAA, USGS, CAL FIRE)
        |       |
        |       v
        |   Raw Data (earthquakes, tides, fires, weather)
        |       |
        |       v
        +--> Location-Specific Analyzers
        |       |
        |       +--> ForestHealthMonitor
        |       +--> CoastalResilienceAnalyzer
        |       +--> FireRiskAssessor
        |       +--> SeismicHazardAnalyzer
        |       |
        |       v
        +--> PlaceDataManager (quality validation, provenance)
        |
        +--> PlaceTemporalAnalyzer (trends, anomalies)
        |
        v
    Unified Results (JSON, visualizations)
```

## Key Design Decisions

- `PlaceInterface` uses lazy initialization for all components -- analyzers, data managers, and API clients are created only when first accessed.
- Location presets are loaded from `config/location_presets.yaml` with a hardcoded fallback dictionary.
- All API clients include retry logic and response caching via `CachedAPIWrapper`.
- H3 v4 API is used throughout (`latlng_to_cell`, `cell_to_latlng`, not legacy functions).
- The module re-exports H3 utility functions for convenience (18 functions from `utils.h3_operations`).
- Results are serialized to timestamped JSON files in the output directory.

## Integration with Other Modules

- **GEO-INFER-SPACE**: H3 hexagonal indexing, spatial backends, place analysis foundations.
- **GEO-INFER-DATA**: Data quality management and provenance tracking via `PlaceDataManager`.
- **GEO-INFER-TIME**: Temporal trend detection and forecasting via `PlaceTemporalAnalyzer`.
- **GEO-INFER-FOREST**: Forest health monitoring methods integrated into Del Norte analyzers.
- **GEO-INFER-RISK**: Seismic hazard and fire risk assessment frameworks.
- **GEO-INFER-CLIMATE**: Climate data for Cascadia bioregional analysis.

## Cascadia Bioregion Example

The `locations/cascadia/` directory contains a complete bioregional analysis pipeline:

```
locations/cascadia/
  cascadia_main.py           # Main analysis orchestrator
  cascadia_server.py         # Optional HTTP server
  config/
    cascadia_config.yaml     # Bioregion-wide configuration
    analysis_config.yaml     # Analysis parameters
    cascadia_ecoregions.yaml # Ecoregion definitions
    cascadia_climate_zones.yaml
    cascadia_indigenous_territories.yaml
    cascadia_salmon_esus.yaml
  src/
    core/
      data_processor.py      # Cascadia data pipeline
      geo_infer_integrations.py
      visualization/
    data_modules/
      ecology/
  tests/
```

## Quick Links

- [Getting Started](getting_started.md) -- installation, core concepts, first place analysis
- [API Reference](api_reference.md) -- classes, methods, parameters, return types
- [Basic Example: Place Characterization](examples/basic_example.md) -- multi-layer neighborhood identity
- [Advanced Example: Bioregional Health](examples/advanced_example.md) -- Cascadia-style composite assessment

## Package Structure

```
GEO-INFER-PLACE/
  src/geo_infer_place/
    __init__.py              # Exports PlaceInterface + 60 other symbols
    core/
      place_interface.py     # PlaceInterface (primary entry point)
      module_bridge.py       # PlaceDataManager, PlaceTemporalAnalyzer
      visualization_engine.py # InteractiveVisualizationEngine
      unified_backend.py     # CascadianAgriculturalH3Backend
      api_clients.py         # NOAA, USGS, CAL FIRE, CDEC clients
      base_module.py         # BaseAnalysisModule
    config/                  # Location presets, YAML configs
    locations/
      del_norte_county/      # Del Norte-specific analyzers
    utils/
      h3_operations.py       # H3 v4 utility functions
      caching.py             # CachedAPIWrapper
      data_sources.py        # CaliforniaDataSources
  locations/cascadia/        # Cascadia bioregion analysis
  tests/
  docs/                      # This documentation
```

## Version

Current version: `1.1.0`
