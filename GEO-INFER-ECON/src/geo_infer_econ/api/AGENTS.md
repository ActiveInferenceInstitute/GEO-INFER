# Agent Instructions: GEO-INFER-ECON/src/geo_infer_econ/api

## Scope

- Owning module: `GEO-INFER-ECON`
- Python package: `geo_infer_econ`
- Directory role: Api workspace within `GEO-INFER-ECON`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_econ` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `__init__.py`
- `economic_api.py`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ECON
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
