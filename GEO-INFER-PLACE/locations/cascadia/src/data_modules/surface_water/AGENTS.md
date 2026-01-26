# Agent
: surface_water ## Scope
 This directory contains surface_water components for the module. It provides 2 classes and 0 functions. ## Classes
 and Functions ### CascadianSurfaceWaterDataSource
s
 Handles fetching of surface water data from the USGS NHD ArcGIS service. **Methods**: - `fetch_surface_water_features(bbox: Tuple[float, float, float, float]) -> dict`: Fetches all relevant surface water features (flowlines and waterbodies) ### GeoInferSurfaceWate
r
 Analyzes surface water features by quantifying the area of water bodies **Methods**: - `acquire_raw_data() -> Path`: Acquire and cache raw NHD flowlines/waterbodies for target area. - `run_analysis(target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]`: Calculates the area of water bodies and length of flowlines for each hexagon. - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Summarize H3-indexed water features into per-hex metrics if provided as features. ## Capabilities
 - **2 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/surface_water` - **Type**: Directory Node 