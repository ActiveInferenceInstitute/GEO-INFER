# Agent
: current_use ## Scope
 This directory contains current_use components for the module. It provides 3 classes and 0 functions. ## Classes
 and Functions ### CropClassificatio
n
 ### CascadianCurrentUseDataSource
s
 Multi-source agricultural land use classification for Cascadian bioregion **Methods**: - `fetch_nass_cdl_data_for_hexagons(year: int, hexagons: List[str]) -> Dict[str, List[Tuple[int, float]]]`: Fetches and processes NASS CDL data for a list of hexagons, chunking requests. - `fetch_land_iq_data(county: str) -> gpd.GeoDataFrame`: Fetches Land IQ land use data for a specific county in California. - `get_usda_county_stats(county_fips: str, year: int) -> Optional[Dict]`: Fetches USDA NASS county-level statistics for validation. - `fetch_oregon_efu_reports(year: int) -> pd.DataFrame`: Fetch Oregon EFU land use reports from local file - `get_crop_classification(crop_code: int) -> Optional[CropClassification]`: Get crop classification information - `classify_crop_category(crop_code: int) -> str`: Classify crop into a general category - `estimate_water_requirements(crop_code: int) -> str`: Estimate water requirements for a crop - `estimate_economic_value(crop_code: int) -> float`: Estimate economic value for a crop - `get_seasonal_pattern(crop_code: int) -> str`: Get seasonal pattern for a crop - `validate_data_availability(year: int, source: str) -> bool`: Validate data availability for a given year and source. - `get_available_years(source: str) -> List[int]`: Get available years for a data source. - `get_target_counties(state: str) -> List[str]`: Get target counties for analysis. ### GeoInferCurrentUs
e
 **Methods**: - `acquire_raw_data() -> Path`: Acquire raw current use data for Del Norte county. - `run_final_analysis(h3_data: Dict[str, Any]) -> Dict[str, Any]`: Generate H3-indexed current agricultural use classification using real OSC H3 v4 methods. ## Capabilities
 - **3 classes** for core functionality ## Integration
 - **Location**: `cascadia/src/data_modules/current_use` - **Type**: Directory Node 