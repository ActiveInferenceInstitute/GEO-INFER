# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 2 classes and 15 functions.

## Classes
 and Functions

### LocationBounds
 Geographic bounds for a location.

**Methods**:
- `to_bbox() -> tuple`: Convert to (west, south, east, north) bbox tuple.
- `center() -> tuple`: Get center point as (lat, lon).

### LocationConfigLoader
 Configuration loader for place-based analysis.

**Methods**:
- `load_location_config(location: str) -> Dict[str, Any]`: Load configuration for a specific location.
- `get_location_bounds(config: Dict[str, Any]) -> LocationBounds`: Extract location bounds from config.

### latlng_to_cell
 `latlng_to_cell(lat: float, lng: float, resolution: int) -> str` Convert lat/lng to H3 cell index using H3 v4 API.

### cell_to_latlng
 `cell_to_latlng(h3_index: str) -> Tuple[float, float]` Convert H3 cell index to lat/lng using H3 v4 API.

### cell_to_latlng_boundary
 `cell_to_latlng_boundary(h3_index: str) -> List[Tuple[float, float]]` Get H3 cell boundary as list of lat/lng pairs using H3 v4 API.

### polygon_to_cells
 `polygon_to_cells(polygon: Union[Dict[str, Any], List[List[float]]], resolution: int) -> List[str]` Convert polygon to H3 cell indices using h3 v4 API.

### cell_to_latlngjson
 `cell_to_latlngjson(h3_indices: List[str], properties: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]` Convert H3 indices to GeoJSON format (H3 4.x API).

### geojson_to_h3
 `geojson_to_h3(geojson_data: Union[str, Dict[str, Any]], resolution: int, feature_properties: bool) -> Dict[str, Union[List[str], Dict[str, Dict[str, Any]]]]` Convert GeoJSON to H3 indices (H3 4.x API).

### geo_to_cells
 `geo_to_cells(geojson: Dict[str, Any], resolution: int) -> List[str]` Convert GeoJSON to H3 cells using H3 v4 API.

### grid_disk
 `grid_disk(h3_index: str, k: int) -> List[str]` Get k-ring around H3 index using H3 v4 API.

### grid_distance
 `grid_distance(h3_index1: str, h3_index2: str) -> int` Get grid distance between two H3 indices using H3 v4 API.

### compact_cells
 `compact_cells(h3_indices: List[str]) -> List[str]` Compact H3 cells using H3 v4 API.

### uncompact_cells
 `uncompact_cells(h3_indices: List[str], resolution: int) -> List[str]` Uncompact H3 cells using H3 v4 API.

### cell_area
 `cell_area(h3_index: str, unit: str) -> float` Get area of H3 cell using H3 v4 API.

### get_resolution
 `get_resolution(h3_index: str) -> int` Get resolution of H3 index using H3 v4 API.

### is_valid_cell
 `is_valid_cell(h3_index: str) -> bool` Check if H3 index is valid using H3 v4 API.

### are_neighbor_cells
 `are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool` Check if two H3 indices are neighbors using H3 v4 API.

## Capabilities

- **2 classes** for core functionality
- **15 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-SPACE/src/geo_infer_space/utils`
- **Type**: Directory Node
