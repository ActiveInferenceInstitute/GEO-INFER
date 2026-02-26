# GEO-INFER-MARINE Documentation

GEO-INFER-MARINE provides marine and oceanographic spatial analysis for the GEO-INFER framework. It covers oceanographic data processing, coastal vulnerability assessment, marine ecosystem modeling, sea-level analysis, marine spatial planning, ocean current modeling, water quality assessment, and coral reef health monitoring.

## Module Architecture

The module is organized around eight core components:

| Component | Class | Purpose |
|-----------|-------|---------|
| Oceanographic Data | `OceanographicDataProcessor` | Load, process, and interpolate 3D ocean data |
| Coastal Analysis | `CoastalAnalyzer` | Coastal vulnerability and erosion assessment |
| Marine Ecosystems | `MarineEcosystemModeler` | Ecosystem health and habitat suitability modeling |
| Sea Level | `SeaLevelAnalyzer` | Sea-level rise projections and inundation mapping |
| Marine Spatial Planning | `MarineSpatialPlanner` | MPA design and offshore wind siting |
| Ocean Currents | `OceanCurrentModeler` | Current velocity, magnitude, and direction analysis |
| Water Quality | `MarineWaterQuality` | Marine water quality index computation |
| Coral Reef | `CoralReefAssessor` | Coral reef health and bleaching risk assessment |

## Data Flow

```
NetCDF / Satellite Data
        |
        v
OceanographicDataProcessor (load, subset, interpolate)
        |
        +--> OceanCurrentModeler (velocity fields, magnitude, direction)
        |
        +--> SeaLevelAnalyzer (projections, inundation zones)
        |
        +--> MarineWaterQuality (temperature, salinity, chlorophyll indices)
        |
        v
CoastalAnalyzer (vulnerability, erosion rates)
        |
        v
MarineSpatialPlanner (MPA networks, offshore wind, zone conflicts)
        |
        v
MarineEcosystemModeler / CoralReefAssessor (health, connectivity, bleaching)
```

## Key Design Decisions

- Ocean data uses `xarray.Dataset` natively, matching the standard format for NetCDF oceanographic products.
- The `OceanographicDataProcessor` supports 3D data with depth dimension for temperature/salinity profiles.
- Ocean current calculation derives magnitude and direction from U/V velocity components.
- Coastal vulnerability scoring uses inverse relative elevation with optional wave height amplification.
- MPA network design uses biodiversity-priority ranking with configurable coverage targets (default 30%, aligned with 30x30 conservation goals).
- Offshore wind siting combines wind resource potential with bathymetric depth constraints.

## Integration with Other Modules

- **GEO-INFER-SPACE**: H3 hexagonal indexing for marine spatial aggregation (ocean hex grids).
- **GEO-INFER-DATA**: Satellite and reanalysis data ingestion (CMEMS, NOAA, Copernicus Marine).
- **GEO-INFER-TIME**: Temporal trend analysis for sea-level rise, SST anomalies, and fisheries time series.
- **GEO-INFER-CLIMATE**: Climate model coupling for ocean warming and acidification projections.
- **GEO-INFER-RISK**: Multi-hazard coastal risk integration (storm surge, tsunami, flooding).
- **GEO-INFER-BIO**: Marine biodiversity and species distribution modeling.
- **GEO-INFER-ENERGY**: Offshore wind and tidal energy resource assessment.

## Quick Links

- [Getting Started](getting_started.md) -- installation, core concepts, first ocean analysis
- [API Reference](api_reference.md) -- classes, methods, parameters, return types
- [Basic Example: Coastal Risk Assessment](examples/basic_example.md) -- vulnerability index from DEM + storm surge
- [Advanced Example: Fisheries Stock Assessment](examples/advanced_example.md) -- spatial CPUE + habitat suitability + MPA effectiveness

## Package Structure

```
GEO-INFER-MARINE/
  src/geo_infer_marine/
    __init__.py                 # Exports all 8 core classes
    core/
      oceanographic_data.py     # OceanographicDataProcessor
      coastal_analysis.py       # CoastalAnalyzer
      marine_ecosystems.py      # MarineEcosystemModeler
      sea_level.py              # SeaLevelAnalyzer
      marine_spatial_planning.py # MarineSpatialPlanner
      ocean_currents.py         # OceanCurrentModeler
      water_quality.py          # MarineWaterQuality
      coral_reef.py             # CoralReefAssessor
    api/                        # REST API endpoints
    utils/                      # Shared utilities
  tests/
    unit/
    integration/
  docs/                         # This documentation
```

## Dependencies

Core dependencies include `numpy`, `xarray`, and `pandas`. Optional dependencies include `netCDF4` for file I/O, `geopandas` for vector operations, and `scipy` for spatial interpolation.

## Version

Current version: `0.1.0`
