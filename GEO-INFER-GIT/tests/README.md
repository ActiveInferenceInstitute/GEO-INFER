# GEO-INFER-GIT/tests

Tests workspace within `GEO-INFER-GIT`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:sample_repo_path` (function)
- `conftest.py:commit_metadata_list` (function)
- `conftest.py:git_config` (function)

## Module Metadata

- Module: `GEO-INFER-GIT`
- Package: `geo_infer_git`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-GIT`
- Tests: `uv run python -m pytest GEO-INFER-GIT/tests`

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
uv run python -m pytest GEO-INFER-GIT/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
