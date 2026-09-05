# Agent Instructions: GEO-INFER-INTRA/docs/modules

## Scope

- Owning module: `GEO-INFER-INTRA`
- Python package: `geo_infer_intra`
- Directory role: Modules workspace within `GEO-INFER-INTRA`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_intra` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `previews/`
- `geo-infer-act.md`
- `geo-infer-ag.md`
- `geo-infer-agent.md`
- `geo-infer-ai.md`
- `geo-infer-ant.md`
- `geo-infer-api.md`
- `geo-infer-app.md`
- `geo-infer-art.md`
- `geo-infer-bayes.md`
- `geo-infer-bio.md`
- `geo-infer-civ.md`
- `geo-infer-climate.md`
- `geo-infer-cog.md`
- `geo-infer-comms.md`
- `geo-infer-data.md`
- `geo-infer-econ.md`
- `geo-infer-edu.md`
- `geo-infer-emergency.md`
- `geo-infer-energy.md`
- `geo-infer-examples.md`
- `geo-infer-forest.md`
- `geo-infer-git.md`
- `geo-infer-health.md`
- `geo-infer-insurance.md`
- `geo-infer-intra.md`
- `geo-infer-iot.md`
- `geo-infer-log.md`
- `geo-infer-marine.md`
- `geo-infer-math.md`
- `geo-infer-metagov.md`
- `geo-infer-norms.md`
- `geo-infer-ops.md`
- `geo-infer-org.md`
- `geo-infer-pep.md`
- `geo-infer-place.md`
- `geo-infer-req.md`
- `geo-infer-risk.md`
- `geo-infer-sec.md`
- `geo-infer-sim.md`
- `geo-infer-space.md`
- `geo-infer-spm.md`
- `geo-infer-test.md`
- `geo-infer-time.md`
- `geo-infer-transport.md`
- `geo-infer-water.md`
- `index.md`
- `previews_index.md`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module INTRA
```


## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
