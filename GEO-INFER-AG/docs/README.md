# GEO-INFER-AG/docs

Docs workspace within `GEO-INFER-AG`.

## Contents

- `api_schema.yaml`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-AG`
- Package: `geo_infer_ag`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module AG`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`
- `scikit-learn>=1.0.0`
- `rasterio>=1.2.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AG
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
