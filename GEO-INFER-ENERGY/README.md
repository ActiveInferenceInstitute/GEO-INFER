# GEO-INFER-ENERGY

Energy systems analysis, renewable energy optimization, and grid management.

## Contents

- `.test-results/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-ENERGY`
- Package: `geo_infer_energy`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ENERGY`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ENERGY`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`
- `matplotlib>=3.4.0`
- `xarray>=0.19.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.0.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ENERGY
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
