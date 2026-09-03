# GEO-INFER-LOG/tests/unit

Unit workspace within `GEO-INFER-LOG`.

## Contents

- `test_core.py`
- `test_delivery.py`
- `test_geo_utils.py`
- `test_optimization.py`
- `test_supply_chain.py`
- `test_transport.py`
- `test_visualization.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-LOG`
- Package: `geo_infer_log`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-LOG`
- Tests: `uv run python -m pytest GEO-INFER-LOG/tests/unit`

## Dependencies

- `pandas>=1.3.0`
- `geopandas>=0.10.0`
- `networkx>=2.6.0`
- `pulp>=2.7.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python -m pytest GEO-INFER-LOG/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
