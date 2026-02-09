# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 6 classes and 19 functions.

## Classes
 and Functions

### DataSource
 Configuration for a data source.

### CaliforniaDataSources
 data source catalog for California geospatial datasets.

**Methods**:
- `get_sources_by_category(category: str) -> List[DataSource]`: Get all data sources in a specific category.
- `get_source_config(source_id: str) -> Optional[DataSource]`: Get configuration for a specific data source.
- `search_sources(query: str, categories: Optional[List[str]], data_types: Optional[List[str]]) -> List[DataSource]`: Search data sources by query and filters.
- `get_sources_for_location(location_bounds: Tuple[float, float, float, float], location_name: str) -> Dict[str, List[DataSource]]`: Get relevant data sources for a specific location.
- `validate_source_access(source_id: str, api_key: Optional[str]) -> Dict[str, Any]`: Validate access to a data source.
- `get_update_schedule() -> Dict[str, List[str]]`: Get data sources organized by their update frequency.
- `get_source_summary() -> Dict[str, Any]`: Get a summary of all available data sources.

### DelNorteDataIntegrator
 Integrator that aggregates API wrappers for analyzers.

### latlng_to_cell
 `latlng_to_cell(lat: float, lng: float, resolution: int) -> str` Convert latitude/longitude coordinates to an H3 cell index.

### cell_to_latlng
 `cell_to_latlng(cell: str) -> Tuple[float, float]` Get the center coordinates of an H3 cell.

### cell_to_latlng_boundary
 `cell_to_latlng_boundary(cell: str) -> List[Tuple[float, float]]` Get the boundary vertices of an H3 cell.

### geo_to_cells
 `geo_to_cells(geojson: Dict[str, Any], resolution: int) -> List[str]` Convert a GeoJSON polygon to a set of H3 cells.

### polygon_to_cells
 `polygon_to_cells(polygon: Any, resolution: int) -> List[str]` Convert a Shapely polygon to H3 cells.

### grid_disk
 `grid_disk(cell: str, k: int) -> List[str]` Get all cells within k grid distance of the origin cell.

### grid_distance
 `grid_distance(cell1: str, cell2: str) -> int` Get the grid distance between two H3 cells.

### grid_ring
 `grid_ring(cell: str, k: int) -> List[str]` Get cells at exactly k grid distance from origin.

### cell_area
 `cell_area(cell: str, unit: str) -> float` Get the area of an H3 cell.

### get_resolution
 `get_resolution(cell: str) -> int` Get the resolution of an H3 cell.

### is_valid_cell
 `is_valid_cell(cell: str) -> bool` Check if a string is a valid H3 cell index.

### are_neighbor_cells
 `are_neighbor_cells(cell1: str, cell2: str) -> bool` Check if two H3 cells are neighbors.

### get_base_cell_number
 `get_base_cell_number(cell: str) -> int` Get the base cell number of an H3 index.

### cell_to_parent
 `cell_to_parent(cell: str, parent_res: int) -> str` Get the parent cell at a coarser resolution.

### cell_to_children
 `cell_to_children(cell: str, child_res: int) -> List[str]` Get all child cells at a finer resolution.

### compact_cells
 `compact_cells(cells: List[str]) -> List[str]` Compact a set of cells to their most compact representation.

### uncompact_cells
 `uncompact_cells(cells: List[str], resolution: int) -> List[str]` Uncompact cells to a specified resolution.

### cells_to_geodataframe
 `cells_to_geodataframe(cells: List[str]) -> 'gpd.GeoDataFrame'` Convert a list of H3 cells to a GeoDataFrame with polygon geometries.

### estimate_cell_count
 `estimate_cell_count(area_km2: float, resolution: int) -> int` Estimate the number of H3 cells to cover an area.

## Capabilities

- **6 classes** for core functionality
- **19 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-PLACE/src/geo_infer_place/utils`
- **Type**: Directory Node
