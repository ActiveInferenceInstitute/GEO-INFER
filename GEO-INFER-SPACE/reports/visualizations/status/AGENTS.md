# Agent Instructions: GEO-INFER-SPACE/reports/visualizations/status

## Scope

- Owning module: `GEO-INFER-SPACE`
- Python package: `geo_infer_space`
- Directory role: Status workspace within `GEO-INFER-SPACE`.

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

- `environment_status_20260114_142208.png`
- `environment_status_20260114_142325.png`
- `environment_status_20260114_142331.png`
- `environment_status_20260114_142428.png`
- `environment_status_20260115_081711.png`
- `environment_status_20260115_081813.png`
- `environment_status_20260115_081855.png`
- `environment_status_20260115_081920.png`
- `environment_status_20260115_082048.png`
- `environment_status_20260115_082509.png`
- `environment_status_20260115_082640.png`
- `git_timeline_20260114_142208.png`
- `git_timeline_20260114_142325.png`
- `git_timeline_20260114_142331.png`
- `git_timeline_20260114_142428.png`
- `git_timeline_20260115_081711.png`
- `git_timeline_20260115_081813.png`
- `git_timeline_20260115_081855.png`
- `git_timeline_20260115_081920.png`
- `git_timeline_20260115_082048.png`
- `git_timeline_20260115_082509.png`
- `git_timeline_20260115_082640.png`
- `repository_health_20260114_142208.png`
- `repository_health_20260114_142325.png`
- `repository_health_20260114_142331.png`
- `repository_health_20260114_142428.png`
- `repository_health_20260115_081711.png`
- `repository_health_20260115_081813.png`
- `repository_health_20260115_081855.png`
- `repository_health_20260115_081920.png`
- `repository_health_20260115_082048.png`
- `repository_health_20260115_082509.png`
- `repository_health_20260115_082640.png`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
