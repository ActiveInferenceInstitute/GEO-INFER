# Agent Instructions: GEO-INFER-AG/tests/unit/core

## Scope

- Owning module: `GEO-INFER-AG`
- Python package: `geo_infer_ag`
- Directory role: Core workspace within `GEO-INFER-AG`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_ag` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_agricultural_analysis.py`
- `test_field_boundary.py`
- `test_seasonal_analysis.py`
- `test_sustainability.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-AG/tests/unit/core
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
