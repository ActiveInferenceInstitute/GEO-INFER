# GEO-INFER-ACT Unit Tests

Unit tests validate the importable ACT package without depending on live
services. They cover the active-inference loop, free-energy math, policy
selection, generative models, domain models, H3/spatial diagnostics, runner
contracts, API facade, analysis utilities, and visualization helpers.

## Primary Files

| File | Coverage |
| --- | --- |
| `test_core.py` | Core active inference, generative models, belief updates, DCM, MDP, and VI. |
| `test_free_energy.py` | VFE/EFE calculations and typed breakdowns. |
| `test_policy_selection.py` | Deterministic and seeded policy selection. |
| `test_spatial_agent.py` | H3 `SpatialActiveInferenceAgent` behavior and diagnostics. |
| `test_runner_contracts.py` | Scenario output schemas and manifest contracts. |
| `test_geospatial_runner_outputs.py` | GIS-ready geospatial runner files and visualization sidecars. |
| `test_models.py` | Base and domain model behavior. |
| `test_utils.py` | Config, math, integration, analysis, and visualization utilities. |
| `test_api.py` | `ActiveInferenceInterface` create/update/policy flows. |

## Commands

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit -q
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_models.py GEO-INFER-ACT/tests/unit/test_utils.py -q
```

The focused `test_models.py` and `test_utils.py` command includes regression
coverage for finite categorical free energy with exact beliefs and for
visualization functions accepting canonical ACT belief/Markov-blanket payloads.
