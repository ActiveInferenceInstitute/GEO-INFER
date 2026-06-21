# GEO-INFER-PLACE/tests

Tests workspace within `GEO-INFER-PLACE`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:del_norte_bbox` (function)
- `conftest.py:sample_h3_cells` (function)
- `conftest.py:temp_output_dir` (function)
- `conftest.py:minimal_config` (function)

## Module Metadata

- Module: `GEO-INFER-PLACE`
- Package: `geo_infer_place`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PLACE`
- Tests: `uv run python -m pytest GEO-INFER-PLACE/tests`

## Dependencies

- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `h3>=4.5.0,<5`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `pyyaml>=6.0`
- `folium>=0.14.0`
- `plotly>=5.0.0`
- `matplotlib>=3.5.0`
- `seaborn>=0.12.0`
- `branca>=0.6.0`
- `requests>=2.28.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-PLACE/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
