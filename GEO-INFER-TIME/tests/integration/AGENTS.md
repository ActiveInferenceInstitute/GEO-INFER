# Agent Instructions: GEO-INFER-TIME/tests/integration

## Scope

- Owning module: `GEO-INFER-TIME`
- Python package: `geo_infer_time`
- Directory role: Integration workspace within `GEO-INFER-TIME`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_time` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `kafka_service_check.py`
- `test_integration.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-TIME/tests/integration
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
