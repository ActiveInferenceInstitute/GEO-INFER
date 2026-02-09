# Agent
: srai

## Scope
 This directory contains srai components for the module. It provides 1 classes and 3 functions.

## Classes
 and Functions

### SraiBackend
 SRAI backend implementation for spatial operations.

**Methods**:
- `name() -> str`: Return the backend name.
- `version() -> str`: Return the backend version.
- `is_available() -> bool`: Check if the backend is available and functional.
- `get_capabilities() -> Dict[str, Any]`: Return the backend's capabilities.
- `latlng_to_cell(lat: float, lng: float, resolution: int) -> str`: Convert lat/lng coordinates to SRAI region cell.
- `cell_to_latlng(cell: str) -> tuple[float, float]`: Convert SRAI region cell back to lat/lng coordinates.
- `polygon_to_cells(polygon: Dict[str, Any], resolution: int) -> List[str]`: Convert polygon to list of SRAI region cells.
- `get_cell_neighbors(cell: str, k: int) -> List[str]`: Get neighboring cells around a given cell.
- `get_cell_distance(cell1: str, cell2: str) -> int`: Calculate the grid distance between two cells.
- `compact_cells(cells: List[str]) -> List[str]`: Compact a list of cells into a more efficient representation.
- `uncompact_cells(compacted_cells: List[str], resolution: int) -> List[str]`: Uncompact cells back to individual cell identifiers.
- `get_cell_parent(cell: str, resolution: int) -> str`: Get the parent of a cell at a coarser resolution.
- `get_cell_children(cell: str, resolution: int) -> List[str]`: Get children of a cell at a finer resolution.
- `get_cell_path(start_cell: str, end_cell: str) -> List[str]`: Get the path of cells between two cells.
- `get_cell_ring(cell: str, k: int) -> List[str]`: Get the ring of cells at distance k.
- `get_cell_resolution(cell: str) -> int`: Get the resolution level of a cell.
- `get_cell_boundary(cell: str) -> List[Tuple[float, float]]`: Get the boundary coordinates of a cell.
- `get_cell_area(cell: str) -> float`: Get the area of a cell in square kilometers.
- `cells_to_multipolygon(cells: List[str]) -> Dict[str, Any]`: Convert a list of cells to a GeoJSON MultiPolygon geometry.
- `analyze_hotspots(data: Dict[str, Any]) -> Dict[str, Any]`: Analyze spatial hotspots using SRAI analytics.
- `compute_proximity(points: List[tuple[float, float]]) -> Dict[str, Any]`: Compute proximity analysis using SRAI.

### decorator
 `decorator(func)`

### wrapper
 `wrapper(self, *args, **kwargs)`

## Capabilities

- **1 classes** for core functionality
- **3 functions** for utility operations

## Integration

- **Location**: `src/geo_infer_space/backends/srai`
- **Type**: Directory Node
