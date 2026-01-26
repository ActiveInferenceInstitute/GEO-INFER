# utils
 ## Overview
 This directory contains utils components. It includes 3 Python modules. ## Components
 ### data_source
s
.py CaliforniaDataSources: data source management for California. **Classes**: `DataSource`, `CaliforniaDataSources` ### h3_operation
s
.py H3 Operations Module for GEO-INFER-PLACE **Functions**: `latlng_to_cell`, `cell_to_latlng`, `cell_to_latlng_boundary`, `geo_to_cells`, `polygon_to_cells`, `grid_disk`, `grid_distance`, `grid_ring`, `cell_area`, `get_resolution`, `is_valid_cell`, `are_neighbor_cells`, `get_base_cell_number`, `cell_to_parent`, `cell_to_children`, `compact_cells`, `uncompact_cells`, `cells_to_geodataframe`, `estimate_cell_count` ### integratio
n
.py Del Norte data integration utilities. **Classes**: `_CALFIREWrapper`, `_NOAAWrapper`, `_USGSWrapper`, `DelNorteDataIntegrator` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 