# Agent Instructions: GEO-INFER-INTRA/tests/unit

## Scope

- Owning module: `GEO-INFER-INTRA`
- Python package: `geo_infer_intra`
- Directory role: Unit workspace within `GEO-INFER-INTRA`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_intra` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_config.py`
- `test_geospatial_utils.py`
- `test_module_utils.py`
- `test_time_series_utils.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-INTRA/tests/unit
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
