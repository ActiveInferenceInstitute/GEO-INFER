# GEO-INFER-SIM/src/geo_infer_sim/core

Core workspace within `GEO-INFER-SIM`.

## Contents

- `__init__.py`
- `simulation_engine.py`

## Public Interface

- `simulation_engine.py:SimulationState` (class)
- `simulation_engine.py:SimulationConfig` (class)
- `simulation_engine.py:SimulationEngine` (class)

## Module Metadata

- Module: `GEO-INFER-SIM`
- Package: `geo_infer_sim`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SIM`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SIM`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SIM
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
