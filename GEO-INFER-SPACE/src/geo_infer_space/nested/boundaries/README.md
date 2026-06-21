# GEO-INFER-SPACE/src/geo_infer_space/nested/boundaries

Boundaries workspace within `GEO-INFER-SPACE`.

## Contents

- `__init__.py`
- `boundary_manager.py`
- `detector.py`

## Public Interface

- `boundary_manager.py:BoundaryOperation` (class)
- `boundary_manager.py:FlowDirection` (class)
- `boundary_manager.py:BoundaryFlow` (class)
- `boundary_manager.py:BoundaryConstraint` (class)
- `boundary_manager.py:H3BoundaryManager` (class)
- `detector.py:BoundaryType` (class)
- `detector.py:BoundaryDetectionMethod` (class)
- `detector.py:BoundarySegment` (class)
- `detector.py:BoundaryDetector` (class)

## Module Metadata

- Module: `GEO-INFER-SPACE`
- Package: `geo_infer_space`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-SPACE`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE`

## Dependencies

- `fastapi>=0.68.0`
- `fiona>=1.8.0`
- `geojson-pydantic>=0.4.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `networkx>=2.6.0`
- `numpy>=1.20.0,<2.0`
- `pandas>=1.3.0`
- `pydantic>=1.8.0`
- `pyproj>=3.3.0`
- `python-multipart>=0.0.5`
- `pyyaml>=6.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
