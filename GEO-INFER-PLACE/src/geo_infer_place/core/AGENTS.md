# Agent
: core ## Scope
 This directory contains core components for the module. It provides 9 classes and 0 functions. ## Classes
 and Functions ### CALFIREClien
t
 Client for CAL FIRE data access. **Methods**: - `fetch_incidents() -> Any`: Fetch active fire incidents from CAL FIRE. - `fetch_perimeters(year: Optional[int], county: Optional[str]) -> Dict[str, Any]`: Fetch fire perimeters data. ### NOAAClien
t
 Client for NOAA Tides and Currents data. **Methods**: - `fetch_weather_observations(station_id: str) -> Dict[str, Any]`: Fetch latest weather observations for a station. - `fetch_tide_data(station: str, begin_date: str, end_date: str, product: str) -> Dict[str, Any]`: Fetch tide gauge data. ### USGSClien
t
 Client for USGS water data. **Methods**: - `fetch_water_data(sites: str, start: str, end: str, parameter_cd: str) -> Dict[str, Any]`: Fetch water data from USGS. ### USGSEarthquakeClien
t
 Client for USGS Earthquake data. **Methods**: - `fetch_earthquakes(feed: str) -> Dict[str, Any]`: Fetch earthquake data feed. ### CDECClien
t
 Client for California Data Exchange Center. **Methods**: - `fetch_sensor_data(stations: str, sensor_num: str, start_date: str, end_date: str) -> Dict[str, Any]`: Fetch sensor data from CDEC. ### CaliforniaAPIManage
r
 Manager class that aggregates California-specific API clients. ### BaseAnalysisModul
e
 Abstract Base Class for a GEO-INFER analysis module. **Methods**: - `acquire_raw_data() -> Path`: Acquires raw data from its source (API, file download, etc.). - `process_to_h3(raw_data_path: Path) -> dict`: Processes a raw data file (e.g., GeoJSON, Shapefile) into an H3-indexed dictionary. - `run_final_analysis(h3_data: dict) -> dict`: Performs the final, module-specific analysis on H3-indexed data. - `run_analysis() -> dict`: Executes the full, standardized workflow for the module. ### CascadianAgriculturalH3Backen
d
 H3-based backend for agricultural analysis in the Cascadian bioregion **Methods**: - `run_comprehensive_analysis() -> None`: analysis with SPACE integration. - `calculate_agricultural_redevelopment_potential() -> Dict[str, Dict]`: redevelopment score calculation with SPACE integration. - `get_comprehensive_summary() -> Dict[str, Any]`: summary with SPACE integration. - `export_unified_data(output_path: str, export_format: str) -> None`: export with SPACE utilities. - `generate_interactive_dashboard(output_path: str) -> None`: interactive dashboard generation with SPACE visualization. ### InteractiveVisualizationEngin
e
 Interactive visualization engine for place-based dashboards. **Methods**: - `create_comprehensive_dashboard(analysis_results: Dict[str, Any], dashboard_config: Optional[Dict]) -> str`: Create interactive dashboard with all analysis results. ## Capabilities
 - **9 classes** for core functionality ## Integration
 - **Location**: `GEO-INFER-PLACE/src/geo_infer_place/core` - **Type**: Directory Node 