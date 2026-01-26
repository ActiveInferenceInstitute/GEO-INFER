# api
 ## Overview
 This directory contains api components. It includes 2 Python modules. ## Components
 ### rest_ap
i
.py FastAPI REST API for GEO-INFER-SPACE spatial services. **Functions**: `geojson_to_gdf`, `gdf_to_geojson` ### schema
s
.py Pydantic schemas for API request/response validation. **Classes**: `SpatialAnalysisRequest`, `SpatialAnalysisResponse`, `BufferAnalysisRequest`, `ProximityAnalysisRequest`, `InterpolationRequest`, `ClusteringRequest`, `HotspotRequest`, `NetworkAnalysisRequest`, `TerrainAnalysisRequest`, `H3AnalysisRequest`, `ErrorResponse` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 