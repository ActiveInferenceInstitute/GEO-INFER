# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 0 classes and 12 functions.

## Classes
 and Functions

### validate_polygon_rings
 `validate_polygon_rings(coordinates: List[List[Tuple[float, float]]]) -> bool` Validate that a polygon's rings follow the GeoJSON specification.

### calculate_polygon_area
 `calculate_polygon_area(polygon: Union[Polygon, Dict]) -> float` Calculate the approximate area of a polygon in square kilometers.

### polygon_contains_point
 `polygon_contains_point(polygon: Union[Polygon, Dict], point: Tuple[float, float]) -> bool` Check if a point is inside a polygon using the ray casting algorithm.

### simplify_polygon
 `simplify_polygon(polygon: Polygon, tolerance: float) -> Polygon` Simplify a polygon using the Ramer-Douglas-Peucker algorithm.

### create_polygon_feature
 `create_polygon_feature(coordinates: List[List[Tuple[float, float]]], properties: Dict, feature_id: str) -> PolygonFeature` Create a GeoJSON PolygonFeature from coordinates.

### create_buffer
 `create_buffer(polygon: Union[Polygon, Dict], distance: float, unit: str, segments: int) -> Polygon` Create a buffer around a polygon at a specified distance.

### calculate_intersection
 `calculate_intersection(polygons: List[Union[Polygon, Dict]]) -> Polygon` Calculate the intersection of multiple polygons.

### calculate_union
 `calculate_union(polygons: List[Union[Polygon, Dict]]) -> Polygon` Calculate the union of multiple polygons.

### calculate_distance
 `calculate_distance(polygon1: Union[Polygon, Dict], polygon2: Union[Polygon, Dict], method: str) -> float` Calculate the distance between two polygons.

### rdp
 `rdp(points, epsilon)` Recursive implementation of Ramer-Douglas-Peucker algorithm.

### perpendicular_distance
 `perpendicular_distance(point, line_start, line_end)` Calculate perpendicular distance from point to line.

### get_centroid
 `get_centroid(polygon)` Calculate centroid of a polygon.

## Capabilities

- **12 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-API/src/geo_infer_api/utils`
- **Type**: Directory Node
