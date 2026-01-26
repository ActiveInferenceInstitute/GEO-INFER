---
title: "GEO-INFER-IOT: Internet of Things Integration"
description: "Sensor networks, real-time data streaming, and edge computing"
purpose: "Enable IoT device integration and real-time geospatial data streams"
module_type: "Data Infrastructure"
status: "Beta"
last_updated: "2026-01-26"
dependencies: ["SPACE", "TIME", "DATA"]
compatibility: ["GEO-INFER-SPACE", "GEO-INFER-TIME", "GEO-INFER-DATA"]
tags: ["iot", "sensors", "streaming", "real-time", "edge"]
difficulty: "Intermediate"
estimated_time: "45"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-IOT: Internet of Things Integration

## Overview

**GEO-INFER-IOT** provides IoT capabilities:

- **Sensor Networks**: Device registration and management
- **Data Streaming**: Real-time data subscriptions
- **Edge Processing**: Local analytics on edge devices
- **Device Coordination**: Multi-device campaigns

## Features

### Sensor Network

```python
from geo_infer_iot import SensorNetwork

# Manage sensors
network = SensorNetwork()

network.register(
    sensor_id="temp_001",
    type="temperature",
    location=(37.77, -122.41)
)

status = network.get_status()
print(f"Active: {status.active_count}")
```

### Data Streaming

```python
from geo_infer_iot import DataStreamer

# Stream sensor data
streamer = DataStreamer()

async for reading in streamer.subscribe(
    sensors=["temp_*"],
    area=city_boundary
):
    print(f"Value: {reading.value}")
```

### Edge Processing

```python
from geo_infer_iot import EdgeProcessor

# Deploy edge analytics
processor = EdgeProcessor()

processor.deploy(
    model="anomaly_detection",
    devices=edge_gateways
)
```

### Device Coordination

```python
from geo_infer_iot import DeviceCoordinator

# Coordinate sensing campaign
coordinator = DeviceCoordinator()

campaign = coordinator.run(
    devices=sensor_array,
    objective="coverage"
)
```

## Device Types

| Type | Examples |
|------|----------|
| **Environmental** | Weather, air quality |
| **Traffic** | Counters, cameras |
| **Infrastructure** | Structural, water |
| **Mobile** | GPS, phones |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-DATA** | Data ingestion |
| **GEO-INFER-TIME** | Time series |
| **GEO-INFER-COMMS** | Alerts |

## Installation

```bash
uv pip install -e "./GEO-INFER-IOT"
```

---

**Status**: Beta

**Last Updated**: 2026-01-26
