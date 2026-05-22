# GEO-INFER-GIT/examples

Examples workspace within `GEO-INFER-GIT`.

## Contents

- `integration_with_ai.py`
- `integration_with_data.py`

## Public Interface

- `integration_with_ai.py:setup_ai_research_integration` (function)
- `integration_with_ai.py:discover_ai_research_repositories` (function)
- `integration_with_ai.py:analyze_model_compatibility` (function)
- `integration_with_ai.py:integrate_with_ai_module` (function)
- `integration_with_ai.py:create_model_catalog` (function)
- `integration_with_ai.py:main` (function)
- `integration_with_data.py:setup_geospatial_data_integration` (function)
- `integration_with_data.py:discover_geospatial_datasets` (function)
- `integration_with_data.py:integrate_with_data_module` (function)
- `integration_with_data.py:cleanup_and_maintenance` (function)
- `integration_with_data.py:main` (function)

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
