# GEO-INFER-COG/examples

Examples workspace within `GEO-INFER-COG`.

## Contents

- `__init__.py`
- `cognitive_processing_demo.py`
- `cognitive_wayfinding.py`

## Public Interface

- `cognitive_processing_demo.py:create_sample_spatial_data` (function)
- `cognitive_processing_demo.py:create_sample_user_profile` (function)
- `cognitive_processing_demo.py:demonstrate_cognitive_processing` (function)
- `cognitive_processing_demo.py:demonstrate_spatial_language_processing` (function)
- `cognitive_processing_demo.py:demonstrate_cognitive_map_creation` (function)
- `cognitive_processing_demo.py:demonstrate_user_profiling` (function)
- `cognitive_processing_demo.py:create_visualization_demo` (function)
- `cognitive_processing_demo.py:main` (function)
- `cognitive_wayfinding.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-COG`
- Package: `geo_infer_cog`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-COG`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module COG`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module COG
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
