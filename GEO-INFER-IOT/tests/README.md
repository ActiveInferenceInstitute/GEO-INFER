# GEO-INFER-IOT/tests

Tests workspace within `GEO-INFER-IOT`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `requirements-test.txt`
- `run_tests.sh`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:sensor_readings` (function)
- `conftest.py:iot_config` (function)
- `conftest.py:sensor_network_gdf` (function)

## Module Metadata

- Module: `GEO-INFER-IOT`
- Package: `geo_infer_iot`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-IOT`
- Tests: `uv run python -m pytest GEO-INFER-IOT/tests`

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
uv run python -m pytest GEO-INFER-IOT/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
