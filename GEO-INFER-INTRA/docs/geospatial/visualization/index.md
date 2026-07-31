# Geospatial Visualization

This hub documents the visualization contracts that are implemented in the
repository. The runnable visualization surface is currently centered on the
SPACE and PLACE modules, with native H3 boundaries converted to GeoJSON order
(``[longitude, latitude]``) and Folium order (``[latitude, longitude]``) at the
client boundary.

## Current guides

- [H3 visualization techniques](../data_formats/h3/h3_visualization_techniques.md)
- [First map](../../getting_started/first_map.md)
- [Coordinate systems](../concepts/coordinate_systems.md)
- [Spatial data models](../concepts/spatial_data_models.md)

## Implemented visualization entry points

- `geo_infer_space.core.visualization_engine.VisualizationEngine`
- `geo_infer_space.backends.h3.visualization.H3Visualization`
- `geo_infer_place.core.visualization_engine.InteractiveVisualizationEngine`
- `geo_infer_place.core.unified_backend.CascadianAgriculturalH3Backend`

Generated HTML, PNG, and dashboard artifacts belong in a caller-provided
output directory. The repository's validation suites check finite metrics,
closed GeoJSON rings, H3 cell metadata, and output isolation; they do not claim
that a historical image in `GEO-INFER-SPACE/reports/visualizations/status/` is
a current assessment.

## Coordinate-order contract

H3's `cell_to_boundary` returns native `(latitude, longitude)` pairs. Convert
explicitly at the output boundary:

```python
ring = [[lng, lat] for lat, lng in h3.cell_to_boundary(cell)]
ring.append(ring[0])
```

Use `[lat, lng]` only when passing coordinates to Folium. Never pass the
removed H3 v3 `geo_json=` argument to `cell_to_boundary`.
