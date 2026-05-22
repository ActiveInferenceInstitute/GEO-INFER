# Agent Instructions: GEO-INFER-PEP/tests/unit

## Scope

- Owning module: `GEO-INFER-PEP`
- Python package: `geo_infer_pep`
- Directory role: Unit workspace within `GEO-INFER-PEP`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_pep` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_crm.py`
- `test_crm_models.py`
- `test_hr.py`
- `test_hr_models.py`
- `test_methods.py`
- `test_pep_engine.py`
- `test_talent.py`
- `test_talent_models.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-PEP/tests/unit
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
