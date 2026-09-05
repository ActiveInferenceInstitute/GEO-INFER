# GEO-INFER-FOREST Documentation

GEO-INFER-FOREST provides spatial forest analysis for the GEO-INFER framework. It covers forest inventory and biomass estimation, carbon sequestration modeling, canopy structure analysis from remote sensing, deforestation detection, wildfire risk assessment, and forest health monitoring.

## Module Architecture

The module is organized around seven core components:

| Component | Class | Purpose |
|-----------|-------|---------|
| Forest Inventory | `ForestInventory` | Biomass estimation and forest area calculation |
| Carbon Sequestration | `CarbonSequestrationModeler` | Carbon stock, sequestration rates, credit valuation |
| Canopy Analysis | `CanopyAnalyzer` | NDVI/EVI indices, canopy cover, LAI, gap detection |
| Deforestation Detection | `DeforestationDetector` | Two-date and time-series change detection |
| Wildfire Risk | `WildfireRiskAnalyzer` | Fire risk scoring and fuel load estimation |
| Forest Health | `ForestHealthMonitor` | Multi-factor health status monitoring |
| Fire Risk | `FireRiskAssessor` | Spatial fire risk assessment |

## Data Flow

```
Remote Sensing (Red, NIR, Blue bands)
        |
        v
CanopyAnalyzer (NDVI, EVI, canopy cover, LAI)
        |
        v
ForestInventory (biomass, forest area)
        |
        v
CarbonSequestrationModeler (carbon stock, sequestration rates, credits)
        |
        +---> DeforestationDetector (change detection, annual rates, fragmentation)
        |
        +---> WildfireRiskAnalyzer / FireRiskAssessor (fire risk maps)
        |
        v
ForestHealthMonitor (integrated health assessment)
```

## Key Design Decisions

- Vegetation index calculations (NDVI, EVI) use `xarray.DataArray` for band-math operations.
- Canopy cover estimation uses the linear FVC-NDVI relationship with configurable soil and vegetation NDVI endpoints.
- Leaf Area Index (LAI) is derived from NDVI via Beer-Lambert law.
- Deforestation detection supports both two-date change detection and time-series approaches with configurable confidence levels.
- Carbon stock follows the standard 50% carbon fraction of dry biomass.
- CO2 equivalent conversion uses the 3.67x molecular weight ratio for carbon credit calculations.
- Fragmentation analysis uses edge density and core-to-edge ratio from raster neighbor analysis.

## Integration with Other Modules

- **GEO-INFER-SPACE**: H3 hexagonal indexing for aggregating forest metrics by cell.
- **GEO-INFER-DATA**: Satellite imagery ingestion (Landsat, Sentinel-2) and preprocessing.
- **GEO-INFER-TIME**: Temporal trend analysis on NDVI time series.
- **GEO-INFER-CLIMATE**: Climate change impacts on forest growth and fire risk.
- **GEO-INFER-BIO**: Biodiversity assessment in forest habitats.
- **GEO-INFER-RISK**: Integrating wildfire risk into multi-hazard frameworks.
- **GEO-INFER-ECON**: Carbon market valuation and forest-based ecosystem services.

## Quick Links

- [Getting Started](getting_started.md) -- installation, core concepts, first biomass estimate
- [API Reference](api_reference.md) -- classes, methods, parameters, return types
- [Basic Example: Carbon Stock Estimation](examples/basic_example.md) -- load stand data, estimate biomass, compute carbon
- [Advanced Example: Habitat Connectivity](examples/advanced_example.md) -- fragmentation analysis and corridor identification

## Package Structure

```
GEO-INFER-FOREST/
  src/geo_infer_forest/
    __init__.py                # Exports all 7 core classes
    core/
      forest_inventory.py      # ForestInventory
      carbon_sequestration.py  # CarbonSequestrationModeler
      canopy_analysis.py       # CanopyAnalyzer
      deforestation.py         # DeforestationDetector
      wildfire_risk.py         # WildfireRiskAnalyzer
      forest_health.py         # ForestHealthMonitor
      fire_risk.py             # FireRiskAssessor
  tests/
    unit/
    integration/
  docs/                        # This documentation
```

## Dependencies

Core dependencies are `numpy`, `xarray`, and `scipy` (for statistical tests in change detection). Optional extras: `vector` (`geopandas` + `shapely`) for vector-based stand polygons, `test` for the test suite. Current version: `0.2.0`.
