# Agent Instructions: GEO-INFER-TEST/tests/unit

## Scope

- Owning module: `GEO-INFER-TEST`
- Python package: `geo_infer_test`
- Directory role: Unit workspace within `GEO-INFER-TEST`.

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

- `test_data_domains.py`
- `test_log_integration.py`
- `test_module_health.py`
- `test_performance_monitor.py`
- `test_spatial_functions.py`
- `test_test_discoverer.py`
- `test_test_orchestrator.py`
- `test_test_runner.py`
- `test_validators.py`
- `test_validators_parametric.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-TEST/tests/unit
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
