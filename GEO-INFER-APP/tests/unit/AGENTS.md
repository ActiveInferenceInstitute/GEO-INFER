# Agent Instructions: GEO-INFER-APP/tests/unit

## Scope

- Owning module: `GEO-INFER-APP`
- Python package: `geo_infer_app`
- Directory role: Unit workspace within `GEO-INFER-APP`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_app` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `models/`
- `test_agent_api.py`
- `test_agent_configuration.py`
- `test_agent_factory.py`
- `test_agent_interface.py`
- `test_agent_visualization.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-APP/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
