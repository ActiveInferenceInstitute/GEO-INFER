# H3 v4.5 visualization techniques

H3 geometry has two coordinate conventions that visualization code must keep
separate:

- H3 and Folium-style map locations use `[latitude, longitude]`.
- GeoJSON and Shapely geometry use `[longitude, latitude]`.

```python
import h3

cell = h3.latlng_to_cell(45.5231, -122.6765, 9)
boundary = h3.cell_to_boundary(cell)
folium_locations = [[lat, lng] for lat, lng in boundary]
geojson_ring = [[lng, lat] for lat, lng in boundary]
geojson_ring.append(geojson_ring[0])
```

Visualization tests should assert finite coordinates, geographic bounds, closed
GeoJSON rings, valid H3 indices, and deterministic feature ordering. Keep
Matplotlib styling local to a call and create output parent directories before
writing artifacts.

```
```bash
uv run pytest GEO-INFER-SPACE/tests/unit/test_h3_operations_runtime.py -q --no-cov
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```
