# GEO-INFER-ANT/examples

Examples workspace within `GEO-INFER-ANT`.

## Contents

- `swarm_intelligence_demo.py`

## Public Interface

- `swarm_intelligence_demo.py:generate_sample_data` (function)
- `swarm_intelligence_demo.py:demonstrate_swarm_agents` (function)
- `swarm_intelligence_demo.py:demonstrate_population_dynamics` (function)
- `swarm_intelligence_demo.py:demonstrate_stigmergic_communication` (function)
- `swarm_intelligence_demo.py:demonstrate_optimization_algorithms` (function)
- `swarm_intelligence_demo.py:demonstrate_environmental_monitoring` (function)
- `swarm_intelligence_demo.py:demonstrate_pattern_analysis` (function)
- `swarm_intelligence_demo.py:run_complete_demonstration` (function)
- `swarm_intelligence_demo.py:main` (function)

## Module Metadata

- Module: `GEO-INFER-ANT`
- Package: `geo_infer_ant`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-ANT`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT`

## Dependencies

- `asyncio-mqtt>=0.11.0`
- `geopandas>=0.10.0`
- `h3>=4.5.0,<5`
- `jsonschema>=4.0.0`
- `matplotlib>=3.5.0`
- `networkx>=2.8`
- `numpy>=1.21.0`
- `pyyaml>=6.0`
- `scikit-learn>=1.1.0`
- `scipy>=1.7.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ANT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
