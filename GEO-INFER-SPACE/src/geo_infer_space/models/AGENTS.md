# Agent
: models ## Scope
 This directory contains models components for the module. It provides 21 classes and 1 functions. ## Classes
 and Functions ### DatabaseConfi
g
 Configuration for spatial database connections. **Methods**: - `validate_port(cls, v)`: - `validate_pool_size(cls, v)`: - `get_connection_string() -> str`: Generate database connection string. ### IndexingConfi
g
 Configuration for spatial indexing systems. **Methods**: - `validate_index_type(cls, v)`: - `validate_cache_size(cls, v)`: ### AnalysisConfi
g
 Configuration for spatial analysis operations. **Methods**: - `validate_buffer_resolution(cls, v)`: - `validate_chunk_size(cls, v)`: - `validate_resampling_method(cls, v)`: - `validate_interpolation_method(cls, v)`: ### APIConfi
g
 Configuration for REST API server. **Methods**: - `validate_port(cls, v)`: - `validate_workers(cls, v)`: - `validate_request_size(cls, v)`: ### LoggingConfi
g
 Configuration for logging system. **Methods**: - `validate_level(cls, v)`: - `validate_file_size(cls, v)`: ### CacheConfi
g
 Configuration for caching system. **Methods**: - `validate_backend(cls, v)`: - `validate_ttl(cls, v)`: ### OSCConfi
g
 Configuration for OS-Climate integration. **Methods**: - `validate_update_interval(cls, v)`: ### SpaceConfi
g
 Main configuration model for GEO-INFER-SPACE. **Methods**: - `validate_environment(cls, v)`: - `validate_directories()`: Ensure directories exist or can be created. - `from_file(cls, config_path: Union[str, Path]) -> 'SpaceConfig'`: Load configuration from YAML or JSON file. - `to_file(config_path: Union[str, Path], format: str) -> None`: Save configuration to file. ### PerformanceConfi
g
 Configuration for performance optimization. **Methods**: - `validate_chunk_size(cls, v)`: - `validate_buffer_size(cls, v)`: ### GeometryTyp
e
 Enumeration of supported geometry types. ### CoordinateReferenceSyste
m
 Model for coordinate reference system information. **Methods**: - `validate_epsg_code(cls, v)`: ### GeometryMode
l
 Model for geometry objects with validation. **Methods**: - `to_feature() -> Feature`: Convert to GeoJSON Feature. ### SpatialBound
s
 Model for spatial bounding box. **Methods**: - `validate_x_bounds(cls, v, values)`: - `validate_y_bounds(cls, v, values)`: - `width() -> float`: Calculate width of bounding box. - `height() -> float`: Calculate height of bounding box. - `area() -> float`: Calculate area of bounding box. ### SpatialInde
x
 Model for spatial index configuration. **Methods**: - `validate_index_type(cls, v)`: ### SpatialMetadat
a
 Model for spatial dataset metadata. **Methods**: - `validate_num_features(cls, v)`: ### SpatialDatase
t
 Model for spatial dataset. **Methods**: - `validate_features(cls, v, values)`: - `get_bounds() -> Optional[SpatialBounds]`: Calculate spatial bounds of the dataset. ### AnalysisResul
t
 Model for spatial analysis results. **Methods**: - `validate_execution_time(cls, v)`: ### H3CellDat
a
 Model for H3 hexagonal cell data. **Methods**: - `validate_h3_index(cls, v)`: - `validate_latitude(cls, v)`: - `validate_longitude(cls, v)`: ### NetworkEdg
e
 Model for network edge data. **Methods**: - `validate_geometry_type(cls, v)`: ### NetworkNod
e
 Model for network node data. **Methods**: - `validate_geometry_type(cls, v)`: ### SpatialNetwor
k
 Model for spatial network data. **Methods**: - `num_nodes() -> int`: Number of nodes in the network. - `num_edges() -> int`: Number of edges in the network. - `get_bounds() -> Optional[SpatialBounds]`: Calculate spatial bounds of the network. ### convert_path
s
 `convert_paths(obj)` ## Capabilities
 - **21 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-SPACE/src/geo_infer_space/models` - **Type**: Directory Node 