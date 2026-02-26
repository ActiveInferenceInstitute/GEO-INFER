# GEO-INFER-MARINE: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-MARINE** module provides marine analysis capabilities for agents, including ocean monitoring, coastal analysis, and fisheries management.

## Agent Capabilities

### 1. Ocean Monitoring

```python
from geo_infer_marine import OceanMonitor

# Monitor ocean conditions
monitor = OceanMonitor()

conditions = monitor.get(
    area=study_area,
    parameters=["sst", "chlorophyll", "currents"])

print(f"SST: {conditions.sst}°C")
print(f"Chlorophyll: {conditions.chl} mg/m³")```

### 2. Coastal Analysis

```python
from geo_infer_marine import CoastalAnalyzer

# Analyze coastal dynamics
coastal = CoastalAnalyzer()

erosion = coastal.analyze(
    shoreline=coastline,
    period=("2000", "2025"))

print(f"Erosion rate: {erosion.rate} m/year")```

### 3. Marine Spatial Planning

```python
from geo_infer_marine import MarinePlanner

# Create marine spatial plan
planner = MarinePlanner()

plan = planner.create(
    area=eez,
    uses=["fishing", "shipping", "conservation"])
```

### 4. Fisheries Analysis

```python
from geo_infer_marine import FisheriesAnalyzer

# Analyze fisheries
fisheries = FisheriesAnalyzer()

stock = fisheries.assess(
    species="cod",
    area=fishing_grounds)

print(f"Stock status: {stock.status}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Ocean** | ✅ Ready | SST, currents |
| **Coastal** | ✅ Ready | Erosion, inundation |
| **MSP** | ✅ Ready | Zone planning |
| **Fisheries** | ✅ Ready | Stock assessment |

### Aspirational Features

- 🔮 **OceanSentinelAgent**: Real-time monitoring
- 🔮 **FisheriesAgent**: Sustainable quotas

---

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
