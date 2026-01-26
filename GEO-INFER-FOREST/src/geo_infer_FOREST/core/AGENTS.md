# Agent: core

## Scope
This agent handles core forest intelligence components for GEO-INFER-FOREST implementing forest health monitoring, wildfire risk assessment, carbon sequestration modeling, and forest inventory management.

## Implementation Status

### Currently Implemented

- ✅ **ForestHealthMonitor**: Forest health assessment and deforestation detection
- ✅ **WildfireRiskAnalyzer**: Wildfire risk assessment and fire spread prediction
- ✅ **CarbonSequestrationModeler**: Carbon stock and sequestration modeling
- ✅ **ForestInventory**: Forest inventory and biomass estimation

## Agent Capabilities

### 1. Forest Health Monitoring

```python
from geo_infer_FOREST.core import ForestHealthMonitor

monitor = ForestHealthMonitor()

# Assess forest health
health_assessment = monitor.assess_forest_health(
    ndvi=ndvi_data,
    temperature=temperature_data,
    precipitation=precipitation_data
)

# Detect deforestation
deforestation = monitor.detect_deforestation(
    forest_cover_time_series=time_series_data,
    threshold=0.2
)
```

### 2. Wildfire Risk Assessment

```python
from geo_infer_FOREST.core import WildfireRiskAnalyzer, FireIncident

analyzer = WildfireRiskAnalyzer()

# Assess wildfire risk
risk_assessment = analyzer.assess_wildfire_risk(
    temperature=temp_data,
    precipitation=precip_data,
    fuel_load=fuel_data,
    wind_speed=wind_data
)

# Predict fire spread
spread_prediction = analyzer.predict_fire_spread(
    ignition_points=ignition_data,
    fuel_load=fuel_data,
    wind_direction=wind_dir_data
)

# Register fire incident
incident_id = analyzer.register_incident(FireIncident(...))
```

### 3. Carbon Sequestration

```python
from geo_infer_FOREST.core import CarbonSequestrationModeler

modeler = CarbonSequestrationModeler()

# Calculate carbon stock
carbon_stock = modeler.calculate_carbon_stock(biomass=biomass_data)

# Estimate sequestration rate
sequestration_rate = modeler.estimate_sequestration_rate(
    biomass_growth=growth_data,
    time_period=365
)

# Calculate carbon credits
credits = modeler.calculate_carbon_credits(
    carbon_sequestration=seq_data,
    area=area_data,
    price_per_ton=50.0
)
```

### 4. Forest Inventory

```python
from geo_infer_FOREST.core import ForestInventory

inventory = ForestInventory()

# Estimate biomass
biomass = inventory.estimate_biomass(
    forest_cover=cover_data,
    tree_density=density_data
)

# Calculate forest area
area = inventory.calculate_forest_area(
    forest_cover=cover_data,
    cell_area=cell_area_data
)
```

## Key Classes

### ForestHealthMonitor
Monitor forest health using NDVI and climate data.

**Key Methods**:
- `assess_forest_health(ndvi, temperature, precipitation) -> xr.Dataset`
- `detect_deforestation(forest_cover_time_series, threshold) -> xr.Dataset`

### WildfireRiskAnalyzer
Wildfire risk assessment system with fire spread prediction.

**Key Methods**:
- `assess_wildfire_risk(temperature, precipitation, fuel_load, wind_speed) -> xr.Dataset`
- `calculate_fire_weather_index(observation) -> Dict[str, Any]`
- `predict_fire_spread(ignition_points, fuel_load, wind_direction) -> xr.Dataset`
- `model_fire_perimeter(ignition_point, fuel_type, wind_speed, wind_direction, slope, time) -> Dict[str, Any]`
- `register_incident(incident) -> str`

### CarbonSequestrationModeler
Model carbon sequestration in forests.

**Key Methods**:
- `calculate_carbon_stock(biomass) -> xr.DataArray`
- `estimate_sequestration_rate(biomass_growth, time_period) -> xr.DataArray`
- `calculate_carbon_credits(carbon_sequestration, area, price_per_ton) -> xr.DataArray`

### ForestInventory
Forest inventory and biomass estimation.

**Key Methods**:
- `estimate_biomass(forest_cover, tree_density) -> xr.DataArray`
- `calculate_forest_area(forest_cover, cell_area) -> xr.DataArray`

## Integration

- **Location**: `GEO-INFER-FOREST/src/geo_infer_FOREST/core`
- **Dependencies**: `xarray`, `geopandas`, `geo_infer_FOREST.models`
- **Used By**: API layer, application modules
- **Provides**: Core forest intelligence capabilities for health monitoring, wildfire risk, and carbon modeling

---

This AGENTS.md documents core forest intelligence components for GEO-INFER-FOREST.
