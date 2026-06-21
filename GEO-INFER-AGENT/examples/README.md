# GEO-INFER-AGENT/examples

Examples workspace within `GEO-INFER-AGENT`.

## Contents

- `active_inference_geospatial.py`
- `agent_examples.py`
- `simple_agent_example.py`

## Public Interface

- `active_inference_geospatial.py:GeospatialEnvironment` (class)
- `active_inference_geospatial.py:GeospatialActiveInferenceAgent` (class)
- `active_inference_geospatial.py:main` (function)
- `agent_examples.py:MockSensor` (class)
- `agent_examples.py:run_bdi_agent_example` (function)
- `agent_examples.py:run_active_inference_agent_example` (function)
- `agent_examples.py:run_rl_agent_example` (function)
- `agent_examples.py:run_rule_based_agent_example` (function)
- `agent_examples.py:run_hybrid_agent_example` (function)
- `agent_examples.py:main` (function)
- `simple_agent_example.py:run_simple_agent` (function)
- `simple_agent_example.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-AGENT`
- Package: `geo_infer_agent`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-AGENT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT`

## Dependencies

- `numpy>=1.23.5`
- `torch>=2.0.0`
- `pyyaml>=6.0`
- `tqdm>=4.65.0`
- `requests>=2.28.2`
- `colorlog>=6.7.0`
- `pytest>=7.3.1`
- `pytest-cov>=4.1.0`
- `mypy>=1.3.0`
- `black>=23.3.0`
- `isort>=5.12.0`
- `matplotlib>=3.7.1`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
