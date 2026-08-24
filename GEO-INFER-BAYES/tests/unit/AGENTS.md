# Agent Instructions: GEO-INFER-BAYES/tests/unit

## Scope

- Owning module: `GEO-INFER-BAYES`
- Python package: `geo_infer_bayes`
- Directory role: Unit workspace within `GEO-INFER-BAYES`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_bayes` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_abc_smc.py`
- `test_base_model.py`
- `test_civic_intel.py`
- `test_data_processing.py`
- `test_diagnostics.py`
- `test_distributional_uncertainty.py`
- `test_evaluation_metrics.py`
- `test_gaussian_process.py`
- `test_hmc.py`
- `test_inference.py`
- `test_likelihoods.py`
- `test_mcmc.py`
- `test_model_comparison.py`
- `test_model_contracts.py`
- `test_posterior.py`
- `test_posterior_prediction.py`
- `test_priors.py`
- `test_psis_loo_contract.py`
- `test_reproducibility.py`
- `test_rng.py`
- `test_sparse_spatial_gp.py`
- `test_spatial_gp.py`
- `test_spatiotemporal_gp.py`
- `test_variational.py`
- `test_visualization_utils.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-BAYES/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
