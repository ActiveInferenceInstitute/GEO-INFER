# GEO-INFER-IOT/src/geo_infer_iot/utils

Utils workspace within `GEO-INFER-IOT`.

## Contents

- `calibration.py`
- `interpolation.py`
- `visualization.py`

## Public Interface

- `calibration.py:CalibrationResult` (class)
- `calibration.py:SensorCalibration` (class)
- `interpolation.py:SpatialInterpolation` (class)
- `visualization.py:IoTVisualization` (class)

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
