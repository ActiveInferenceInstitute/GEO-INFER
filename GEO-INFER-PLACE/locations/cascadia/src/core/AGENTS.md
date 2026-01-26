# Agent
: core ## Scope
 This directory contains core components for the module. It provides 24 classes and 27 functions. ## Classes
 and Functions ### SpatialProcesso
r
 **Methods**: - `calculate_spatial_correlation(scores1, scores2)`: ### DataCleanupManage
r
 Manages data cleanup and reorganization for the Cascadia framework. **Methods**: - `cleanup_old_runs(keep_recent_runs: int)`: Clean up old run data from output directory. - `move_module_data_to_modules()`: Move module-specific data from output/data to appropriate module directories. - `cleanup_output_data_directory()`: Clean up the output/data directory after moving data to modules. - `create_module_data_structure()`: Create standardized data structure for each module. - `update_data_manager_paths()`: Update the data manager to use module-specific paths. - `run_full_cleanup(keep_recent_runs: int)`: Run cleanup and reorganization. ### NumpyEncode
r
 **Methods**: - `default(obj)`: ### EmpiricalDataDownloade
r
 Downloads real empirical data for Del Norte county. **Methods**: - `download_census_data()`: Download Census TIGER/Line data for Del Norte county. - `download_and_process_dataset(url: str, dataset_name: str)`: Download and process a specific dataset. - `filter_to_del_norte(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame`: Filter data to Del Norte county bounds. - `create_empirical_zoning_data()`: Create empirical zoning data from California FMMP data. - `create_empirical_current_use_data()`: Create empirical current use data from NASS CDL. - `create_empirical_ownership_data()`: Create empirical ownership data from county records. - `create_empirical_improvements_data()`: Create empirical improvements data from building footprints. - `download_all_empirical_data()`: Download all empirical data sources. ### EmpiricalDataAssesso
r
 Assesses empirical data quality and sources for Del Norte county. **Methods**: - `assess_data_sources()`: Assess all data sources for empirical quality. - `assess_data_directory(data_dir: Path)`: Assess data in a specific directory. - `assess_data_file(file_path: Path)`: Assess the quality of a data file. - `assess_geojson_file(file_path: Path)`: Assess GeoJSON file quality and content. - `assess_json_file(file_path: Path)`: Assess JSON file quality and content. - `check_empirical_indicators(gdf: gpd.GeoDataFrame, file_name: str)`: Check for indicators of empirical vs synthetic data. - `generate_assessment_report()`: Generate a assessment report. ### AnalysisConfi
g
 Configuration for analysis parameters. ### VisualizationConfi
g
 Configuration for visualization settings. ### DataConfi
g
 Configuration for data processing. ### ModuleConfi
g
 Configuration for individual modules. ### CascadiaConfi
g
 Main configuration class for Cascadia framework. ### EnhancedConfigManage
r
 configuration manager for Cascadia framework. **Methods**: - `load_configuration() -> CascadiaConfig`: Load configuration from files or create default. - `save_configuration(config: CascadiaConfig)`: Save configuration to file. - `update_configuration(updates: Dict[str, Any])`: Update configuration with values. - `get_analysis_config() -> AnalysisConfig`: Get analysis configuration. - `get_visualization_config() -> VisualizationConfig`: Get visualization configuration. - `get_data_config() -> DataConfig`: Get data configuration. - `get_module_config() -> ModuleConfig`: Get module configuration. - `get_active_modules() -> List[str]`: Get list of active modules. - `is_module_enabled(module_name: str) -> bool`: Check if a module is enabled. - `get_module_config(module_name: str) -> Dict[str, Any]`: Get configuration for a specific module. - `validate_configuration() -> Dict[str, Any]`: Validate configuration and return validation results. ### EnhancedDataManage
r
 data manager for Cascadia agricultural analysis. **Methods**: - `get_data_quality_report(module_name: str) -> Dict[str, Any]`: Generate data quality report for a module. - `benchmark_performance(module_name: str) -> Dict[str, Any]`: Benchmark performance for a module's data processing operations. - `get_data_structure(module_name: str) -> Dict[str, Path]`: Get the standardized data structure for a module. - `acquire_data_with_caching(module_name: str, data_source_func, force_refresh: bool) -> Path`: Acquire data with caching and validation. - `process_to_h3_with_caching(data_path: Path, module_name: str, target_hexagons: List[str]) -> Dict[str, Any]`: Process data to H3 format with caching. - `get_data_quality_report(module_name: str) -> Dict[str, Any]`: Generate data quality report. - `cleanup_old_cache(max_age_days: int) -> int`: Clean up old cache files. ### EnhancedH3Fusio
