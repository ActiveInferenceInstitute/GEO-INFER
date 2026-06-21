# Agent Instructions: GEO-INFER-LOG

## Scope

- Owning module: `GEO-INFER-LOG`
- Python package: `geo_infer_log`
- Directory role: Geospatial intelligence for logistics optimization, supply chain management, route optimization, and transportation planning.

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

- `.pytest_cache/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `setup.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module LOG
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
