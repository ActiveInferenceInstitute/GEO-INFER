# GEO-INFER-LOG

Geospatial intelligence for logistics optimization, supply chain management, route optimization, and transportation planning.

## Contents

- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-LOG`
- Package: `geo_infer_log`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-LOG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG`

## Dependencies

- `pandas>=1.3.0`
- `geopandas>=0.10.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Visualization Contracts

- Route plotting validates geographic coordinates and preserves the supplied
  path geometry; network highlighting rejects unknown nodes.
- Interactive map zoom and optional map basemaps are validated/guarded so
  plotting remains usable without contextily network access.

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
