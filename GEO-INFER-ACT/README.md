# GEO-INFER-ACT

Advanced Active Inference framework implementing Free Energy Principle for geospatial decision-making, perception, and learning.

## Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `debug_models.py`
- `setup.py`
- `verify_comprehensive.py`
- `verify_pipeline.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

## Public Interface

- `debug_models.py:main` (function)
- `verify_comprehensive.py:audit_active_inference_model` (function)
- `verify_comprehensive.py:audit_generative_model` (function)
- `verify_comprehensive.py:audit_free_energy_and_policy` (function)
- `verify_comprehensive.py:audit_inference_math` (function)
- `verify_comprehensive.py:audit_spatial_agent` (function)
- `verify_comprehensive.py:audit_domain_models` (function)
- `verify_comprehensive.py:audit_api_interface` (function)
- `verify_comprehensive.py:audit_visualization_methods` (function)
- `verify_comprehensive.py:audit_scenario_outputs` (function)
- `verify_comprehensive.py:audit_docs_and_mermaid` (function)
- `verify_comprehensive.py:parse_args` (function)
- `verify_comprehensive.py:main` (function)
- `verify_pipeline.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-ACT`
- Package: `geo_infer_act`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ACT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT`

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
- `h3>=4.0.0`
- `imageio>=2.9.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT
```

## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
