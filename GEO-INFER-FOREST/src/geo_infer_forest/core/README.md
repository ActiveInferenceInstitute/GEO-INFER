# core

## Overview

Core forest intelligence components for GEO-INFER-FOREST implementing forest health monitoring, wildfire risk assessment, carbon sequestration modeling, and forest inventory management.

This directory contains core components for forest intelligence including health monitoring, wildfire risk, carbon modeling, and inventory management.

## Components

### carbon_sequestration.py
Carbon sequestration modeling in forests.

**Classes**: `CarbonSequestrationModeler`

### forest_health.py
Forest health monitoring using NDVI and climate data.

**Classes**: `ForestHealthMonitor`

### forest_inventory.py
Forest inventory and biomass estimation.

**Classes**: `ForestInventory`

### wildfire_risk.py
Wildfire risk assessment and fire behavior modeling.

**Classes**: `FireDangerRating`, `FuelType`, `FireWeatherObservation`, `FireIncident`, `WildfireRiskAnalyzer`

## Usage

```python
from geo_infer_forest.core import (
    ForestHealthMonitor,
    WildfireRiskAnalyzer,
    CarbonSequestrationModeler,
    ForestInventory
)

# Forest health monitoring
monitor = ForestHealthMonitor()
health = monitor.assess_forest_health(ndvi=ndvi_data, temperature=temp_data)

# Wildfire risk assessment
analyzer = WildfireRiskAnalyzer()
risk = analyzer.assess_wildfire_risk(temperature=temp, precipitation=precip, fuel_load=fuel)

# Carbon modeling
modeler = CarbonSequestrationModeler()
carbon_stock = modeler.calculate_carbon_stock(biomass=biomass_data)
```

## Integration

- **Location**: `GEO-INFER-FOREST/src/geo_infer_forest/core`
- **Dependencies**: `xarray`, `geopandas`, `geo_infer_forest.models`
- **Used By**: API layer, application modules
- **Provides**: Core forest intelligence capabilities

--- 