# Agent
: power_source ## Scope
 This directory contains power_source components for the module. It provides 2 classes and 0 functions. ## Classes
 and Functions ### CascadianPowerSourceDataSource
s
 Handles fetching and loading of power infrastructure data. **Methods**: - `fetch_power_infrastructure_features(hexagons: List[str]) -> dict`: Fetches all power infrastructure (transmission lines, power plants) ### GeoInferPowerSourc
e
 Analyzes proximity to high-voltage power infrastructure. **Methods**: - `acquire_raw_data() -> Path`: Acquire and cache raw HIFLD infrastructure features for target hexagons. - `run_analysis(target_hexagons: List[str]) -> Dict[str, Dict[str, Any]]`: Calculates the density of transmission lines and average voltage - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Summarize H3-indexed power infrastructure features into per-hex metrics. ## Capabilities
 - **2 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/power_source` - **Type**: Directory Node 