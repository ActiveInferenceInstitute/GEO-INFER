# Agent Instructions: GEO-INFER-RISK/tests/unit

## Scope

- Owning module: `GEO-INFER-RISK`
- Python package: `geo_infer_risk`
- Directory role: Unit workspace within `GEO-INFER-RISK`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_risk` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_aal_exposure_years.py`
- `test_aep_pml_curve.py`
- `test_catastrophe_compound_paths.py`
- `test_civic_intel.py`
- `test_compound_risk_matrix.py`
- `test_config_loader.py`
- `test_core.py`
- `test_distributional_uncertainty.py`
- `test_exposure_model.py`
- `test_generator_isolation.py`
- `test_hazard_model.py`
- `test_insurance_models.py`
- `test_package_exports.py`
- `test_portfolio_management.py`
- `test_reproducibility.py`
- `test_risk_engine.py`
- `test_risk_metrics.py`
- `test_risk_models.py`
- `test_rng.py`
- `test_underwriting.py`
- `test_validation.py`
- `test_vulnerability_model.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-RISK/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
