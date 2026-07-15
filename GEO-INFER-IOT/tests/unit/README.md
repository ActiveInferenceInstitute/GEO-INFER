# GEO-INFER-IOT/tests/unit

Unit workspace within `GEO-INFER-IOT`.

## Contents

- `test_data_ingestion.py`
- `test_ingestion.py`
- `test_performance_monitor.py`
- `test_quality_control.py`
- `test_radiation_monitoring.py`
- `test_registry.py`
- `test_sensor_data.py`
- `test_visualization.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-IOT`
- Package: `geo_infer_iot`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-IOT`
- Tests: `uv run python -m pytest GEO-INFER-IOT/tests/unit`

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
uv run python -m pytest GEO-INFER-IOT/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
