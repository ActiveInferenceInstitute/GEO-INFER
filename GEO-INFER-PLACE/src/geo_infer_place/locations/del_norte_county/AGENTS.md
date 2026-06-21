# Agent Instructions: GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county

## Scope

- Owning module: `GEO-INFER-PLACE`
- Python package: `geo_infer_place`
- Directory role: Del Norte County workspace within `GEO-INFER-PLACE`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_place` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `dashboard/`
- `__init__.py`
- `coastal_resilience_analyzer.py`
- `comprehensive_dashboard.py`
- `fire_risk_assessor.py`
- `forest_health_monitor.py`
- `seismic_hazard_analyzer.py`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
