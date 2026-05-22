# Agent Instructions: GEO-INFER-AGENT/examples

## Scope

- Owning module: `GEO-INFER-AGENT`
- Python package: `geo_infer_agent`
- Directory role: Examples workspace within `GEO-INFER-AGENT`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_agent` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `active_inference_geospatial.py`
- `agent_examples.py`
- `simple_agent_example.py`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module AGENT
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
