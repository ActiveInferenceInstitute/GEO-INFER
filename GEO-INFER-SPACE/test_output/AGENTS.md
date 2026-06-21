# Agent Instructions: GEO-INFER-SPACE/test_output

## Scope

- Owning module: `GEO-INFER-SPACE`
- Python package: `geo_infer_space`
- Directory role: Test Output workspace within `GEO-INFER-SPACE`.

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

- `comprehensive_dashboard_20260114_142208.html`
- `comprehensive_dashboard_20260114_142325.html`
- `comprehensive_dashboard_20260114_142331.html`
- `comprehensive_dashboard_20260114_142428.html`
- `comprehensive_dashboard_20260115_081712.html`
- `comprehensive_dashboard_20260115_081813.html`
- `comprehensive_dashboard_20260115_081856.html`
- `comprehensive_dashboard_20260115_081920.html`
- `comprehensive_dashboard_20260115_082048.html`
- `comprehensive_dashboard_20260115_082510.html`
- `comprehensive_dashboard_20260115_082640.html`
- `comprehensive_dashboard_20260125_122852.html`
- `comprehensive_dashboard_20260125_123816.html`
- `comprehensive_dashboard_20260125_124103.html`
- `comprehensive_dashboard_20260125_125049.html`
- `comprehensive_dashboard_20260208_174046.html`
- `comprehensive_dashboard_20260208_174104.html`
- `comprehensive_dashboard_20260208_174826.html`
- `comprehensive_dashboard_20260208_175435.html`
- `comprehensive_dashboard_20260208_175511.html`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
