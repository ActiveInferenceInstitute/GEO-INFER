# GEO-INFER-TIME: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-TIME** module provides temporal analysis capabilities for agents, enabling time series analysis, forecasting, and spatiotemporal modeling.

## Agent Capabilities

### 1. Time Series Analysis

```python
from geo_infer_time import TimeSeriesAnalyzer

# Analyze time series data
analyzer = TimeSeriesAnalyzer()

analysis = analyzer.analyze(
    data=sensor_readings,
    frequency="hourly",
    decompose=True)

print(f"Trend: {analysis.trend}")
print(f"Seasonality: {analysis.seasonal_period}")
print(f"Anomalies: {analysis.anomalies}")```

### 2. Forecasting

```python
from geo_infer_time import Forecaster

# Forecast future values
forecaster = Forecaster()

forecast = forecaster.predict(
    data=historical_data,
    horizon=30,
    method="prophet",
    confidence=0.95)

print(f"Forecast: {forecast.values}")
print(f"Uncertainty: {forecast.confidence_interval}")```

### 3. Temporal Pattern Mining

```python
from geo_infer_time import PatternMiner

# Find temporal patterns
miner = PatternMiner()

patterns = miner.find(
    data=activity_data,
    pattern_types=["periodic", "sequential", "burst"])

print(f"Daily patterns: {patterns.daily}")
print(f"Weekly patterns: {patterns.weekly}")```

### 4. Event Detection

```python
from geo_infer_time import EventDetector

# Detect events in time series
detector = EventDetector()

events = detector.detect(
    data=monitoring_data,
    methods=["change_point", "anomaly", "threshold"])

print(f"Events detected: {len(events)}")
print(f"Significant events: {events.significant}")```

## Implementation Status

| Feature | Status | Description |
|---------|--------|-------------|
| **Time Series** | ✅ Ready | Analysis, decomposition |
| **Forecasting** | ✅ Ready | ML-based prediction |
| **Patterns** | ✅ Ready | Pattern discovery |
| **Events** | ✅ Ready | Change detection |

### Aspirational Features

- 🔮 **ForecastAgent**: Autonomous prediction
- 🔮 **TrendAgent**: Trend monitoring

---

This AGENTS.md documents how GEO-INFER-TIME provides temporal capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
