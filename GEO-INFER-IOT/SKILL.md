---
name: geo-infer-iot
description: IoT sensor data ingestion and real-time streaming for geospatial monitoring. Use when connecting to MQTT brokers, processing sensor streams, validating spatial sensor data quality, or building real-time geospatial monitoring pipelines.
prerequisites:
  required:
    - geo-infer-data
    - geo-infer-time
  recommended:
    - geo-infer-space
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-IOT

## Instructions

### Core Capabilities

- **MQTT ingestion**: Real paho-mqtt connection lifecycle management
- **Streaming**: Async sensor data pipelines
- **Quality control**: Spatial validation, outlier detection, data completeness
- **Device management**: Sensor registry, health monitoring
- **Protocol support**: MQTT, HTTP webhooks, WebSocket

### Key Imports

```python
from geo_infer_iot.core.ingestion import MQTTIngestionEngine
from geo_infer_iot.core.quality_control import SpatialQualityChecker
from geo_infer_iot.core.device_management import DeviceRegistry
```

## Examples

```python
from geo_infer_iot.core.ingestion import MQTTIngestionEngine

engine = MQTTIngestionEngine(broker="mqtt.example.com", port=1883)
engine.subscribe("sensors/temperature/#")

@engine.on_message
def handle_temperature(topic, payload):
    lat, lng = payload["location"]
    temp = payload["value"]
    print(f"Sensor at ({lat}, {lng}): {temp}°C")

engine.start()
```

```python
from geo_infer_iot.core.quality_control import SpatialQualityChecker

checker = SpatialQualityChecker(bounds=(-90, -180, 90, 180))
clean_data = checker.validate(raw_readings)
print(f"Passed: {len(clean_data.valid)}, Rejected: {len(clean_data.outliers)}")
```

## Guidelines

- MQTT handlers use real paho-mqtt (not placeholders)
- Spatial validation includes real geometry checks
- Optional deps load via `try/except` with lightweight fallback adapters for graceful degradation
- Test: `uv run python -m pytest GEO-INFER-IOT/tests/ -v`

### Integrations

- **DATA** → Sensor data feeds into ETL pipelines
- **TIME** → Time-series analysis of sensor streams
- **SPACE** → Spatial indexing of sensor locations
- **OPS** → Monitoring sensor health and uptime
- **COMMS** → Alert broadcasting on sensor thresholds
