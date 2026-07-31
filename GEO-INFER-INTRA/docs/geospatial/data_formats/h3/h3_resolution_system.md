# H3 resolution system

H3 provides integer resolutions `0` through `15`. Resolution 0 covers the
coarsest global cells; increasing the resolution produces smaller cells and a
larger potential cell count.

GEO-INFER APIs validate the range and require callers to choose a cell budget
before polygon expansion or nested hierarchy construction. A resolution is
metadata, not a substitute for a declared coordinate reference system: H3
coordinates are WGS84 degrees.

```python
import h3

cell = h3.latlng_to_cell(45.5231, -122.6765, resolution=9)
assert h3.get_resolution(cell) == 9
parent = h3.cell_to_parent(cell, 7)
children = h3.cell_to_children(parent, 9)
assert cell in children
```

Use real H3 cells in fixtures and tests. Synthetic strings are invalid H3
inputs and must not be used to make a spatial test appear to pass.
