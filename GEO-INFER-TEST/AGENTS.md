# Agent Instructions: GEO-INFER-TEST

## Scope

- Owning module: `GEO-INFER-TEST`
- Python package: `geo_infer_test`
- Directory role: Unified testing framework for quality assurance across all GEO-INFER modules with automated testing, performance benchmarks, and integration validation.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_test` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `.pytest_cache/`
- `config/`
- `docs/`
- `examples/`
- `src/`
- `tests/`
- `rewrite_readme_agents.py`
- `run_unified_tests.py`
- `setup.py`
- `validate_act_geospatial_contract.py`
- `validate_act_script_orchestration.py`
- `validate_active_inference_contract.py`
- `validate_h3_active_inference_contract.py`
- `validate_repo_contracts.py`
- `validate_skills.py`
- `.cursorrules`
- `SKILL.md`
- `TESTING.md`
- `pyproject.toml`
- `requirements.txt`

## Validation

```bash
uv sync --all-packages --all-extras
uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
