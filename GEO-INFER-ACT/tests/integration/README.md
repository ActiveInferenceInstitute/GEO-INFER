# GEO-INFER-ACT/tests/integration

Integration workspace within `GEO-INFER-ACT`.

## Contents

- `test_h3_example_smoke.py`
- `test_integration.py`
- `test_space_integration.py`
- `test_stigmergy.py`

## Public Interface

- No public Python symbols are defined directly in this directory.

## Module Metadata

- Module: `GEO-INFER-ACT`
- Package: `geo_infer_act`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ACT`
- Tests: `uv run python -m pytest GEO-INFER-ACT/tests/integration`

## Dependencies

- `matplotlib>=3.4.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `pyro-ppl>=1.7.0`
- `pyyaml>=6.0`
- `scipy>=1.7.0`
- `torch>=1.9.0`
- `arviz>=0.11.0`
- `bayeux-ml>=0.0.1`
- `h3>=4.5.0,<5`
- `imageio>=2.9.0`


## Validation

```bash
uv run python -m pytest GEO-INFER-ACT/tests/integration
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
