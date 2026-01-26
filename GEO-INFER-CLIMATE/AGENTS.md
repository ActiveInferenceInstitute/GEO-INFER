# GEO-INFER-CLIMATE: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-CLIMATE** module provides climate analysis capabilities for agents, enabling weather data integration, climate modeling, and climate change impact assessment.

## Agent Capabilities

### 1. Weather Data Access

```python
from geo_infer_climate import WeatherService

# Access weather data
weather = WeatherService()

# Get current conditions
current = weather.get_current(
    location=(37.77, -122.41),
    parameters=["temperature", "precipitation", "wind"]
)

# Get forecast
forecast = weather.get_forecast(
    location=(37.77, -122.41),
    hours_ahead=72
)

print(f"Current temp: {current.temperature}°C")
print(f"Rain probability: {forecast[0].precipitation_prob}%")
```

### 2. Climate Projections

```python
from geo_infer_climate import ClimateProjector

# Access climate projections
projector = ClimateProjector()

projection = projector.get_projection(
    region=study_area,
    scenario="ssp245",  # SSP2-4.5
    time_period=("2040", "2060"),
    variables=["temperature", "precipitation"]
)

print(f"Projected warming: {projection.temp_change}°C")
print(f"Precip change: {projection.precip_change}%")
```

### 3. Climate Risk Analysis

```python
from geo_infer_climate import ClimateRiskAnalyzer

# Analyze climate risks
analyzer = ClimateRiskAnalyzer()

risk = analyzer.assess(
    assets=infrastructure_locations,
    hazards=["sea_level_rise", "extreme_heat", "flooding"],
    time_horizon=2050
)

print(f"High risk assets: {risk.high_risk_count}")
print(f"Adaptation needs: {risk.recommendations}")
```

### 4. Historical Analysis

```python
from geo_infer_climate import HistoricalAnalyzer

# Analyze historical climate
historical = HistoricalAnalyzer()

trends = historical.analyze(
    region=city_boundary,
    period=("1990", "2025"),
    metrics=["mean_temp", "extreme_heat_days", "precipitation"]
)

print(f"Warming trend: {trends.temp_trend}°C/decade")
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Weather Data** | ✅ Ready | Real-time weather |
| **Projections** | ✅ Ready | CMIP6 scenarios |
| **Risk Analysis** | ✅ Ready | Climate risk |
| **Historical** | ✅ Ready | Trend analysis |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **ClimateAdvisorAgent** | 🔮 High | Adaptation guidance |
| **ExtremeWeatherAgent** | 🔮 High | Event prediction |

## Use Cases

### Climate Adaptation Planning

```python
from geo_infer_climate import AdaptationPlanner

planner = AdaptationPlanner(city="metropolis")

plan = planner.develop_plan(
    risks=["urban_heat", "flooding"],
    strategies=["green_infrastructure", "resilient_design"],
    budget=50_000_000
)
```

---

This AGENTS.md documents how GEO-INFER-CLIMATE provides climate capabilities for agents.

**Last Updated**: 2026-01-26
