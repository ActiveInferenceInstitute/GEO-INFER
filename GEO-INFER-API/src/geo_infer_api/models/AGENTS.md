# Agent
: models

## Scope
 This directory contains models components for the module. It provides 15 classes and 0 functions.

## Classes
 and Functions

### GeoJSONType
 Valid GeoJSON types.

### GeometryBase
 Base model for all GeoJSON geometry objects.

### Point
 GeoJSON Point geometry.

**Methods**:
- `validate_coordinates(cls, v)`: Validate point coordinates.

### LineString
 GeoJSON LineString geometry.

**Methods**:
- `validate_coordinates(cls, v)`: Validate LineString has at least 2 points.

### Polygon
 GeoJSON Polygon geometry.

**Methods**:
- `validate_coordinates(cls, v)`: Validate Polygon rings.

### MultiPoint
 GeoJSON MultiPoint geometry.

### MultiLineString
 GeoJSON MultiLineString geometry.

### MultiPolygon
 GeoJSON MultiPolygon geometry.

### Feature
 GeoJSON Feature object.

### FeatureCollection
 GeoJSON FeatureCollection object.

### PolygonFeature
 A GeoJSON Feature with a Polygon geometry.

**Methods**:
- `ensure_polygon_geometry(cls, values)`: Ensure the geometry is a Polygon.

### PolygonFeatureCollection
 A GeoJSON FeatureCollection containing only Polygon features.

### Config

### Config

### Config

## Capabilities

- **15 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-API/src/geo_infer_api/models`
- **Type**: Directory Node
