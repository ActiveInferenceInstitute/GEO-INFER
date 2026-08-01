# Agent Instructions: GEO-INFER-SIM/tests/unit

## Scope

- Owning module: `GEO-INFER-SIM`
- Python package: `geo_infer_sim`
- Directory role: Unit workspace within `GEO-INFER-SIM`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_sim` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_abm.py`
- `test_mesa_bridge.py`
- `test_scenario_manager.py`
- `test_simulation_engine.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-SIM/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
