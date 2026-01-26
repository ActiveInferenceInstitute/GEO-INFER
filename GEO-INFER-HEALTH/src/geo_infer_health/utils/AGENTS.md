# Agent
: utils ## Scope
 This directory contains utils components for the module. It provides 2 classes and 37 functions. ## Classes
 and Functions ### HealthConfi
g
 Pydantic model for health configuration validation. ### PerformanceLogge
r
 Context manager for performance logging. ### project_to_ut
m
 `project_to_utm(location: Location) -> Tuple[float, float, str]` Project a geographic location to UTM coordinates. ### buffer_poin
t
 `buffer_point(location: Location, radius_meters: float, num_points: int) -> List[Location]` Create a circular buffer around a point. ### spatial_clusterin
g
 `spatial_clustering(locations: List[Location], eps_km: float, min_samples: int) -> List[List[Location]]` Perform spatial clustering using DBSCAN algorithm. ### calculate_spatial_statistic
s
 `calculate_spatial_statistics(locations: List[Location]) -> Dict[str, float]` Calculate basic spatial statistics for a set of locations. ### validate_geographic_bound
s
 `validate_geographic_bounds(locations: List[Location]) -> Dict[str, Any]` Validate that locations are within reasonable geographic bounds. ### interpolate_point
s
 `interpolate_points(locations: List[Location], num_points: int) -> List[Location]` Interpolate additional points along a path defined by locations. ### find_centroi
d
 `find_centroid(locations: List[Location]) -> Location` Calculate the centroid of a list of locations. ### calculate_voronoi_region
s
 `calculate_voronoi_regions(locations: List[Location], boundary_box: Optional[Tuple[Location, Location]]) -> List[List[Location]]` Calculate Voronoi regions for a set of points. ### calculate_spatial_autocorrelatio
n
 `calculate_spatial_autocorrelation(locations: List[Location], values: List[float], max_distance_km: float) -> Dict[str, float]` Calculate spatial autocorrelation statistics (Moran's I). ### calculate_hotspot_statistic
s
 `calculate_hotspot_statistics(locations: List[Location], case_counts: List[int]) -> Dict[str, Any]` Calculate hotspot statistics using spatial scan statistics. ### region_quer
y
 `region_query(point_idx: int) -> List[int]` Find neighbors within eps distance. ### expand_cluste
r
 `expand_cluster(point_idx: int, neighbors: List[int]) -> List[int]` Expand cluster from a core point. ### load_yaml_confi
g
 `load_yaml_config(file_path: Union[str, Path]) -> Dict[str, Any]` Load configuration from YAML file. ### load_json_confi
g
 `load_json_config(file_path: Union[str, Path]) -> Dict[str, Any]` Load configuration from JSON file. ### validate_confi
g
 `validate_config(config: Dict[str, Any]) -> HealthConfig` Validate configuration data against the HealthConfig model. ### merge_config
s
 `merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]` Merge two configuration dictionaries, with override_config taking precedence. ### resolve_environment_variable
s
 `resolve_environment_variables(config: Dict[str, Any]) -> Dict[str, Any]` Resolve environment variables in configuration values. ### get_default_config_pat
h
 `get_default_config_path() -> Path` Get the default configuration file path. ### load_confi
g
 `load_config(config_path: Optional[Union[str, Path]]) -> HealthConfig` Load and validate configuration from file. ### save_confi
g
 `save_config(config: Union[HealthConfig, Dict[str, Any]], file_path: Union[str, Path]) -> None` Save configuration to file. ### get_config_valu
e
 `get_config_value(config: HealthConfig, key_path: str, default: Any) -> Any` Get a configuration value using dot notation. ### create_default_confi
g
 `create_default_config(output_path: Union[str, Path]) -> None` Create a default configuration file. ### get_global_confi
g
 `get_global_config(force_reload: bool) -> HealthConfig` Get the global configuration instance. ### reload_global_confi
g
 `reload_global_config() -> HealthConfig` Reload the global configuration from file. ### resolve_valu
e
 `resolve_value(value: Any) -> Any` ### replace_va
r
 `replace_var(match)` ### haversine_distanc
e
 `haversine_distance(loc1: Location, loc2: Location) -> float` Calculate the Haversine distance between two points on the Earth. ### create_bounding_bo
x
 `create_bounding_box(center_loc: Location, distance_km: float) -> Tuple[Location, Location]` Creates a square bounding box around a central point. ### setup_loggin
g
 `setup_logging(level: str, format: str, file_path: Optional[str], max_bytes: int, backup_count: int, verbose: bool) -> None` Setup logging configuration for the application. ### get_logge
r
 `get_logger(name: str)` Get a logger instance with the specified name. ### log_function_cal
l
 `log_function_call(func_name: str, log_args: bool, log_result: bool)` Decorator to log function calls. ### log_performanc
e
 `log_performance(operation_name: str, duration: float, metadata: Optional[Dict[str, Any]])` Log performance metrics. ### create_log_contex
t
 `create_log_context(context_info: Dict[str, Any])` Create a logging context with additional information. ### setup_structured_loggin
g
 `setup_structured_logging(service_name: str, version: str, environment: str)` Setup structured logging for production use. ### decorato
r
 `decorator(func)` ### wrappe
r
 `wrapper(*args, **kwargs)` ## Capabilities
 - **2 classes** for core functionality - **37 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-HEALTH/src/geo_infer_health/utils` - **Type**: Directory Node 