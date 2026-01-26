# Agent
: mortgage_debt ## Scope
 This directory contains mortgage_debt components for the module. It provides 2 classes and 0 functions. ## Classes
 and Functions ### CascadianMortgageDataSource
s
 Handles fetching and processing of HMDA mortgage data. **Methods**: - `fetch_all_mortgage_data(year: int) -> pd.DataFrame`: Loads all available HMDA mortgage data for target counties. ### GeoInferMortgageDeb
t
 Processes and analyzes mortgage data aggregated at the census tract level. **Methods**: - `acquire_raw_data(year: int) -> Path`: Acquire and cache raw mortgage data merged to census tract geometries. - `run_analysis(target_hexagons: List[str], year: int) -> Dict[str, Dict[str, Any]]`: Spatially joins HMDA mortgage data with H3 hexagons and calculates debt metrics. - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Summarize H3 mortgage features into per-hex metrics if needed. ## Capabilities
 - **2 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/mortgage_debt` - **Type**: Directory Node 