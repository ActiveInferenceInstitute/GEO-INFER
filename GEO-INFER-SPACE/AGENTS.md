# Agent Instructions: GEO-INFER-SPACE

## Scope

- Owning module: `GEO-INFER-SPACE`
- Python package: `geo_infer_space`
- Directory role: H3 v4 spatial indexing and comprehensive geospatial analysis framework with advanced spatial methods and coordinate transformations.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_space` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `docs/`
- `examples/`
- `output/`
- `reports/`
- `scripts/`
- `src/`
- `test_output/`
- `tests/`
- `demo_all_methods.py`
- `verify_installation.py`
- `.cursorrules`
- `SKILL.md`
- `pyproject.toml`
- `requirements.txt`
- `uv.lock`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
