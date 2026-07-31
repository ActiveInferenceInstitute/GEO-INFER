# H3 v4.5 spatial analysis

## Point and polygon workflows

Use latitude/longitude order at the H3 boundary and GeoJSON order at the
GeoJSON boundary:

```python
import h3

cell = h3.latlng_to_cell(45.5231, -122.6765, 9)
nearby = sorted(h3.grid_disk(cell, 2))
geometry = {
    "type": "Polygon",
    "coordinates": [[
        [-122.70, 45.50], [-122.65, 45.50],
        [-122.65, 45.54], [-122.70, 45.54],
        [-122.70, 45.50],
    ]],
}
covered = sorted(h3.geo_to_cells(geometry, 9))
```

For exact rings use `grid_ring` where valid; for pentagon-safe neighborhood
analysis derive an exact shell from the difference between disks at `k` and
`k-1`. For disconnected coverage, keep the result as cells or a multipolygon
rather than silently collapsing it into one polygon.

## Aggregation

Aggregate values by H3 cell only after validating cell resolution, finite
values, and aligned keys. Sort cell IDs at serialization boundaries so API and
visualization outputs are reproducible.
