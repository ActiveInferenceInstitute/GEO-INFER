---
title: "GEO-INFER-AG: Precision Agriculture"
description: "Crop monitoring, soil analysis, yield prediction, and farm management"
purpose: "Enable precision agriculture through geospatial analytics and sensing"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["SPACE", "TIME", "DATA", "IOT"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-IOT"]
tags: ["agriculture", "precision-farming", "crops", "soil", "yield"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-AG: Precision Agriculture

## Overview

**GEO-INFER-AG** provides precision agriculture capabilities:

- **Crop Monitoring**: Health assessment via remote sensing
- **Soil Analysis**: Soil property mapping and recommendations
- **Yield Prediction**: ML-based yield forecasting
- **Variable Rate**: Precision input application

## Features

### Crop Health Monitoring

```python
from geo_infer_ag import CropMonitor

# Monitor crop health
monitor = CropMonitor()

health = monitor.assess(
    field=field_boundary,
    imagery=satellite_data,
    indices=["ndvi", "ndre", "evi"]
)

print(f"Health status: {health.status}")
print(f"Stress zones: {health.stress_areas}")
print(f"Recommendations: {health.recommendations}")
```

### Soil Mapping

```python
from geo_infer_ag import SoilAnalyzer

# Analyze soil properties
soil = SoilAnalyzer()

analysis = soil.map(
    samples=soil_samples,
    properties=["ph", "nitrogen", "organic_matter"],
    interpolation="kriging"
)

print(f"Soil zones: {analysis.zones}")
print(f"Amendments needed: {analysis.recommendations}")
```

### Yield Prediction

```python
from geo_infer_ag import YieldForecaster

# Predict crop yield
forecaster = YieldForecaster()

prediction = forecaster.predict(
    field=field_boundary,
    crop="corn",
    weather_forecast=nws_data,
    historical_yields=yield_history
)

print(f"Expected yield: {prediction.tonnes_ha} t/ha")
print(f"Confidence: {prediction.confidence}%")
```

### Variable Rate Application

```python
from geo_infer_ag import VariableRatePlanner

# Plan variable rate application
planner = VariableRatePlanner()

prescription = planner.create(
    field=field_boundary,
    input_type="fertilizer",
    soil_data=soil_analysis,
    yield_goal=target_yield
)

print(f"Application map generated")
prescription.export("prescription.shp")
```

## Crop Indices

| Index | Application |
|-------|-------------|
| **NDVI** | Overall health |
| **NDRE** | Chlorophyll content |
| **EVI** | Dense vegetation |
| **NDMI** | Water stress |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-IOT** | Sensor data |
| **GEO-INFER-CLIMATE** | Weather data |
| **GEO-INFER-WATER** | Irrigation |

## Installation

```bash
uv pip install -e "./GEO-INFER-AG"
```

## Use Cases

### Precision Irrigation

```python
from geo_infer_ag import IrrigationPlanner

planner = IrrigationPlanner()

schedule = planner.create(
    field=field,
    soil_moisture=sensor_data,
    weather=forecast,
    crop_stage="flowering"
)
```

---

**Status**: Alpha

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
