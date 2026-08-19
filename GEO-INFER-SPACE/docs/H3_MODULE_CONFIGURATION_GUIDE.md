# H3 module configuration guide

This guide defines the small, executable configuration contract used by H3
integration code. It is not a generator for unimplemented modules.

```yaml
h3:
  library: h3-py
  minimum_version: "4.5.0"
  maximum_major: 5
  default_resolution: 9
  max_cells_per_operation: 100000
  coordinate_order:
    input: "latitude,longitude"
    geojson: "longitude,latitude"
```

Modules should validate the resolution range `0..15`, finite WGS84
coordinates, a positive cell budget, and the installed H3 version before
expanding a polygon. Use `h3.geo_to_cells` for GeoJSON geometry and preserve
holes and multipolygons. Use `h3.LatLngPoly` only for native
`(latitude, longitude)` rings.

A module's public API should expose an explicit backend capability or a clear
`H3UnavailableError`; it must not fabricate H3 IDs when the dependency is
missing. Add focused tests for point conversion, polygon conversion, invalid
inputs, and GeoJSON ring order.

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language
```
