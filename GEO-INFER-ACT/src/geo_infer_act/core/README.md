# GEO-INFER-ACT/src/geo_infer_act/core

Core workspace within `GEO-INFER-ACT`.

## Contents

- `__init__.py`
- `active_inference.py`
- `belief_updating.py`
- `dynamic_causal_model.py`
- `free_energy.py`
- `generative_model.py`
- `markov_decision_process.py`
- `policy_selection.py`
- `spatial_agent.py`
- `types.py`
- `variational_inference.py`

## Public Interface

- `active_inference.py:ActiveInferenceModel` (class)
- `belief_updating.py:BayesianBeliefUpdate` (class)
- `dynamic_causal_model.py:DynamicCausalModel` (class)
- `free_energy.py:FreeEnergyCalculator` (class)
- `generative_model.py:MarkovBlanket` (class)
- `generative_model.py:HierarchicalLevel` (class)
- `generative_model.py:GenerativeModel` (class)
- `markov_decision_process.py:MarkovDecisionProcess` (class)
- `policy_selection.py:PolicySelector` (class)
- `spatial_agent.py:SpatialActiveInferenceAgent` (class)
- `types.py:FreeEnergyBreakdown` (class)
- `types.py:PolicyEvaluation` (class)
- `types.py:ActiveInferenceStepResult` (class)
- `types.py:H3SpatialConsistency` (class)
- `types.py:H3BeliefUpdateResult` (class)
- `types.py:H3GridInferenceResult` (class)
- `types.py:H3CellDiagnostics` (class)
- `types.py:H3EdgeDiagnostics` (class)
- `types.py:H3LevelDiagnostics` (class)
- `types.py:SpatialInferenceTrace` (class)

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
- `h3>=4.5.0,<5`
- `imageio>=2.9.0`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
