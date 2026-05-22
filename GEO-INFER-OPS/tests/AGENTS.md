# Agent Instructions: GEO-INFER-OPS/tests

## Scope

- Owning module: `GEO-INFER-OPS`
- Python package: `geo_infer_ops`
- Directory role: Tests workspace within `GEO-INFER-OPS`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_ops` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `integration/`
- `unit/`
- `__init__.py`
- `conftest.py`
- `test_cache.py`
- `test_config.py`
- `test_deployment.py`
- `test_framework.py`
- `test_logging.py`
- `test_monitoring.py`
- `test_security.py`
- `test_testing.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-OPS/tests
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
