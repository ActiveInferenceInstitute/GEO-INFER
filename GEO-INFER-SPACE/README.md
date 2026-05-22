# GEO-INFER-SPACE

H3 v4 spatial indexing and comprehensive geospatial analysis framework with advanced spatial methods and coordinate transformations.

## Contents

- `docs/`
- `examples/`
- `output/`
- `reports/`
- `scripts/`
- `src/`
- `test_output/`
- `tests/`
- `demo_all_methods.py`
- `verify_installation.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

## Public Interface

- `demo_all_methods.py:success` (function)
- `demo_all_methods.py:info` (function)
- `demo_all_methods.py:section` (function)
- `verify_installation.py:verify_h3_backend` (function)
- `verify_installation.py:verify_srai_backend` (function)
- `verify_installation.py:verify_dispatcher` (function)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

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
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
