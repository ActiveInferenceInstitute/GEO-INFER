# Agent Instructions: GEO-INFER-TIME/tests

## Scope

- Owning module: `GEO-INFER-TIME`
- Python package: `geo_infer_time`
- Directory role: Tests workspace within `GEO-INFER-TIME`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_time` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `integration/`
- `unit/`
- `conftest.py`
- `test_advanced_forecasting.py`
- `test_analysis_extended.py`
- `test_event_detection.py`
- `test_forecasting.py`
- `test_interpolation.py`
- `test_io_utils_db.py`
- `test_statistics_extended.py`
- `test_stream_processing.py`
- `test_temporal_analysis.py`
- `test_temporal_statistics.py`
- `test_temporal_visualization.py`
- `test_timeseries_model.py`

## Validation

```bash
uv run python -m pytest GEO-INFER-TIME/tests
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
