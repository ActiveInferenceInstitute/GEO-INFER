# GEO-INFER-WATER: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-WATER** module provides water resources capabilities for agents, enabling hydrological analysis, water quality monitoring, and watershed management.

## Agent Capabilities

### 1. Watershed Analysis

```python
from geo_infer_water import WatershedAnalyzer

# Delineate watershed
analyzer = WatershedAnalyzer()

watershed = analyzer.delineate(
    dem=elevation_data,
    pour_point=(lat, lon)
)

print(f"Area: {watershed.area_km2} km²")
print(f"Stream length: {watershed.stream_km} km")
```

### 2. Flood Modeling

```python
from geo_infer_water import FloodModeler

# Model flood scenarios
modeler = FloodModeler()

flood = modeler.simulate(
    dem=terrain,
    scenario="100_year"
)

print(f"Inundation area: {flood.area_km2} km²")
print(f"Max depth: {flood.max_depth} m")
```

### 3. Water Quality

```python
from geo_infer_water import WaterQualityMonitor

# Monitor water quality
monitor = WaterQualityMonitor()

quality = monitor.assess(
    water_body=lake,
    parameters=["ph", "do", "turbidity"]
)

print(f"WQI: {quality.index}")
```

### 4. Groundwater

```python
from geo_infer_water import GroundwaterAnalyzer

# Analyze groundwater
gw = GroundwaterAnalyzer()

analysis = gw.analyze(
    aquifer=aquifer_boundary,
    wells=monitoring_wells
)

print(f"Depth to water: {analysis.depth} m")
```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Watershed** | ✅ Ready | Delineation, flow |
| **Flood** | ✅ Ready | Inundation modeling |
| **Quality** | ✅ Ready | WQ monitoring |
| **Groundwater** | ✅ Ready | Aquifer analysis |

### Aspirational Features

- 🔮 **WaterManagerAgent**: Resource optimization
- 🔮 **FloodWarningAgent**: Real-time alerts

---

**Last Updated**: 2026-01-26
