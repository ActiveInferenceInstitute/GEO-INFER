# Agent Instructions: GEO-INFER-ENERGY/tests/unit

## Scope

- Owning module: `GEO-INFER-ENERGY`
- Python package: `geo_infer_energy`
- Directory role: Unit workspace within `GEO-INFER-ENERGY`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_energy` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `__init__.py`
- `test_acceptance_energy.py`
- `test_carbon_footprint.py`
- `test_energy_demand.py`
- `test_energy_grid.py`
- `test_renewable_resources.py`
- `test_solar_analysis.py`
- `test_wind_analysis.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-ENERGY/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
