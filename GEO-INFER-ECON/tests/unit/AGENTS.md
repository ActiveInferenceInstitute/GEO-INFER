# Agent Instructions: GEO-INFER-ECON/tests/unit

## Scope

- Owning module: `GEO-INFER-ECON`
- Python package: `geo_infer_econ`
- Directory role: Unit workspace within `GEO-INFER-ECON`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_econ` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `test_behavioral_economics.py`
- `test_bioregional_economics.py`
- `test_consumer_theory.py`
- `test_enhanced_capabilities.py`
- `test_game_theory.py`
- `test_growth_models.py`
- `test_indicators.py`
- `test_market_structure.py`
- `test_modeling_engine.py`
- `test_policy_engine.py`
- `test_producer_theory.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-ECON/tests/unit
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
