# GEO-INFER-GIT/src/geo_infer_git/api

Api workspace within `GEO-INFER-GIT`.

## Contents

- `__init__.py`
- `rest_api.py`

## Public Interface

- `rest_api.py:RepositoryRequest` (class)
- `rest_api.py:RepositoryResponse` (class)
- `rest_api.py:CloneRequest` (class)
- `rest_api.py:CloneResponse` (class)
- `rest_api.py:SyncRequest` (class)
- `rest_api.py:SyncResponse` (class)
- `rest_api.py:BranchRequest` (class)
- `rest_api.py:BranchResponse` (class)
- `rest_api.py:MergeRequest` (class)
- `rest_api.py:MergeResponse` (class)
- `rest_api.py:HealthResponse` (class)
- `rest_api.py:SystemStatusResponse` (class)
- `rest_api.py:get_repo_manager` (function)
- `rest_api.py:get_github_api` (function)
- `rest_api.py:get_logger` (function)
- `rest_api.py:health_check` (function)
- `rest_api.py:list_repositories` (function)
- `rest_api.py:add_repository` (function)
- `rest_api.py:get_repository` (function)
- `rest_api.py:clone_repository` (function)

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
- `colorlog>=6.7.0`
- `tqdm>=4.65.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module GIT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
