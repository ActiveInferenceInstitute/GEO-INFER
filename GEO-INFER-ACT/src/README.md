# GEO-INFER-ACT Source

This tree contains the importable `geo_infer_act` package. `GEO-INFER-ACT`
is the canonical Active Inference implementation in GEO-INFER: it owns
generative models, belief updates, variational free energy, expected free
energy policy selection, spatial active inference, and typed diagnostic
contracts.

## Package Map

| Path | Purpose |
| --- | --- |
| `geo_infer_act/__init__.py` | Public package exports. |
| `geo_infer_act/core/active_inference.py` | `ActiveInferenceModel` perception-action loop. |
| `geo_infer_act/core/free_energy.py` | `FreeEnergyCalculator` VFE/EFE calculations. |
| `geo_infer_act/core/policy_selection.py` | `PolicySelector` policy evaluation and selection. |
| `geo_infer_act/core/generative_model.py` | `GenerativeModel`, Markov blankets, H3 spatial helpers. |
| `geo_infer_act/core/belief_updating.py` | Bayesian categorical and Gaussian belief updates. |
| `geo_infer_act/core/variational_inference.py` | Mean-field, structured, and sampling VI helpers. |
| `geo_infer_act/core/dynamic_causal_model.py` | Continuous-time dynamic causal model. |
| `geo_infer_act/core/markov_decision_process.py` | Discrete transition/observation dynamics. |
| `geo_infer_act/core/spatial_agent.py` | H3/spatial `SpatialActiveInferenceAgent`. |
| `geo_infer_act/runners/` | Scenario runners, manifest generation, geospatial output contracts, and traceable figure artifact writers. |
| `geo_infer_act/schemas/` | JSON Schema files for run config, manifests, metrics, and H3 diagnostics. |
| `geo_infer_act/api/interface.py` | High-level local API facade. |
| `geo_infer_act/models/` | Domain model examples using ACT primitives. |
| `geo_infer_act/utils/` | Math, diagnostics, integration, and visualization helpers. |

## Runnable Core Example

```python
import numpy as np
from geo_infer_act import ActiveInferenceModel, GenerativeModel

generative_model = GenerativeModel(
    model_type="categorical",
    parameters={"state_dim": 3, "obs_dim": 3},
)

agent = ActiveInferenceModel(
    model_type="categorical",
    policy_selection_mode="deterministic",
    random_seed=7,
)
agent.set_generative_model(generative_model)

result = agent.step(
    np.array([1.0, 0.0, 0.0]),
    available_actions=["survey", "wait"],
    return_result=True,
)

print(result.beliefs)
print(result.action)
print(result.free_energy)
```

## Typed Contracts

ACT exports three stable result objects for callers that need diagnostics:

```python
from geo_infer_act import (
    ActiveInferenceStepResult,
    FreeEnergyBreakdown,
    PolicyEvaluation,
)
```

Use `FreeEnergyBreakdown` through
`FreeEnergyCalculator.compute_categorical_free_energy(..., return_breakdown=True)`
or `compute_expected_free_energy(..., return_breakdown=True)`. Use
`PolicyEvaluation` through `PolicySelector.select_policy(...)`. Use
`ActiveInferenceStepResult` through
`ActiveInferenceModel.step(..., return_result=True)`.

## Runner Artifact Traceability

Scenario runners write `manifest.json` plus `data/`, `analysis/`,
`visualizations/`, and `logs/`. When visualizations are enabled, every figure has
embedded ACT metadata and adjacent sidecars: `*.metadata.json` for provenance and
`*.data.csv` or `*.data.json` for the exact plotted values. Manifest entries
include artifact type, MIME type, SHA-256 digest, figure sidecar paths, source
data files, plotted metrics, description, alt text, and image dimensions when
available.

## Verification

Run the ACT method/API contract check from the repository root:

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
```

Run ACT tests:

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```
