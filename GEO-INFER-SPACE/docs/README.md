# GEO-INFER-SPACE/docs

Docs workspace within `GEO-INFER-SPACE`.

## Contents

- `references/`
- `CLI_TOOLS.md`
- `H3_DATASET_INTEGRATION_GUIDE.md`
- `H3_DEMO_README.md`
- `H3_MODULE_CONFIGURATION_GUIDE.md`
- `H3_V4_MIGRATION_GUIDE.md`
- `TESTING.md`
- `api_schema.yaml`
- `h3_advanced_methods.md`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.100.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=2.0.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=2.0.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
