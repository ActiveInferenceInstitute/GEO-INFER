# H3 advanced methods in SPACE

Advanced H3 behavior is implemented under
`geo_infer_space.backends.h3` and `geo_infer_space.utils.h3_utils`; there is no
`geo_infer_space.h3` module.

```python
import h3
from geo_infer_space.backends.h3.h3_backend import H3Backend

backend = H3Backend()
cell = backend.latlng_to_cell(37.7749, -122.4194, 9)
ring = backend.get_cell_neighbors(cell, k=1)
area_km2 = backend.get_cell_area(cell, unit="km^2")
```

Use `h3.geo_to_cells` for GeoJSON polygons, `h3.LatLngPoly` for native
latitude/longitude rings, and explicit coordinate conversion for GeoJSON and
visualization output. Backend capabilities include the installed version and
minimum supported version.

```bash
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
```
