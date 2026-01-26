# Agent
: api ## Scope
 This directory contains api components for the module. It provides 11 classes and 2 functions. ## Classes
 and Functions ### SpatialAnalysisReques
t
 Base request model for spatial analysis operations. ### SpatialAnalysisRespons
e
 Base response model for spatial analysis results. ### BufferAnalysisReques
t
 Request model for buffer analysis operations. ### ProximityAnalysisReques
t
 Request model for proximity analysis operations. ### InterpolationReques
t
 Request model for spatial interpolation operations. **Methods**: - `validate_method(cls, v)`: ### ClusteringReques
t
 Request model for spatial clustering operations. **Methods**: - `validate_method(cls, v)`: ### HotspotReques
t
 Request model for hotspot detection operations. **Methods**: - `validate_method(cls, v)`: ### NetworkAnalysisReques
t
 Request model for network analysis operations. **Methods**: - `validate_analysis_type(cls, v)`: ### TerrainAnalysisReques
t
 Request model for terrain analysis operations. **Methods**: - `validate_analyses(cls, v)`: ### H3AnalysisReques
t
 Request model for H3 hexagonal grid operations. **Methods**: - `validate_operation(cls, v)`: ### ErrorRespons
e
 Error response model. ### geojson_to_gd
f
 `geojson_to_gdf(geojson_data: Dict[str, Any], crs: str) -> gpd.GeoDataFrame` Convert GeoJSON data to GeoDataFrame. ### gdf_to_geojso
n
 `gdf_to_geojson(gdf: gpd.GeoDataFrame) -> Dict[str, Any]` Convert GeoDataFrame to GeoJSON. ## Capabilities
 - **11 classes** for core functionality - **2 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPACE/src/geo_infer_space/api` - **Type**: Directory Node 