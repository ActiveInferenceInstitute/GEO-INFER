# GEO-INFER-FOREST: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-FOREST** module provides forest monitoring capabilities for agents, enabling forest inventory, change detection, and ecosystem analysis.

## Agent Capabilities

### 1. Forest Inventory

```python
from geo_infer_forest import ForestInventory

# Conduct forest inventory
inventory = ForestInventory()

results = inventory.analyze(
    area=forest_boundary,
    data_sources={"lidar": lidar_data, "imagery": satellite})

print(f"Biomass: {results.biomass_tonnes_ha} t/ha")
print(f"Canopy height: {results.mean_height} m")```

### 2. Change Detection

```python
from geo_infer_forest import ChangeDetector

# Detect forest changes
detector = ChangeDetector()

changes = detector.detect(
    area=study_area,
    start_date="2020-01-01",
    end_date="2025-12-31")

print(f"Forest loss: {changes.loss_hectares} ha")
print(f"Forest gain: {changes.gain_hectares} ha")```

### 3. Fire Risk

```python
from geo_infer_forest import FireRisk

# Assess fire risk
risk = FireRisk()

assessment = risk.assess(
    area=wildland_area,
    weather=current_weather,
    fuel_data=fuel_model)

print(f"Fire danger: {assessment.danger_rating}")```

### 4. Carbon Accounting

```python
from geo_infer_forest import CarbonAccounting

# Estimate carbon stocks
carbon = CarbonAccounting()

stocks = carbon.estimate(
    forest_area=forest_boundary,
    pools=["above_ground", "below_ground", "soil"])

print(f"Total carbon: {stocks.total_tonnes} tC")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Inventory** | ✅ Ready | Biomass, structure |
| **Change Detection** | ✅ Ready | Deforestation monitoring |
| **Fire Risk** | ✅ Ready | Fire danger assessment |
| **Carbon** | ✅ Ready | Carbon accounting |

### Aspirational Features

- 🔮 **ForestMonitorAgent**: Continuous monitoring
- 🔮 **FirePredictionAgent**: Fire spread prediction

---

This AGENTS.md documents how GEO-INFER-FOREST provides forest capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
