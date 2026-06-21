# GEO-INFER-EMERGENCY/tests

Tests workspace within `GEO-INFER-EMERGENCY`.

## Contents

- `integration/`
- `conftest.py`
- `test_awareness.py`
- `test_coordinator.py`
- `test_evacuation.py`
- `test_evacuation_sar.py`
- `test_resources.py`
- `test_sar.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:hazard_zone_gdf` (function)
- `conftest.py:shelter_locations_gdf` (function)
- `conftest.py:emergency_config` (function)

## Module Metadata

- Module: `GEO-INFER-EMERGENCY`
- Package: `geo_infer_emergency`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EMERGENCY`
- Tests: `uv run python -m pytest GEO-INFER-EMERGENCY/tests`

## Dependencies

- Dependencies are declared in `pyproject.toml` or inherited from the workspace.

## Validation

```bash
uv run python -m pytest GEO-INFER-EMERGENCY/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
