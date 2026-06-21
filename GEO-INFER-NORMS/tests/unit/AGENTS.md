# Agent Instructions: GEO-INFER-NORMS/tests/unit

## Scope

- Owning module: `GEO-INFER-NORMS`
- Python package: `geo_infer_norms`
- Directory role: Unit workspace within `GEO-INFER-NORMS`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_norms` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_compliance_tracking.py`
- `test_legal_frameworks.py`
- `test_models.py`
- `test_normative_inference.py`
- `test_policy_impact.py`
- `test_policy_validation.py`
- `test_zoning_analysis.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-NORMS/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
