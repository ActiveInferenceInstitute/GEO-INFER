# Agent Instructions: GEO-INFER-NORMS/tests/test-outputs

## Scope

- Owning module: `GEO-INFER-NORMS`
- Python package: `geo_infer_norms`
- Directory role: Test Outputs workspace within `GEO-INFER-NORMS`.

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

- `all_tests.html`
- `normative_inference.html`
- `report.html`
- `social_norm_diffusion.html`

## Validation

```bash
uv run python -m pytest GEO-INFER-NORMS/tests/test-outputs
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
