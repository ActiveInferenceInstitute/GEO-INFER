# Agent Instructions: GEO-INFER-TRANSPORT/tests

## Scope

- Owning module: `GEO-INFER-TRANSPORT`
- Python package: `geo_infer_transport`
- Directory role: Tests workspace within `GEO-INFER-TRANSPORT`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_transport` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_accessibility.py`
- `test_network_routing.py`
- `test_routing.py`
- `test_traffic.py`
- `test_traffic_transit.py`
- `test_transit.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
