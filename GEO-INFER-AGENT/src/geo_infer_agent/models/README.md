# GEO-INFER-AGENT/src/geo_infer_agent/models

Models workspace within `GEO-INFER-AGENT`.

## Contents

- `bdi/`
- `schemas/`
- `__init__.py`
- `active_inference.py`
- `bdi.py`
- `hybrid.py`
- `rl.py`
- `rule_based.py`

## Public Interface

- `active_inference.py:GenerativeModel` (class)
- `active_inference.py:ActiveInferenceState` (class)
- `active_inference.py:ActiveInferenceAgent` (class)
- `hybrid.py:SubAgentWrapper` (class)
- `hybrid.py:HybridState` (class)
- `hybrid.py:HybridAgent` (class)
- `rl.py:Experience` (class)
- `rl.py:QTable` (class)
- `rl.py:ReplayBuffer` (class)
- `rl.py:RLState` (class)
- `rl.py:RLAgent` (class)
- `rule_based.py:Rule` (class)
- `rule_based.py:RuleSet` (class)
- `rule_based.py:RuleBasedState` (class)
- `rule_based.py:RuleBasedAgent` (class)

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
