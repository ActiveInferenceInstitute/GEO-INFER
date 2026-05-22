# GEO-INFER-IOT/tests/integration

Integration workspace within `GEO-INFER-IOT`.

## Contents

- `test_iot_integration.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-IOT`
- Package: `geo_infer_iot`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-IOT`
- Tests: `uv run python -m pytest GEO-INFER-IOT/tests/integration`

## Dependencies

- `aiocoap>=0.4.3`
- `asyncio-mqtt>=0.11.0`
- `confluent-kafka>=1.8.0`
- `fastapi>=0.68.0`
- `folium>=0.12.0`
- `geopandas>=0.10.0`
- `h3>=4.0.0`
- `influxdb-client>=1.24.0`
- `matplotlib>=3.5.0`
- `numpy>=1.20.0`
- `paho-mqtt>=1.6.0`
- `pandas>=1.3.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-IOT/tests/integration
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
