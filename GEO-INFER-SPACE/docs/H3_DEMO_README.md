# H3 geospatial demonstrations

Run the maintained examples from the SPACE module with the workspace
environment. They use real H3 v4.5 APIs and write outputs only where the
example specifies.

```bash
uv run python GEO-INFER-SPACE/examples/h3_advanced_applications.py
uv run python GEO-INFER-SPACE/examples/h3_comprehensive_examples.py
uv run python GEO-INFER-SPACE/examples/h3_integration_examples.py
```

Examples use latitude/longitude for H3 calls, `[latitude, longitude]` for
Folium map locations, and closed GeoJSON rings in `[longitude, latitude]`
order. Inspect generated artifacts rather than treating example execution as a
release gate; use the H3 contract validator for the gate.
