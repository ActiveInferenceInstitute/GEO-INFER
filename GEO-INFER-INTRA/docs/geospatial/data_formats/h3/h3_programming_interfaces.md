# H3 v4.5 programming interfaces

GEO-INFER exposes H3 through three deliberate layers:

1. Direct `h3` calls for focused integrations and tests.
2. `geo_infer_space.utils.h3_utils` for coordinate, GeoJSON, and convenience
   conversions.
3. `geo_infer_space.backends.h3.H3Backend` for availability checks,
   validation, capabilities, and backend-neutral spatial interfaces.

## Boundary and geometry rules

- `h3.cell_to_boundary(cell)` returns `(latitude, longitude)` pairs.
- GeoJSON positions are `[longitude, latitude]` and polygon rings are closed.
- `h3.geo_to_cells` consumes GeoJSON geometry and preserves holes and
  multipolygon structure.
- `h3.polygon_to_cells` consumes `h3.LatLngPoly` or another H3 shape in native
  latitude/longitude order.
- H3 resolution is an integer in `[0, 15]`.

## Public validation

`H3Backend` reports its installed version and minimum supported version through
`get_capabilities()`, rejects unsupported major versions, and returns sorted
cell collections at deterministic API boundaries. Use the backend for service
surfaces that need a stable contract.

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
```
