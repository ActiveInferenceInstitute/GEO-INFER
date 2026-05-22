# Agent Instructions: GEO-INFER-FOREST/tests/unit

## Scope

- Owning module: `GEO-INFER-FOREST`
- Python package: `geo_infer_forest`
- Directory role: Unit workspace within `GEO-INFER-FOREST`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_forest` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_canopy_analysis.py`
- `test_carbon_sequestration.py`
- `test_deforestation.py`
- `test_fire_risk.py`
- `test_forest_health.py`
- `test_forest_inventory.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-FOREST/tests/unit
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
