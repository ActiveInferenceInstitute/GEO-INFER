# GEO-INFER-ENERGY Documentation

GEO-INFER-ENERGY provides spatial energy systems analysis for the GEO-INFER framework. It covers renewable resource assessment, grid optimization, demand forecasting, carbon footprint analysis, and energy infrastructure planning.

## Module Architecture

The module is organized around seven core components:

| Component | Class | Purpose |
|-----------|-------|---------|
| Solar Analysis | `SolarAnalyzer` | Physics-based solar irradiance and PV output modeling |
| Wind Analysis | `WindAnalyzer` | Wind resource assessment and turbine power curves |
| Renewable Resources | `RenewableResourceAssessor` | Multi-resource siting, LCOE, capacity factor, storage needs |
| Energy Grid | `EnergyGridOptimizer` | Supply-demand balancing and grid reliability assessment |
| Energy Demand | `EnergyDemandForecaster` | Trend-based demand forecasting with temperature/population adjustors |
| Carbon Footprint | `CarbonFootprintAnalyzer` | Emissions tracking and carbon intensity mapping |
| Infrastructure | `EnergyInfrastructurePlanner` | Transmission and generation infrastructure planning |

## Data Flow

```
Resource Data (irradiance, wind, flow)
        |
        v
RenewableResourceAssessor / SolarAnalyzer / WindAnalyzer
        |
        v
Site suitability scores, capacity factors, LCOE
        |
        v
EnergyGridOptimizer  <---  EnergyDemandForecaster
        |
        v
Supply-demand balance, reliability indices
        |
        v
CarbonFootprintAnalyzer / EnergyInfrastructurePlanner
        |
        v
Emissions maps, infrastructure expansion plans
```

## Key Design Decisions

- All spatial data uses `xarray.DataArray` and `xarray.Dataset` for raster operations.
- Solar irradiance models are physics-based (Spencer 1971 declination, Hottel 1976 clear-sky).
- The `RenewableResourceAssessor` uses configurable thresholds per resource type for suitability classification.
- LCOE calculation uses real NPV discounting over the project lifetime.
- Wind power curves implement cut-in, rated, and cut-out speed thresholds with cubic ramp.
- Storage analysis sizes batteries to cover 4 hours of peak deficit by default.

## Integration with Other Modules

GEO-INFER-ENERGY integrates with the broader GEO-INFER ecosystem:

- **GEO-INFER-SPACE**: H3 hexagonal grid indexing for spatial aggregation of energy potential.
- **GEO-INFER-DATA**: Data ingestion pipelines for satellite-derived irradiance and reanalysis wind data.
- **GEO-INFER-CLIMATE**: Climate projections for long-term renewable resource estimation.
- **GEO-INFER-RISK**: Grid vulnerability and natural hazard exposure analysis.
- **GEO-INFER-ECON**: Energy market modeling and cost-benefit analysis of infrastructure investments.

## Quick Links

- [Getting Started](getting_started.md) -- installation, core concepts, first analysis
- [API Reference](api_reference.md) -- classes, methods, parameters, return types
- [Basic Example: Solar Siting](examples/basic_example.md) -- H3-indexed solar irradiance scoring
- [Advanced Example: Integrated Energy Planning](examples/advanced_example.md) -- solar + wind + grid extension optimization

## Package Structure

```
GEO-INFER-ENERGY/
  src/geo_infer_energy/
    __init__.py              # Exports all 7 core classes
    core/
      solar_analysis.py      # SolarAnalyzer
      wind_analysis.py       # WindAnalyzer
      renewable_resources.py # RenewableResourceAssessor, RenewableType, RenewableSite
      energy_grid.py         # EnergyGridOptimizer
      energy_demand.py       # EnergyDemandForecaster
      carbon_footprint.py    # CarbonFootprintAnalyzer
      energy_infrastructure.py # EnergyInfrastructurePlanner
    api/                     # REST API endpoints
    utils/                   # Shared utilities
  tests/
    unit/
    integration/
  docs/                      # This documentation
```

## Dependencies

Core dependencies include `numpy`, `xarray`, `pandas`, and `scikit-learn`. All are standard scientific Python packages. Optional dependencies such as `geopandas` and `h3` enable spatial operations when available.

## Version

Current version: `0.1.0`