n
 H3 geospatial fusion engine for Cascadia agricultural analysis. **Methods**: - `fuse_geospatial_data(data_sources: Dict[str, Any], target_hexagons: List[str]) -> Dict[str, Any]`: Fuse multiple geospatial data sources into unified H3-indexed format. - `load_fusion_cache(data_sources: Dict[str, Any], target_hexagons: List[str]) -> Optional[Dict[str, Any]]`: Attempt to load fused data from cache based on inputs. - `save_fusion_cache(data_sources: Dict[str, Any], target_hexagons: List[str], fused_data: Dict[str, Any], report: Optional[Dict[str, Any]]) -> Optional[Path]`: Persist fused data and report to cache. - `validate_h3_operations() -> Dict[str, Any]`: Validate H3 operations and API usage. ### EnhancedLoggingConfi
g
 logging configuration for Cascadia framework. **Methods**: - `setup_logging(log_level: str, log_file: Optional[Path], console_output: bool, include_timestamps: bool, include_module_names: bool, include_line_numbers: bool) -> logging.Logger`: Set up logging configuration. ### DataSourceLogge
r
 Specialized logger for data source operations. **Methods**: - `log_real_data_acquisition(source_url: str, file_path: Path, data_type: str, row_count: int, file_size_mb: float, geometry_types: List[str], crs: str, bbox: Optional[tuple], attributes: Optional[List[str]])`: Log information about real data acquisition. - `log_synthetic_data_generation(reason: str, parameters: Dict[str, Any], row_count: int, coverage_area_km2: float, geometry_types: List[str])`: Log synthetic data generation with clear marking. - `log_fallback_data_usage(original_source: str, fallback_reason: str, fallback_type: str, limitations: List[str])`: Log fallback data usage with clear limitations. - `log_data_validation(validation_results: Dict[str, Any], quality_score: float, issues: List[str])`: Log data validation results. - `log_h3_processing(input_features: int, output_hexagons: int, coverage_percentage: float, processing_time: float)`: Log H3 processing results. ### ProcessingLogge
r
 Specialized logger for data processing operations. **Methods**: - `log_processing_start(operation: str, parameters: Dict[str, Any])`: Log the start of a processing operation. - `log_processing_step(step: str, details: Dict[str, Any])`: Log a processing step. - `log_processing_complete(operation: str, results: Dict[str, Any], duration: float)`: Log the completion of a processing operation. ### VisualizationLogge
r
 Specialized logger for visualization operations. **Methods**: - `log_visualization_creation(viz_type: str, data_sources: List[str], hexagon_count: int, layers: List[str], interactive_features: List[str])`: Log visualization creation. - `log_interactive_feature(feature: str, status: str)`: Log interactive feature status. ### PerformanceLogge
r
 Specialized logger for performance metrics. **Methods**: - `log_performance_metrics(operation: str, duration: float, memory_usage_mb: float, cpu_usage_percent: float, data_size_mb: float)`: Log performance metrics. ### RealDataAcquisitio
n
 real data acquisition system for Cascadia framework. **Methods**: - `acquire_zoning_data() -> Optional[Path]`: Acquire real zoning data from Del Norte County and state sources. - `acquire_current_use_data() -> Optional[Path]`: Acquire real current land use data from USDA and state sources. - `acquire_ownership_data() -> Optional[Path]`: Attempt to acquire ownership data via configured sources; return path or None. - `acquire_improvements_data() -> Optional[Path]`: Attempt to acquire improvements data via configured sources; return path or None. ### SpatialProcesso
r
 **Methods**: - `calculate_spatial_correlation(scores1, scores2)`: ### SpatialProcesso
r
 **Methods**: - `calculate_spatial_correlation(scores1, scores2)`: ### DataIntegrato
r
 ### InteractiveVisualizationEngin
e
 **Methods**: - `create_comprehensive_dashboard(*args, **kwargs)`: ### LocationBound
s
 ### perform_enhanced_spatial_analysi
