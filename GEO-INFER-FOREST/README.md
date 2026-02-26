---
title: "GEO-INFER-FOREST: Forest and Vegetation Analysis"
description: "Forest monitoring, vegetation analysis, and woodland management"
purpose: "Provide forest inventory, change detection, and ecosystem analysis capabilities"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "TIME", "DATA", "BIO"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-DATA", "GEO-INFER-BIO"]
tags: ["forestry", "vegetation", "remote-sensing", "carbon", "biodiversity"]
difficulty: "Intermediate"
estimated_time: "50"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-FOREST: Forest and Vegetation Analysis

## Overview

**GEO-INFER-FOREST** provides comprehensive capabilities for forest monitoring and vegetation analysis. The module enables:

- **Forest Inventory**: Biomass estimation, species classification
- **Change Detection**: Deforestation, degradation, regrowth monitoring
- **Fire Risk Assessment**: Fuel load mapping, fire danger indices
- **Carbon Accounting**: Forest carbon stock estimation
- **Health Monitoring**: Pest, disease, and stress detection

## Features

### Forest Inventory

```python
from geo_infer_forest import ForestInventory

# Conduct forest inventory
inventory = ForestInventory()

results = inventory.analyze(
    area=forest_boundary,
    data_sources={
        "lidar": lidar_point_cloud,
        "imagery": satellite_imagery,
        "plots": field_plots
    }
)

print(f"Canopy height: {results.mean_height} m")
print(f"Biomass: {results.biomass_tonnes_ha} t/ha")
print(f"Dominant species: {results.dominant_species}")
```

### Change Detection

```python
from geo_infer_forest import ChangeDetector

# Detect forest changes
detector = ChangeDetector()

changes = detector.detect(
    area=study_area,
    start_date="2020-01-01",
    end_date="2025-12-31",
    change_types=["deforestation", "degradation", "regrowth"]
)

print(f"Forest loss: {changes.loss_hectares} ha")
print(f"Forest gain: {changes.gain_hectares} ha")
print(f"Net change: {changes.net_change_hectares} ha")
```

### Fire Risk Assessment

```python
from geo_infer_forest import FireRisk

# Assess fire risk
fire_risk = FireRisk()

assessment = fire_risk.assess(
    area=wildland_area,
    weather=current_weather,
    fuel_data=fuel_model,
    topography=dem
)

print(f"Fire danger rating: {assessment.danger_rating}")
print(f"Spread rate: {assessment.spread_rate} m/min")
print(f"High risk areas: {assessment.high_risk_zones}")
```

### Carbon Accounting

```python
from geo_infer_forest import CarbonAccounting

# Estimate forest carbon
carbon = CarbonAccounting()

stocks = carbon.estimate(
    forest_area=forest_boundary,
    inventory_data=forest_inventory,
    pools=["above_ground", "below_ground", "soil", "dead_wood"]
)

print(f"Total carbon: {stocks.total_tonnes} tC")
print(f"CO2 equivalent: {stocks.co2e_tonnes} tCO2e")
print(f"Annual sequestration: {stocks.annual_sequestration} tC/year")
```

## Analysis Capabilities

| Analysis Type | Description |
|---------------|-------------|
| **Canopy Height** | LiDAR-based height modeling |
| **Biomass** | Above/below-ground biomass mapping |
| **Species Classification** | ML-based species mapping |
| **NDVI/EVI** | Vegetation indices time series |
| **Disturbance** | Fire, harvest, storm detection |
| **Structure** | Canopy cover, gap analysis |

## Data Sources

| Data Type | Sources |
|-----------|---------|
| **Satellite** | Landsat, Sentinel-2, MODIS, Planet |
| **LiDAR** | Airborne, GEDI, ICESat-2 |
| **Radar** | Sentinel-1, ALOS PALSAR |
| **Field** | Plot data, inventory samples |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-BIO** | Biodiversity, habitat analysis |
| **GEO-INFER-CLIMATE** | Climate impacts on forests |
| **GEO-INFER-WATER** | Watershed forest coverage |
| **GEO-INFER-RISK** | Fire and pest risk modeling |

## Installation

```bash
# Install forest module
uv pip install -e "./GEO-INFER-FOREST"

# With remote sensing tools
uv pip install -e "./GEO-INFER-FOREST[remote_sensing]"
```

## Use Cases

### REDD+ Carbon Monitoring

```python
from geo_infer_forest import REDDMonitor

monitor = REDDMonitor(project="amazon_conservation")

# Generate REDD+ report
report = monitor.generate_report(
    reference_period=("2010", "2015"),
    monitoring_period=("2020", "2025"),
    uncertainty_analysis=True
)

print(f"Emissions reduced: {report.emissions_reduced} tCO2e")
print(f"Carbon credits: {report.credits}")
```

## Related Documentation

- [GEO-INFER-BIO](../GEO-INFER-BIO/README.md): Biodiversity
- [GEO-INFER-CLIMATE](../GEO-INFER-CLIMATE/README.md): Climate
- [AGENTS.md](./AGENTS.md): Forest agent capabilities

---

**Status**: Alpha - Core functionality implemented

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
