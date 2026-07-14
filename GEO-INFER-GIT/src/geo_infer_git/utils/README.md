# GEO-INFER-GIT/src/geo_infer_git/utils

Utils workspace within `GEO-INFER-GIT`.

## Contents

- `__init__.py`
- `advanced_cache.py`
- `config_loader.py`
- `error_handler.py`
- `logging_utils.py`
- `observability.py`
- `performance.py`
- `validation.py`

## Public Interface

- `advanced_cache.py:CacheEntry` (class)
- `advanced_cache.py:CacheStatistics` (class)
- `advanced_cache.py:CachePolicy` (class)
- `advanced_cache.py:LRUPolicy` (class)
- `advanced_cache.py:LFUPolicy` (class)
- `advanced_cache.py:TTLPolicy` (class)
- `advanced_cache.py:AdaptivePolicy` (class)
- `advanced_cache.py:MemoryCache` (class)
- `advanced_cache.py:DiskCache` (class)
- `advanced_cache.py:RedisCache` (class)
- `advanced_cache.py:MultiLevelCache` (class)
- `advanced_cache.py:IntelligentCache` (class)
- `advanced_cache.py:create_optimized_cache` (function)
- `advanced_cache.py:CacheDecorator` (class)
- `config_loader.py:CloneConfig` (class)
- `config_loader.py:TargetRepository` (class)
- `config_loader.py:TargetUser` (class)
- `config_loader.py:ConfigLoader` (class)
- `config_loader.py:load_clone_config` (function)
- `config_loader.py:load_target_repos_config` (function)

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
