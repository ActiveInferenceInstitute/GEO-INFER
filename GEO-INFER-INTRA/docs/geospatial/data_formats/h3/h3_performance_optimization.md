# H3 v4.5 performance guidance

This page describes current, measurable optimization boundaries for
`h3>=4.5.0,<5`.

- Convert points in batches while keeping latitude/longitude order explicit.
- Use `geo_to_cells` once for a complete GeoJSON geometry instead of filling
  each boundary vertex independently.
- Use `set` for deduplication, then sort cells at API boundaries when stable
  output is required.
- Validate a cell budget before expanding a polygon or nested hierarchy.
- Use `compact_cells` and `uncompact_cells` only when the source and target
  resolutions are explicit.
- Avoid constructing Shapely objects for every cell when a GeoJSON
  `FeatureCollection` is sufficient.
- Treat pentagons, holes, disconnected polygons, and antimeridian crossings as
  benchmark cases rather than assuming six vertices or six neighbors.

A performance change is accepted only with a focused benchmark or test and a
behavioral H3 contract check:

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
```
