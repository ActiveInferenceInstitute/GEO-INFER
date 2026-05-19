# GEO-INFER-ACT Tests

This directory validates the importable `geo_infer_act` package.

## Test Map

| Path | Coverage |
| --- | --- |
| `unit/test_core.py` | `ActiveInferenceModel`, `GenerativeModel`, belief updates, DCM, MDP, VI. |
| `unit/test_free_energy.py` | `FreeEnergyCalculator` VFE/EFE terms and typed breakdowns. |
| `unit/test_policy_selection.py` | `PolicySelector`, deterministic and seeded stochastic policy selection. |
| `unit/test_api.py` | `ActiveInferenceInterface` model creation, belief updates, policy reports. |
| `unit/test_spatial_agent.py` | `SpatialActiveInferenceAgent` perception, action, diagnostics. |
| `unit/test_h3_active_inference.py` | H3 example reproducibility and exported metrics. |
| `integration/` | Cross-module ACT integrations. |

## Focused Verification

From the repository root:

```bash
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_core.py -q
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_free_energy.py -q
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_policy_selection.py -q
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests/unit/test_api.py -q
```

## Full ACT Suite

```bash
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
```

## Contract Expectations

- Public ACT methods in the checked core surfaces have docstrings.
- ACT source has no `pass` or `NotImplementedError` method bodies.
- Categorical VFE exposes `complexity - accuracy`.
- EFE policy selection uses policy-conditioned predictive beliefs when supplied.
- Gaussian belief updates return real `mean` and `precision` values.
- H3/spatial methods return real spatial consistency diagnostics.
