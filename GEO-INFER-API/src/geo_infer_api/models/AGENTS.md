# Agent
: models ## Scope
 This directory contains models components for the module. It provides 15 classes and 0 functions. ## Classes
 and Functions ### GeoJSONTyp
e
 Valid GeoJSON types. ### GeometryBas
e
 Base model for all GeoJSON geometry objects. ### Poin
t
 GeoJSON Point geometry. **Methods**: - `validate_coordinates(cls, v)`: Validate point coordinates. ### LineStrin
g
 GeoJSON LineString geometry. **Methods**: - `validate_coordinates(cls, v)`: Validate LineString has at least 2 points. ### Polygo
n
 GeoJSON Polygon geometry. **Methods**: - `validate_coordinates(cls, v)`: Validate Polygon rings. ### MultiPoin
t
 GeoJSON MultiPoint geometry. ### MultiLineStrin
g
 GeoJSON MultiLineString geometry. ### MultiPolygo
n
 GeoJSON MultiPolygon geometry. ### Featur
e
 GeoJSON Feature object. ### FeatureCollectio
n
 GeoJSON FeatureCollection object. ### PolygonFeatur
e
 A GeoJSON Feature with a Polygon geometry. **Methods**: - `ensure_polygon_geometry(cls, values)`: Ensure the geometry is a Polygon. ### PolygonFeatureCollectio
n
 A GeoJSON FeatureCollection containing only Polygon features. ### Confi
g
 ### Confi
g
 ### Confi
g
 ## Capabilities
 - **15 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-API/src/geo_infer_api/models` - **Type**: Directory Node 