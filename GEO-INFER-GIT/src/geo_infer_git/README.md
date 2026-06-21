# GEO-INFER-GIT/src/geo_infer_git

Geo Infer Git workspace within `GEO-INFER-GIT`.

## Contents

- `api/`
- `core/`
- `utils/`
- `__init__.py`
- `cli.py`
- `main.py`

## Public Interface

- `cli.py:setup_logging` (function)
- `cli.py:load_repo_list` (function)
- `cli.py:clone_command` (function)
- `cli.py:sync_command` (function)
- `cli.py:status_command` (function)
- `cli.py:branch_command` (function)
- `cli.py:main` (function)
- `main.py:parse_arguments` (function)
- `main.py:create_gitignore_entry` (function)
- `main.py:generate_report` (function)
- `main.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-GIT`
- Package: `geo_infer_git`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-GIT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module GIT`

## Dependencies

- `requests>=2.28.1`
- `pyyaml>=6.0`
- `psutil>=5.9.0`
- `jsonschema>=4.17.0`
- `GitPython>=3.1.0`
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `pydantic>=2.5.0`
- `pytest>=7.3.1`
- `black>=23.3.0`
- `flake8>=6.0.0`
- `mypy>=1.3.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module GIT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
