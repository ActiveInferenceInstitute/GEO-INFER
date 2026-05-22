# GEO-INFER-OPS/examples

Examples workspace within `GEO-INFER-OPS`.

## Contents

- `demo_framework.py`
- `geo_infer_paths.py`
- `setup_framework.py`

## Public Interface

- `demo_framework.py:demo_space_module` (function)
- `demo_framework.py:demo_place_module` (function)
- `demo_framework.py:demo_iot_module` (function)
- `demo_framework.py:demo_cross_module_integration` (function)
- `demo_framework.py:demo_framework_entry_point` (function)
- `demo_framework.py:main` (function)
- `geo_infer_paths.py:GEOINFERPathManager` (class)
- `geo_infer_paths.py:get_path_manager` (function)
- `geo_infer_paths.py:add_module_paths` (function)
- `geo_infer_paths.py:add_all_paths` (function)
- `geo_infer_paths.py:import_module` (function)
- `geo_infer_paths.py:import_from_module` (function)
- `geo_infer_paths.py:list_available_modules` (function)
- `geo_infer_paths.py:is_module_installed` (function)
- `setup_framework.py:GEOINFERInstaller` (class)
- `setup_framework.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-OPS`
- Package: `geo_infer_ops`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-OPS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module OPS`

## Dependencies

- `pyyaml>=6.0`
- `fastapi>=0.100.0`
- `uvicorn>=0.21.0`
- `prometheus-client>=0.16.0`
- `structlog>=23.1.0`
- `pytest>=7.3.1`
- `docker>=6.0.1`
- `kubernetes>=26.1.0`
- `black>=23.3.0`
- `isort>=5.12.0`
- `flake8>=6.0.0`
- `pytest-cov>=4.1.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module OPS
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
