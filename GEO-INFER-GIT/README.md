# GEO-INFER-GIT

Version control and repository management tools specifically designed for geospatial data and code collaboration.

## Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `clone_repos.py`
- `clone_script.py`
- `setup.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- `clone_script.py:load_yaml_config` (function)
- `clone_script.py:get_github_repo_info` (function)
- `clone_script.py:clone_repository` (function)
- `clone_script.py:main` (function)
- `clone_script.py:match_wildcard` (function)

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
