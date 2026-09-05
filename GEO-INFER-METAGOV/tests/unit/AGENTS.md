# Agent Instructions: GEO-INFER-METAGOV/tests/unit

## Scope

- Owning module: `GEO-INFER-METAGOV`
- Python package: `geo_infer_metagov`
- Directory role: Unit workspace within `GEO-INFER-METAGOV`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_metagov` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_acceptance_metagov.py`
- `test_accountability.py`
- `test_adaptation.py`
- `test_advanced_analysis.py`
- `test_all_modules.py`
- `test_api.py`
- `test_entity_object_support.py`
- `test_institutional.py`
- `test_metagov_core_units.py`
- `test_multi_level.py`
- `test_polycentric.py`
- `test_stakeholder.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-METAGOV/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
