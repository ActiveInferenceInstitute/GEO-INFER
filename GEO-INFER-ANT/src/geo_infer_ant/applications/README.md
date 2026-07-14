# GEO-INFER-ANT/src/geo_infer_ant/applications

Applications workspace within `GEO-INFER-ANT`.

## Contents

- `__init__.py`
- `disaster.py`
- `environmental.py`
- `urban.py`

## Public Interface

- `disaster.py:DisasterScenario` (class)
- `disaster.py:DisasterResponseSwarm` (class)
- `environmental.py:MonitoringObjective` (class)
- `environmental.py:SensorReading` (class)
- `environmental.py:EnvironmentalMonitoringSwarm` (class)
- `urban.py:UrbanSystem` (class)
- `urban.py:UrbanTrafficSwarm` (class)

## Module Metadata

- Module: `GEO-INFER-ANT`
- Package: `geo_infer_ant`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ANT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT`

## Dependencies

- `aiomqtt>=2.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `jsonschema>=4.0.0`
- `matplotlib>=3.5.0`
- `networkx>=2.8`
- `numpy>=1.21.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.1.0`
- `scipy>=1.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
