# Agent Instructions: GEO-INFER-LOG/src

## Scope

- Owning module: `GEO-INFER-LOG`
- Python package: `geo_infer_log`
- Directory role: Src workspace within `GEO-INFER-LOG`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_log` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `geo_infer_log.egg-info/`
- `geo_infer_log/`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
