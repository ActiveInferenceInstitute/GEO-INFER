# GEO-INFER-IOT/src/geo_infer_iot/models

Models workspace within `GEO-INFER-IOT`.

## Contents

- `measurement.py`
- `network.py`
- `sensor.py`

## Public Interface

- `measurement.py:MeasurementQuality` (class)
- `measurement.py:Measurement` (class)
- `measurement.py:MeasurementBatch` (class)
- `measurement.py:MeasurementStream` (class)
- `measurement.py:MeasurementValidation` (class)
- `network.py:NetworkTopologyType` (class)
- `network.py:CommunicationProtocol` (class)
- `network.py:NetworkNode` (class)
- `network.py:NetworkLink` (class)
- `network.py:NetworkTopology` (class)
- `network.py:NetworkEvent` (class)
- `network.py:NetworkConfiguration` (class)
- `network.py:NetworkPerformance` (class)
- `sensor.py:Location` (class)
- `sensor.py:SensorCapabilities` (class)
- `sensor.py:SensorCalibration` (class)
- `sensor.py:Sensor` (class)
- `sensor.py:SensorNetwork` (class)
- `sensor.py:SensorDeployment` (class)

## Module Metadata

- Module: `GEO-INFER-IOT`
- Package: `geo_infer_iot`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-IOT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module IOT`

## Dependencies

- `aiocoap>=0.4.3`
- `aiomqtt>=2.4.0`
- `confluent-kafka>=1.8.0`
- `fastapi>=0.68.0`
- `folium>=0.12.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `influxdb-client>=1.24.0`
- `matplotlib>=3.5.0`
- `numpy>=1.20.0`
- `paho-mqtt>=1.6.0`
- `pandas>=1.3.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module IOT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
