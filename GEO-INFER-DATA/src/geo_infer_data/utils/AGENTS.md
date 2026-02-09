# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 11 classes and 1 functions.

## Classes
 and Functions

### CacheEntry
 Cache entry with metadata.

**Methods**:
- `is_expired() -> bool`: Check if cache entry is expired.
- `update_access()`: Update access statistics.

### CacheManager
 caching manager for geospatial data.

**Methods**:
- `get_stats() -> Dict[str, Any]`: Get cache statistics.
- `generate_cache_key(spatial_bounds: Optional[List[float]], temporal_range: Optional[Tuple[datetime, datetime]], query_params: Optional[Dict[str, Any]]) -> str`: Generate cache key from query parameters.
- `optimize_cache()`: Optimize cache performance.

### DataCompressor
 Data compression for efficient storage.

**Methods**:
- `is_enabled() -> bool`: Check if compression is enabled.
- `compress_data(data: Any, format: Optional[DataFormat]) -> bytes`: Compress geospatial data.
- `decompress_data(compressed_data: bytes, format: Optional[DataFormat]) -> Any`: Decompress geospatial data.
- `get_compression_stats() -> Dict[str, Any]`: Get compression statistics.
- `optimize_for_storage(data: Any) -> Dict[str, Any]`: Optimize data for storage with compression recommendations.

### FormatDetector
 Automatic format detection for geospatial data.

**Methods**:
- `detect_from_path(file_path: Union[str, Path]) -> DataFormat`: Detect format from file path.
- `detect_from_content(file_path: Union[str, Path]) -> DataFormat`: Detect format from file content.
- `detect_format(data: Any) -> DataFormat`: Detect format from data object.
- `get_supported_formats() -> List[DataFormat]`: Get list of supported formats.
- `validate_format(file_path: Union[str, Path], expected_format: DataFormat) -> bool`: Validate that file matches expected format.

### SpatialIndexer
 Spatial indexing for efficient geospatial queries.

**Methods**:
- `create_spatial_index(data: gpd.GeoDataFrame, strategy: str) -> str`: Create spatial index for geospatial data.
- `query_by_bounds(index_id: str, bbox: List[float]) -> gpd.GeoDataFrame`: Query spatial index by bounding box.
- `latlng_to_cell(lat: float, lng: float, resolution: int) -> str`: Convert latitude/longitude to H3 cell.
- `cell_to_latlng(cell: str) -> Tuple[float, float]`: Convert H3 cell to latitude/longitude.

### TemporalIndexer
 Temporal indexing for efficient time-based queries.

**Methods**:
- `create_temporal_index(data: Union[pd.DataFrame, gpd.GeoDataFrame], time_column: str) -> str`: Create temporal index for time-based queries.
- `query_by_time_range(index_id: str, start_time: Union[str, pd.Timestamp], end_time: Union[str, pd.Timestamp]) -> Union[pd.DataFrame, gpd.GeoDataFrame]`: Query temporal index by time range.
- `query_by_time_point(index_id: str, time_point: Union[str, pd.Timestamp]) -> Union[pd.DataFrame, gpd.GeoDataFrame]`: Query temporal index by time point.

### PerformanceMonitor
 Performance monitoring for data operations.

**Methods**:
- `track_operation(operation_name: str) -> 'OperationTracker'`: Track performance of an operation.
- `record_metric(operation_name: str, metric_name: str, value: float)`: Record a custom metric.
- `get_metrics() -> Dict[str, Any]`: Get performance metrics.
- `identify_bottlenecks() -> List[Dict[str, Any]]`: Identify performance bottlenecks.
- `reset_metrics()`: Reset all performance metrics.

### OperationTracker
 Context manager for tracking operation performance.

### DataProcessingProfiler
 Profiler for data processing operations.

**Methods**:
- `profile_step(step_name: str) -> 'StepProfiler'`: Profile a processing step.
- `start_profiling()`: Start profiling session.
- `end_profiling()`: End profiling session.
- `get_profile() -> Dict[str, Any]`: Get profiling results.

### StepProfiler
 Context manager for profiling individual steps.

### GeospatialValidator
 geospatial data validation.

**Methods**:
- `validate_geometries(geodataframe: gpd.GeoDataFrame) -> QualityCheck`: Validate geometries in a GeoDataFrame.
- `validate_coordinates(data: Union[pd.DataFrame, gpd.GeoDataFrame]) -> QualityCheck`: Validate coordinate data.
- `validate_temporal_data(data: Union[pd.DataFrame, gpd.GeoDataFrame]) -> QualityCheck`: Validate temporal data.

### monitor_system
 `monitor_system()`

## Capabilities

- **11 classes** for core functionality
- **1 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-DATA/src/geo_infer_data/utils`
- **Type**: Directory Node
