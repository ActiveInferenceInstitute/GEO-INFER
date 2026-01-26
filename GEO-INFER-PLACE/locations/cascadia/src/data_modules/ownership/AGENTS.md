# Agent
: ownership ## Scope
 This directory contains ownership components for the module. It provides 2 classes and 0 functions. ## Classes
 and Functions ### CascadianOwnershipDataSource
s
 Handles fetching of ownership parcel data from public ArcGIS services. **Methods**: - `fetch_all_parcel_data(target_hexagons: List[str]) -> gpd.GeoDataFrame`: Fetches all available parcel data from configured ArcGIS services or OSM. ### GeoInferOwnershi
p
 Processes and analyzes ownership data within an H3 grid using real OSC H3 v4 methods. **Methods**: - `acquire_raw_data() -> Path`: Acquire raw ownership data for Del Norte county. - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Perform real ownership analysis on H3-indexed data using OSC H3 v4 methods. ## Capabilities
 - **2 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/ownership` - **Type**: Directory Node 