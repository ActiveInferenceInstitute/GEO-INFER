# GEO-INFER-SPACE/tests/integration

Integration workspace within `GEO-INFER-SPACE`.

## Contents

- `test_cross_component_workflows.py`
- `test_unified_ml_integration.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python -m pytest GEO-INFER-SPACE/tests/integration`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.0.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-SPACE/tests/integration
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
