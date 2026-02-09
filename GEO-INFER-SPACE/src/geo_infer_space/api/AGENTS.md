# Agent
: api

## Scope
 This directory contains api components for the module. It provides 11 classes and 2 functions.

## Classes
 and Functions

### SpatialAnalysisRequest
 Base request model for spatial analysis operations.

### SpatialAnalysisResponse
 Base response model for spatial analysis results.

### BufferAnalysisRequest
 Request model for buffer analysis operations.

### ProximityAnalysisRequest
 Request model for proximity analysis operations.

### InterpolationRequest
 Request model for spatial interpolation operations.

**Methods**:
- `validate_method(cls, v)`:

### ClusteringRequest
 Request model for spatial clustering operations.

**Methods**:
- `validate_method(cls, v)`:

### HotspotRequest
 Request model for hotspot detection operations.

**Methods**:
- `validate_method(cls, v)`:

### NetworkAnalysisRequest
 Request model for network analysis operations.

**Methods**:
- `validate_analysis_type(cls, v)`:

### TerrainAnalysisRequest
 Request model for terrain analysis operations.

**Methods**:
- `validate_analyses(cls, v)`:

### H3AnalysisRequest
 Request model for H3 hexagonal grid operations.

**Methods**:
- `validate_operation(cls, v)`:

### ErrorResponse
 Error response model.

### geojson_to_gdf
 `geojson_to_gdf(geojson_data: Dict[str, Any], crs: str) -> gpd.GeoDataFrame` Convert GeoJSON data to GeoDataFrame.

### gdf_to_geojson
 `gdf_to_geojson(gdf: gpd.GeoDataFrame) -> Dict[str, Any]` Convert GeoDataFrame to GeoJSON.

## Capabilities

- **11 classes** for core functionality
- **2 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-SPACE/src/geo_infer_space/api`
- **Type**: Directory Node
