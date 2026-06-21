# Agent Instructions: GEO-INFER-MATH/src/geo_infer_math/api/convenience

## Scope

- Owning module: `GEO-INFER-MATH`
- Python package: `geo_infer_math`
- Directory role: Convenience workspace within `GEO-INFER-MATH`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_math` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `__init__.py`
- `act_convenience.py`
- `ai_convenience.py`
- `bayes_convenience.py`
- `information_convenience.py`
- `integration_convenience.py`
- `spatial_convenience.py`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
