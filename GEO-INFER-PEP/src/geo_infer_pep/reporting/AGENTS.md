# Agent Instructions: GEO-INFER-PEP/src/geo_infer_pep/reporting

## Scope

- Owning module: `GEO-INFER-PEP`
- Python package: `geo_infer_pep`
- Directory role: Reporting workspace within `GEO-INFER-PEP`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_pep` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `__init__.py`
- `crm_reports.py`
- `generic_report_generator.py`
- `hr_reports.py`
- `talent_reports.py`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module PEP
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
