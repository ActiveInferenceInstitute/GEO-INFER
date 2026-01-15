# GEO-INFER-FOREST: Forest Intelligence Agents

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="../GEO-INFER-INTRA/README.md">📚 Documentation</a>
</div>

---

## Overview


The GEO-INFER-FOREST module provides forest management capabilities enabling agents to monitor forest health, detect deforestation, estimate biomass, and support sustainable forestry.

## Implementation Status

**⚠️ Important Note**: This document describes both **implemented** and **aspirational** features. Features marked with 🔮 are planned/aspirational.

### Currently Implemented

- ✅ **ForestHealthAnalyzer**: Forest condition monitoring
- ✅ **DeforestationDetector**: Change detection and alerts
- ✅ **BiomassEstimator**: Carbon stock estimation
- ✅ **FireRiskAssessor**: Wildfire risk modeling

### Aspirational/Planned Features

- 🔮 **ForestMonitoringAgent**: Autonomous forest surveillance
- 🔮 **FireResponseAgent**: Real-time fire detection and response

## Agent Capabilities Supported

### 1. Forest Health Monitoring

```python
from geo_infer_forest import ForestHealthAnalyzer

# Agent monitors forest health
analyzer = ForestHealthAnalyzer()
health = analyzer.assess(
    imagery=satellite_data,
    indices=['ndvi', 'evi', 'nbr'],
    baseline=reference_period
)
```

### 2. Deforestation Detection

```python
from geo_infer_forest import DeforestationDetector

# Detect forest loss
detector = DeforestationDetector()
changes = detector.detect(
    current=recent_imagery,
    baseline=historical_imagery,
    threshold=0.3
)
```

### 3. Biomass Estimation

```python
from geo_infer_forest import BiomassEstimator

# Estimate carbon stocks
estimator = BiomassEstimator()
biomass = estimator.estimate(
    canopy_height=lidar_data,
    forest_type=species_map,
    method='allometric'
)
```

## Integration Status

| Capability | Status | Description |
|------------|--------|-------------|
| **Forest Health** | ✅ Ready | Condition monitoring |
| **Deforestation** | ✅ Ready | Change detection |
| **Biomass** | ✅ Ready | Carbon estimation |
| **Fire Risk** | ✅ Ready | Wildfire modeling |
| **Monitoring Agent** | 🔮 Planned | Autonomous surveillance |
| **Fire Agent** | 🔮 Planned | Real-time response |

---

This AGENTS.md documents how GEO-INFER-FOREST provides forest management intelligence capabilities.
