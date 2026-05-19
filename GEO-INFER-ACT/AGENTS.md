# Agent Guidance: GEO-INFER-ACT

## Scope

`GEO-INFER-ACT` is the canonical Active Inference implementation for
GEO-INFER. Keep Active Inference math, typed diagnostics, and runnable examples
grounded in `src/geo_infer_act`. Keep this file aligned with `SKILL.md`.

## Canonical Imports

```python
from geo_infer_act import (
    ActiveInferenceModel,
    ActiveInferenceStepResult,
    FreeEnergyBreakdown,
    FreeEnergyCalculator,
    GenerativeModel,
    PolicyEvaluation,
    PolicySelector,
    SpatialActiveInferenceAgent,
)
```

## Core Contracts

- `ActiveInferenceModel` owns the perceive-act loop.
- `GenerativeModel` owns categorical/Gaussian generative-model state and H3 helpers.
- `FreeEnergyCalculator` owns VFE/EFE math.
- `PolicySelector` owns expected-free-energy policy evaluation and selection.
- `SpatialActiveInferenceAgent` owns H3/cell-indexed active inference.
- Typed result objects are public API and must remain importable from `geo_infer_act`.

## Implementation Rules

- Do not introduce fake policy selection, first-policy defaults, or inert method bodies.
- Keep stochastic methods seedable when exposed to tests or examples.
- Optional integrations may return clear `not_available` results, but core ACT methods must be locally runnable.
- Update docs and tests when public method signatures or return shapes change.

## Verification

Run these from the repository root after ACT changes:

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```
