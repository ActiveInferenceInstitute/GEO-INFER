# GEO-INFER-GIT/tests/unit

Unit workspace within `GEO-INFER-GIT`.

## Contents

- `test_config_loader.py`
- `test_error_handler.py`
- `test_error_recovery_strategies.py`
- `test_github_api.py`
- `test_intelligent_cache_prefetch.py`
- `test_repo_analyzer.py`
- `test_repo_cloner.py`
- `test_repo_manager.py`
- `test_rest_api.py`
- `test_validation.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-GIT`
- Package: `geo_infer_git`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-GIT`
- Tests: `uv run python -m pytest GEO-INFER-GIT/tests/unit`

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
uv run python -m pytest GEO-INFER-GIT/tests/unit
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
