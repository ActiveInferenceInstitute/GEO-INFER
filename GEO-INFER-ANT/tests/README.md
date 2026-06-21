# GEO-INFER-ANT/tests

Tests workspace within `GEO-INFER-ANT`.

## Contents

- `integration/`
- `performance/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:pytest_configure` (function)
- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:distance_matrix` (function)
- `conftest.py:pheromone_grid` (function)
- `conftest.py:ant_colony_config` (function)

## Module Metadata

- Module: `GEO-INFER-ANT`
- Package: `geo_infer_ant`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ANT`
- Tests: `uv run python -m pytest GEO-INFER-ANT/tests`

## Dependencies

- `asyncio-mqtt>=0.11.0`
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
uv run python -m pytest GEO-INFER-ANT/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
