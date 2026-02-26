# GEO-INFER-TRANSPORT: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-TRANSPORT** module provides transportation analysis capabilities for agents, enabling network analysis, traffic modeling, and mobility planning.

## Agent Capabilities

### 1. Network Analysis

```python
from geo_infer_transport import NetworkAnalyzer

# Analyze transport network
analyzer = NetworkAnalyzer()

route = analyzer.find_route(
    origin=(37.77, -122.41),
    destination=(37.80, -122.27),
    mode="car")

print(f"Distance: {route.distance_km} km")
print(f"Duration: {route.duration_min} min")```

### 2. Traffic Modeling

```python
from geo_infer_transport import TrafficModeler

# Model traffic flow
modeler = TrafficModeler()

flow = modeler.simulate(
    network=road_network,
    demand=od_matrix,
    time_period="peak")

print(f"Congestion: {flow.congestion_index}")
print(f"Bottlenecks: {flow.bottlenecks}")```

### 3. Transit Planning

```python
from geo_infer_transport import TransitPlanner

# Plan transit routes
planner = TransitPlanner()

coverage = planner.analyze_coverage(
    routes=gtfs_data,
    population=census_data)

print(f"Coverage: {coverage.percent}%")```

### 4. Demand Forecast

```python
from geo_infer_transport import DemandForecaster

# Forecast travel demand
forecaster = DemandForecaster()

forecast = forecaster.predict(
    historical=traffic_counts,
    scenario="growth")

print(f"Projected VMT: {forecast.vmt}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Network** | ✅ Ready | Routing, analysis |
| **Traffic** | ✅ Ready | Flow simulation |
| **Transit** | ✅ Ready | Coverage, GTFS |
| **Demand** | ✅ Ready | Forecasting |

### Aspirational Features

- 🔮 **TrafficAgent**: Real-time optimization
- 🔮 **RoutingAgent**: Dynamic routing

---

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
