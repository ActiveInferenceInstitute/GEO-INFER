# GEO-INFER-MATH/tests

Tests workspace within `GEO-INFER-MATH`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:spatial_weight_matrix` (function)
- `conftest.py:coordinate_pairs` (function)
- `conftest.py:graph_adjacency` (function)
- `conftest.py:symmetric_positive_definite_matrix` (function)

## Module Metadata

- Module: `GEO-INFER-MATH`
- Package: `geo_infer_math`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-MATH`
- Tests: `uv run python -m pytest GEO-INFER-MATH/tests`

## Dependencies

- `numpy>=1.20.0`
- `scipy>=1.7.0`
- `pandas>=1.3.0`
- `psutil>=5.8.0`
- `scikit-learn>=1.0.0`
- `sympy>=1.9.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-MATH/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
