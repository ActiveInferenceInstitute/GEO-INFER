# geo_infer_act

`geo_infer_act` is the importable Active Inference package for GEO-INFER.

## Public Surface

- `ActiveInferenceModel`: perception-action loop over a `GenerativeModel`.
- `GenerativeModel`: categorical/Gaussian generative model and H3 helpers.
- `FreeEnergyCalculator`: variational and expected free-energy calculations.
- `PolicySelector`: expected-free-energy policy evaluation and selection.
- `BayesianBeliefUpdate`: categorical Bayes and Gaussian Kalman updates.
- `VariationalInference`: mean-field, structured, and importance-sampling updates.
- `DynamicCausalModel`: continuous-time state-space dynamics.
- `SpatialActiveInferenceAgent`: H3/spatial active inference agent.
- `FreeEnergyBreakdown`, `PolicyEvaluation`, `ActiveInferenceStepResult`:
  typed diagnostic result objects.

## Subpackages

- `api/`: local API facade and endpoint/client helpers.
- `core/`: canonical Active Inference methods.
- `models/`: domain model examples built on core methods.
- `utils/`: math, diagnostics, integration, and visualization helpers.
- `runners/`: package-owned scenario execution, manifests, GIS outputs,
  geospatial visualization generation, embedded figure metadata, and figure
  data sidecars.
- `schemas/`: JSON Schema contracts for run configs, manifests, metrics, and
  H3 diagnostics.

## Contract Check

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
```
