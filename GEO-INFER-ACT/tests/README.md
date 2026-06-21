# GEO-INFER-ACT/tests

Tests workspace within `GEO-INFER-ACT`.

## Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_act_models_real.py`

## Public Interface

- `conftest.py:sample_coordinates` (function)
- `conftest.py:sample_geodataframe` (function)
- `conftest.py:tmp_output_dir` (function)
- `conftest.py:free_energy_agent` (function)
- `conftest.py:generative_model_config` (function)
- `conftest.py:observation_sequence` (function)

## Module Metadata

- Module: `GEO-INFER-ACT`
- Package: `geo_infer_act`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ACT`
- Tests: `uv run python -m pytest GEO-INFER-ACT/tests`

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
uv run python -m pytest GEO-INFER-ACT/tests
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
