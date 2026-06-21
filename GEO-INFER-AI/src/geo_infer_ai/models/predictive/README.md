# GEO-INFER-AI/src/geo_infer_ai/models/predictive

Predictive workspace within `GEO-INFER-AI`.

## Contents

- `__init__.py`
- `spatial_predictor.py`

## Public Interface

- `spatial_predictor.py:SpatialPredictor` (class)
- `spatial_predictor.py:IDWInterpolator` (class)
- `spatial_predictor.py:OrdinaryKriging` (class)

## Module Metadata

- Module: `GEO-INFER-AI`
- Package: `geo_infer_ai`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AI`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module AI`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `torch>=1.9.0`
- `tensorflow>=2.6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AI
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
