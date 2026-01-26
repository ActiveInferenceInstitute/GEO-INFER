# utils
 ## Overview
 This directory contains utils components. It includes 2 Python modules. ## Components
 ### config_loade
r
.py LocationConfigLoader: Configuration management for place-based analysis. **Classes**: `LocationBounds`, `LocationConfigLoader` ### h3_util
s
.py H3 utility functions for OSC-GEO. **Functions**: `latlng_to_cell`, `cell_to_latlng`, `cell_to_latlng_boundary`, `polygon_to_cells`, `cell_to_latlngjson`, `geojson_to_h3`, `geo_to_cells`, `grid_disk`, `grid_distance`, `compact_cells`, `uncompact_cells`, `cell_area`, `get_resolution`, `is_valid_cell`, `are_neighbor_cells` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 