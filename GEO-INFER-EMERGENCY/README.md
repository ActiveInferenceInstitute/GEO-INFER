# GEO-INFER-EMERGENCY

Emergency management and disaster response capabilities for geospatial systems.

## Contents

- `docs/`
- `examples/`
- `src/`
- `tests/`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-EMERGENCY`
- Package: `geo_infer_emergency`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-EMERGENCY`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module EMERGENCY`

## Dependencies

- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `geopandas>=0.10.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module EMERGENCY
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
