# Agent Instructions: GEO-INFER-EDU/tests

## Scope

- Owning module: `GEO-INFER-EDU`
- Python package: `geo_infer_edu`
- Directory role: Tests workspace within `GEO-INFER-EDU`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_edu` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_curriculum.py`
- `test_exercise_generator.py`
- `test_exercises.py`
- `test_personalization.py`
- `test_professional.py`
- `test_progress.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-EDU/tests
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
