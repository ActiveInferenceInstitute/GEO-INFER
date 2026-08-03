# H3 v4.5 code examples

These examples use the repository-supported `h3>=4.5.0,<5` API and real cells.

## Point, boundary, and GeoJSON

```python
import h3

cell = h3.latlng_to_cell(45.5231, -122.6765, 9)
center_lat, center_lng = h3.cell_to_latlng(cell)

# h3-py returns (lat, lng); GeoJSON requires [lng, lat].
ring = [[lng, lat] for lat, lng in h3.cell_to_boundary(cell)]
ring.append(ring[0])
feature = {
    "type": "Feature",
    "geometry": {"type": "Polygon", "coordinates": [ring]},
    "properties": {"h3_index": cell},
}
```

## Fill a GeoJSON polygon

```
```python
geometry = {
    "type": "Polygon",
    "coordinates": [[
        [-122.70, 45.50],
        [-122.65, 45.50],
        [-122.65, 45.54],
        [-122.70, 45.54],
        [-122.70, 45.50],
    ]],
}
cells = sorted(h3.geo_to_cells(geometry, res=9))
```

## Native H3 polygon

```
```python
polygon = h3.LatLngPoly([
    (45.50, -122.70),
    (45.50, -122.65),
    (45.54, -122.65),
    (45.54, -122.70),
])
cells = sorted(h3.polygon_to_cells(polygon, res=9))
```

Run the repository H3 contract gate after changing an example.
