---
name: geo-infer-act
description: Canonical GEO-INFER Active Inference implementation. Use when implementing or reviewing free-energy minimization, belief updating, generative models, policy selection, H3/spatial active inference, or typed ACT diagnostics.
prerequisites:
  required:
    - geo-infer-bayes
  recommended:
    - geo-infer-space
    - geo-infer-time
difficulty: advanced
estimated_time: 60min
examples_dir: ./examples/
---

# GEO-INFER-ACT

## Instructions

Use `GEO-INFER-ACT/src/geo_infer_act` as the canonical implementation for
Active Inference inside GEO-INFER. Prefer these public exports:

```python
from geo_infer_act import (
    ActiveInferenceModel,
    ActiveInferenceStepResult,
    FreeEnergyBreakdown,
    FreeEnergyCalculator,
    GenerativeModel,
    H3BeliefUpdateResult,
    H3GridInferenceResult,
    H3SpatialConsistency,
    PolicyEvaluation,
    PolicySelector,
    SpatialActiveInferenceAgent,
)
```

## Examples

```python
import numpy as np
from geo_infer_act import ActiveInferenceModel, GenerativeModel

generative_model = GenerativeModel(
    "categorical",
    {"state_dim": 3, "obs_dim": 3},
)

agent = ActiveInferenceModel(
    model_type="categorical",
    policy_selection_mode="deterministic",
    random_seed=42,
)
agent.set_generative_model(generative_model)

result = agent.step(
    np.array([1.0, 0.0, 0.0]),
    available_actions=["survey", "wait"],
    return_result=True,
)

assert isinstance(result, ActiveInferenceStepResult)
```

## Guidelines

### Method Contracts

- `FreeEnergyCalculator.compute_categorical_free_energy(..., return_breakdown=True)`
  returns `FreeEnergyBreakdown` with `free_energy = complexity - accuracy`.
- `FreeEnergyCalculator.compute_expected_free_energy(..., return_breakdown=True)`
  returns pragmatic, epistemic, risk, ambiguity, and entropy terms.
- `PolicySelector.select_policy(...)` returns selected policy metadata and a
  `PolicyEvaluation` object.
- `ActiveInferenceModel.step(..., return_result=True)` returns an
  `ActiveInferenceStepResult` without breaking the legacy `(beliefs, action)`
  return shape.
- `GenerativeModel.update_h3_beliefs(..., return_result=True)` returns an
  `H3BeliefUpdateResult` with normalized per-cell beliefs, aggregate free
  energy, and `H3SpatialConsistency`.
- `ActiveInferenceModel.infer_over_h3_grid(..., return_result=True)` and
  `SpatialActiveInferenceAgent.step(..., return_result=True)` return
  `H3GridInferenceResult`; their default dictionary outputs remain compatible.
- H3 methods must validate real H3 v4 cells. Synthetic cells are only for
  explicit `cell_*` unit-test paths.

### Integrations

- AGENT active-inference adapters should call or conform to ACT typed result
  contracts.
- MATH/BAYES convenience surfaces may expose helpers, but ACT remains the
  canonical implementation for Active Inference policy and free-energy logic.
- Optional external backends may be absent; use real local ACT methods or
  explicit `not_available` results.

## Verification

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```

Do not add inert placeholders, fake policy selection, first-policy defaults, or
undocumented public methods.
