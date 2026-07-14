# GEO-INFER-INTRA/scripts/maintenance

Maintenance workspace within `GEO-INFER-INTRA`.

## Contents

- `update_documentation_signposts.py`

## Public Interface

- `update_documentation_signposts.py:get_pkg_name` (function)
- `update_documentation_signposts.py:update_file_signpost` (function)
- `update_documentation_signposts.py:create_agents_md` (function)
- `update_documentation_signposts.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-INTRA`
- Package: `geo_infer_intra`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-INTRA`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA`

## Dependencies

- `fastapi>=0.95.0`
- `pydantic>=2.0.0`
- `sqlalchemy>=2.0.0`
- `elasticsearch>=8.0.0`
- `rdflib>=6.0.0`
- `mkdocs>=1.4.0`
- `celery>=5.2.0`
- `pyyaml>=6.0`
- `jsonschema>=4.0.0`
- `typer>=0.7.0`
- `rich>=12.0.0`
- `uvicorn>=0.20.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
