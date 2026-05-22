# Agent Instructions: GEO-INFER-PLACE/data/improvements/tl_2023_us_zcta520

## Scope

- Owning module: `GEO-INFER-PLACE`
- Python package: `geo_infer_place`
- Directory role: Tl 2023 Us Zcta520 workspace within `GEO-INFER-PLACE`.

## Capabilities

- Maintains the tracked files and subdirectories listed below for this workspace.
- Validates behavior with the command in the Validation section.
- Integrates through `geo_infer_place` and the owning module's public contracts.

## Working Rules

- Keep changes scoped to this directory unless an import, test, or documented command requires a coordinated edit.
- Prefer existing module patterns and public exports over new orchestration layers.
- Do not add planned, fake, mock, stub, or placeholder behavior to user-facing docs.
- If external services are involved, keep deterministic local validation available.

## Local Contents

- `tl_2023_us_zcta520.cpg`
- `tl_2023_us_zcta520.dbf`
- `tl_2023_us_zcta520.prj`
- `tl_2023_us_zcta520.shp.ea.iso.xml`
- `tl_2023_us_zcta520.shp.iso.xml`
- `tl_2023_us_zcta520.shx`

## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module PLACE
```

## Integration Notes

- Update this AGENTS.md and the sibling README.md when commands, exports, dependencies, or generated outputs change.
- Keep cross-module references anchored to real package imports and tracked files.
