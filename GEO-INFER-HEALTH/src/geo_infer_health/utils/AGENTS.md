# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 2 classes and 37 functions.

## Classes
 and Functions

### HealthConfig
 Pydantic model for health configuration validation.

### PerformanceLogger
 Context manager for performance logging.

### project_to_utm
 `project_to_utm(location: Location) -> Tuple[float, float, str]` Project a geographic location to UTM coordinates.

### buffer_point
 `buffer_point(location: Location, radius_meters: float, num_points: int) -> List[Location]` Create a circular buffer around a point.

### spatial_clustering
 `spatial_clustering(locations: List[Location], eps_km: float, min_samples: int) -> List[List[Location]]` Perform spatial clustering using DBSCAN algorithm.

### calculate_spatial_statistics
 `calculate_spatial_statistics(locations: List[Location]) -> Dict[str, float]` Calculate basic spatial statistics for a set of locations.

### validate_geographic_bounds
 `validate_geographic_bounds(locations: List[Location]) -> Dict[str, Any]` Validate that locations are within reasonable geographic bounds.

### interpolate_points
 `interpolate_points(locations: List[Location], num_points: int) -> List[Location]` Interpolate additional points along a path defined by locations.

### find_centroid
 `find_centroid(locations: List[Location]) -> Location` Calculate the centroid of a list of locations.

### calculate_voronoi_regions
 `calculate_voronoi_regions(locations: List[Location], boundary_box: Optional[Tuple[Location, Location]]) -> List[List[Location]]` Calculate Voronoi regions for a set of points.

### calculate_spatial_autocorrelation
 `calculate_spatial_autocorrelation(locations: List[Location], values: List[float], max_distance_km: float) -> Dict[str, float]` Calculate spatial autocorrelation statistics (Moran's I).

### calculate_hotspot_statistics
 `calculate_hotspot_statistics(locations: List[Location], case_counts: List[int]) -> Dict[str, Any]` Calculate hotspot statistics using spatial scan statistics.

### region_query
 `region_query(point_idx: int) -> List[int]` Find neighbors within eps distance.

### expand_cluster
 `expand_cluster(point_idx: int, neighbors: List[int]) -> List[int]` Expand cluster from a core point.

### load_yaml_config
 `load_yaml_config(file_path: Union[str, Path]) -> Dict[str, Any]` Load configuration from YAML file.

### load_json_config
 `load_json_config(file_path: Union[str, Path]) -> Dict[str, Any]` Load configuration from JSON file.

### validate_config
 `validate_config(config: Dict[str, Any]) -> HealthConfig` Validate configuration data against the HealthConfig model.

### merge_configs
 `merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]` Merge two configuration dictionaries, with override_config taking precedence.

### resolve_environment_variables
 `resolve_environment_variables(config: Dict[str, Any]) -> Dict[str, Any]` Resolve environment variables in configuration values.

### get_default_config_path
 `get_default_config_path() -> Path` Get the default configuration file path.

### load_config
 `load_config(config_path: Optional[Union[str, Path]]) -> HealthConfig` Load and validate configuration from file.

### save_config
 `save_config(config: Union[HealthConfig, Dict[str, Any]], file_path: Union[str, Path]) -> None` Save configuration to file.

### get_config_value
 `get_config_value(config: HealthConfig, key_path: str, default: Any) -> Any` Get a configuration value using dot notation.

### create_default_config
 `create_default_config(output_path: Union[str, Path]) -> None` Create a default configuration file.

### get_global_config
 `get_global_config(force_reload: bool) -> HealthConfig` Get the global configuration instance.

### reload_global_config
 `reload_global_config() -> HealthConfig` Reload the global configuration from file.

### resolve_value
 `resolve_value(value: Any) -> Any`

### replace_var
 `replace_var(match)`

### haversine_distance
 `haversine_distance(loc1: Location, loc2: Location) -> float` Calculate the Haversine distance between two points on the Earth.

### create_bounding_box
 `create_bounding_box(center_loc: Location, distance_km: float) -> Tuple[Location, Location]` Creates a square bounding box around a central point.

### setup_logging
 `setup_logging(level: str, format: str, file_path: Optional[str], max_bytes: int, backup_count: int, verbose: bool) -> None` Setup logging configuration for the application.

### get_logger
 `get_logger(name: str)` Get a logger instance with the specified name.

### log_function_call
 `log_function_call(func_name: str, log_args: bool, log_result: bool)` Decorator to log function calls.

### log_performance
 `log_performance(operation_name: str, duration: float, metadata: Optional[Dict[str, Any]])` Log performance metrics.

### create_log_context
 `create_log_context(context_info: Dict[str, Any])` Create a logging context with additional information.

### setup_structured_logging
 `setup_structured_logging(service_name: str, version: str, environment: str)` Setup structured logging for production use.

### decorator
 `decorator(func)`

### wrapper
 `wrapper(*args, **kwargs)`

## Capabilities

- **2 classes** for core functionality
- **37 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-HEALTH/src/geo_infer_health/utils`
- **Type**: Directory Node
