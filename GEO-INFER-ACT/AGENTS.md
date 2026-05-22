# Agent Instructions: GEO-INFER-ACT

## Scope

- Owning module: `GEO-INFER-ACT`
- Python package: `geo_infer_act`
- Directory role: Advanced Active Inference framework implementing Free Energy Principle for geospatial decision-making, perception, and learning.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_act` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `debug_models.py`
- `setup.py`
- `verify_comprehensive.py`
- `verify_pipeline.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
