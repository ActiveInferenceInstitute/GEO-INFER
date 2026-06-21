# GEO-INFER-TRANSPORT/tests

Tests workspace within `GEO-INFER-TRANSPORT`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_accessibility.py`
- `test_network_routing.py`
- `test_routing.py`
- `test_traffic.py`
- `test_traffic_transit.py`
- `test_transit.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:road_network_gdf` (function)
- `conftest.py:od_matrix` (function)
- `conftest.py:transport_config` (function)

## Module Metadata

- Module: `GEO-INFER-TRANSPORT`
- Package: `geo_infer_transport`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-TRANSPORT`
- Tests: `uv run python -m pytest GEO-INFER-TRANSPORT/tests`

## Dependencies

- Dependencies are declared in `pyproject.toml` or inherited from the workspace.

## Validation

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
