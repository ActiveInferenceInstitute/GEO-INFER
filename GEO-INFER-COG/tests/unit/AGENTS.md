# Agent Instructions: GEO-INFER-COG/tests/unit

## Scope

- Owning module: `GEO-INFER-COG`
- Python package: `geo_infer_cog`
- Directory role: Unit workspace within `GEO-INFER-COG`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_cog` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_acceptance_cog.py`
- `test_attention.py`
- `test_cognitive_engine.py`
- `test_cognitive_models.py`
- `test_core.py`
- `test_decision_support.py`
- `test_spatial_language.py`
- `test_spatial_memory.py`
- `test_spatial_perception.py`
- `test_spatial_reasoning.py`
- `test_validation.py`
- `test_visualization.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-COG/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