s
 `perform_enhanced_spatial_analysis(backend, spatial_processor: SpatialProcessor) -> Dict[str, Any]` Perform spatial analysis using SPACE capabilities ### run_comprehensive_analysi
s
 `run_comprehensive_analysis(backend, modules: Dict, args) -> Tuple[Dict, Dict]` Run analysis with real data tracking and reporting. ### create_data_cleanup_manage
r
 `create_data_cleanup_manager(base_dir: Path) -> DataCleanupManager` Create a data cleanup manager instance. ### initialize_module
s
 `initialize_modules(active_modules: List[str], shared_backend, osc_repo_path: str) -> Dict[str, Any]` Initialize all available modules using the shared backend ### create_shared_backen
d
 `create_shared_backend(resolution: int, target_counties: Dict, output_dir: Path, osc_repo_path: str) -> CascadianAgriculturalH3Backend` Create a single shared backend for all modules ### export_result
s
 `export_results(backend, redevelopment_scores: Dict, summary: Dict, output_dir: Path, timestamp: str, bioregion_lower: str, export_format: str) -> Dict[str, str]` Export analysis results with visualization options. ### validate_data_acquisitio
n
 `validate_data_acquisition(modules: Dict) -> Dict[str, int]` Validate data acquisition for each module ### mai
n
 `main()` Main function to download empirical data. ### mai
n
 `main()` Main function to run the empirical data assessment. ### create_enhanced_config_manage
r
 `create_enhanced_config_manager(config_dir: Path) -> EnhancedConfigManager` Create an configuration manager instance. ### create_enhanced_data_manage
r
 `create_enhanced_data_manager(base_data_dir: Path, h3_resolution: int) -> EnhancedDataManager` Factory function to create an data manager. ### create_enhanced_h3_fusio
n
 `create_enhanced_h3_fusion(h3_resolution: int, enable_spatial_analysis: bool, cache_dir: Optional[Path], fusion_mode: str) -> EnhancedH3Fusion` Factory function to create an H3 fusion engine. ### create_enhanced_logge
r
 `create_enhanced_logger(module_name: str) -> tuple` Create loggers for a module. ### log_dataframe_summar
y
 `log_dataframe_summary(logger: logging.Logger, df: pd.DataFrame, name: str)` Log a summary of a DataFrame. ### log_geodataframe_summar
y
 `log_geodataframe_summary(logger: logging.Logger, gdf: gpd.GeoDataFrame, name: str)` Log a summary of a GeoDataFrame. ### create_real_data_acquisitio
n
 `create_real_data_acquisition(output_dir: Path) -> RealDataAcquisition` Create a real data acquisition instance. ### generate_spatial_analysis_repor
t
 `generate_spatial_analysis_report(backend, output_dir: Path) -> str` Generate spatial analysis report using SPACE capabilities ### generate_enhanced_dashboar
d
 `generate_enhanced_dashboard(backend, output_dir: Path, visualization_engine) -> str` Generate interactive dashboard using SPACE visualization engine ### generate_analysis_repor
t
 `generate_analysis_report(summary: Dict[str, Any], output_path: Path) -> None` Generate a analysis report in Markdown format with SPACE integration. ### export_data_provenanc
e
 `export_data_provenance(provenance: Dict[str, Any], output_dir: Path) -> Path` Write a machine-readable data provenance manifest. ### fm
t
 `fmt(value)` ### setup_loggin
g
 `setup_logging(verbose: bool, output_dir: str) -> None` Setup logging configuration with SPACE integration ### check_dependencie
s
 `check_dependencies() -> bool` Check and report on all dependencies with SPACE integration ### setup_spatial_processo
r
 `setup_spatial_processor() -> SpatialProcessor` Initialize SPACE spatial processor with Cascadia configuration ### setup_data_integrato
r
 `setup_data_integrator() -> DataIntegrator` Initialize SPACE data integrator for Cascadia data sources ### load_analysis_confi
g
 `load_analysis_config() -> Dict[str, Any]` Load analysis configuration with SPACE integration ### setup_visualization_engin
e
 `setup_visualization_engine(output_dir: Path) -> InteractiveVisualizationEngine` Initialize SPACE visualization engine with Cascadia configuration ## Capabilities
 - **24 classes** for core functionality - **27 functions** for utility operations ## Integration
 - **Location**: `locations/cascadia/src/core` - **Type**: Directory Node 