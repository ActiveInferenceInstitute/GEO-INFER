# GEO-INFER-NORMS/tests

Tests workspace within `GEO-INFER-NORMS`.

## Contents

- `integration/`
- `test-outputs/`
- `unit/`
- `conftest.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:normative_rules` (function)
- `conftest.py:compliance_data` (function)
- `conftest.py:norms_config` (function)

## Module Metadata

- Module: `GEO-INFER-NORMS`
- Package: `geo_infer_norms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-NORMS`
- Tests: `uv run python -m pytest GEO-INFER-NORMS/tests`

## Dependencies

- `geopandas>=0.10.0`
- `matplotlib>=3.4.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `shapely>=1.8.0`

## Validation

```bash
uv run python -m pytest GEO-INFER-NORMS/tests
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
