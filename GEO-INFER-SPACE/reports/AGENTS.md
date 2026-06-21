# Agent Instructions: GEO-INFER-SPACE/reports

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
- `enhanced_status_report_20260114_142208.json`
- `enhanced_status_report_20260114_142325.json`
- `enhanced_status_report_20260114_142331.json`
- `enhanced_status_report_20260114_142428.json`
- `enhanced_status_report_20260115_081712.json`
- `enhanced_status_report_20260115_081813.json`
- `enhanced_status_report_20260115_081856.json`
- `enhanced_status_report_20260115_081920.json`
- `enhanced_status_report_20260115_082048.json`
- `enhanced_status_report_20260115_082510.json`
- `enhanced_status_report_20260115_082640.json`
- `status_dashboard_20260114_142208.html`
- `status_dashboard_20260114_142325.html`
- `status_dashboard_20260114_142331.html`
- `status_dashboard_20260114_142428.html`
- `status_dashboard_20260115_081712.html`
- `status_dashboard_20260115_081813.html`
- `status_dashboard_20260115_081856.html`
- `status_dashboard_20260115_081920.html`
- `status_dashboard_20260115_082048.html`
- `status_dashboard_20260115_082510.html`
- `status_dashboard_20260115_082640.html`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
