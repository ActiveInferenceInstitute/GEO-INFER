# Agent
: ground_water ## Scope
 This directory contains ground_water components for the module. It provides 2 classes and 0 functions. ## Classes
 and Functions ### CascadianGroundWaterDataSource
s
 Manages the acquisition and processing of groundwater data from USGS NWIS. **Methods**: - `fetch_groundwater_data(hexagons: List[str]) -> gpd.GeoDataFrame`: Fetches groundwater well data from the USGS NWIS for a list of H3 hexagons, ### GeoInferGroundWate
r
 Analyzes groundwater availability by fetching real well data from the USGS **Methods**: - `acquire_raw_data() -> Path`: Acquire and cache raw groundwater wells in target area. - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Pass-through for groundwater presence when features already summarized upstream. - `run_analysis(target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]`: Performs groundwater analysis by querying the USGS NWIS for wells within ## Capabilities
 - **2 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/ground_water` - **Type**: Directory Node 