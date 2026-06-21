# Agent Instructions: GEO-INFER-SPACE/tests/reports

## Scope

- Owning module: `GEO-INFER-SPACE`
- Python package: `geo_infer_space`
- Directory role: Reports workspace within `GEO-INFER-SPACE`.

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

- `visualizations/`
- `enhanced_status_report_20250714_074630.json`
- `enhanced_status_report_20250714_074746.json`
- `enhanced_status_report_20250714_081511.json`
- `status_dashboard_20250714_074630.html`
- `status_dashboard_20250714_074746.html`
- `status_dashboard_20250714_081511.html`

## Validation

```bash
uv run python -m pytest GEO-INFER-SPACE/tests/reports
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
