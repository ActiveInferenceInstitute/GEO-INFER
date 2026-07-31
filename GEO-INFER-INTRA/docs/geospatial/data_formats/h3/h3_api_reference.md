# H3 v4.5 API reference

Status: current GEO-INFER guidance for `h3>=4.5.0,<5`; the repository lockfile
currently resolves `h3==4.5.0`.

## Core calls

| Operation | h3-py v4 call | Coordinate contract |
| --- | --- | --- |
| Point to cell | `h3.latlng_to_cell(lat, lng, resolution)` | input is latitude, longitude |
| Cell center | `h3.cell_to_latlng(cell)` | output is latitude, longitude |
| Boundary | `h3.cell_to_boundary(cell)` | vertices are latitude, longitude |
| Disk | `h3.grid_disk(cell, k)` | includes the origin cell |
| Exact ring | `h3.grid_ring(cell, k)` | may require pentagon-aware handling |
| Polygon fill | `h3.geo_to_cells(geometry, resolution)` | GeoJSON positions are longitude, latitude |
| Cell area | `h3.cell_area(cell, unit='km^2')` | explicit unit required |

Use `h3.LatLngPoly` with `h3.polygon_to_cells` when the input is already in
native `(latitude, longitude)` order. Use `h3.geo_to_cells` for GeoJSON
geometry, Shapely `__geo_interface__`, and holes or multipolygons.

## GEO-INFER wrappers

The SPACE helpers preserve native H3 boundary order in
`cell_to_latlng_boundary` and perform explicit conversion in GeoJSON-producing
helpers. Do not pass a removed keyword to `cell_to_boundary`.

## Verification

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
```

The upstream API reference and release history are authoritative for behavior
outside this repository's wrapper contracts.
