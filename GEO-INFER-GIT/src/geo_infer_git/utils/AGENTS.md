# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 54 classes and 31 functions.

## Classes
 and Functions

### CacheEntry
 A cache entry with metadata.

**Methods**:
- `is_expired() -> bool`: Check if the cache entry has expired.
- `access() -> None`: Mark the entry as accessed.
- `get_age_seconds() -> float`: Get age of the cache entry in seconds.

### CacheStatistics
 Statistics for cache performance monitoring.

**Methods**:
- `hit_rate() -> float`: Get cache hit rate as percentage.
- `reset() -> None`: Reset statistics.

### CachePolicy
 Base class for cache eviction policies.

**Methods**:
- `should_evict(entries: Dict[str, CacheEntry]) -> List[str]`: Determine which entries should be evicted.

### LRUPolicy
 Least Recently Used eviction policy.

**Methods**:
- `should_evict(entries: Dict[str, CacheEntry]) -> List[str]`: Evict least recently used entries.

### LFUPolicy
 Least Frequently Used eviction policy.

**Methods**:
- `should_evict(entries: Dict[str, CacheEntry]) -> List[str]`: Evict least frequently used entries.

### TTLPolicy
 Time To Live eviction policy.

**Methods**:
- `should_evict(entries: Dict[str, CacheEntry]) -> List[str]`: Evict expired entries.

### AdaptivePolicy
 Adaptive eviction policy that combines multiple strategies.

**Methods**:
- `should_evict(entries: Dict[str, CacheEntry]) -> List[str]`: Evict entries based on adaptive scoring.

### MemoryCache
 High-performance in-memory cache with multiple eviction policies.

**Methods**:
- `get(key: str, default: Any) -> Any`: Get value from cache.
- `put(key: str, value: Any, ttl_seconds: Optional[int], tags: List[str], metadata: Dict[str, Any]) -> None`: Put value in cache.
- `evict_by_tag(tag: str) -> int`: Evict all entries with a specific tag.
- `clear() -> None`: Clear all cache entries.
- `get_stats() -> CacheStatistics`: Get cache statistics.

### DiskCache
 Persistent disk-based cache for large data.

**Methods**:
- `get(key: str, default: Any) -> Any`: Get value from disk cache.
- `put(key: str, value: Any, ttl_seconds: Optional[int], tags: List[str], metadata: Dict[str, Any]) -> None`: Put value in disk cache.
- `cleanup_expired() -> int`: Clean up expired cache entries.

### RedisCache
 Redis-based distributed cache for multi-node scenarios.

**Methods**:
- `get(key: str, default: Any) -> Any`: Get value from Redis cache.
- `put(key: str, value: Any, ttl_seconds: Optional[int], tags: List[str], metadata: Dict[str, Any]) -> None`: Put value in Redis cache.
- `evict_by_tag(tag: str) -> int`: Evict all entries with a specific tag.
- `get_stats() -> CacheStatistics`: Get cache statistics.

### MultiLevelCache
 Multi-level cache combining memory, disk, and distributed caching.

**Methods**:
- `get(key: str, default: Any) -> Any`: Get value from multi-level cache.
- `put(key: str, value: Any, ttl_seconds: Optional[int], tags: List[str], metadata: Dict[str, Any]) -> None`: Put value in all cache levels.
- `evict(key: str) -> None`: Evict entry from all cache levels.
- `clear() -> None`: Clear all cache levels.

### IntelligentCache
 cache with adaptive strategies and optimization.

**Methods**:
- `get(key: str, default: Any) -> Any`: Get value with caching behavior.
- `put(key: str, value: Any, adaptive_ttl: bool, tags: List[str], metadata: Dict[str, Any]) -> None`: Put value with TTL calculation.
- `warmup(keys: List[str]) -> None`: Warm up cache with frequently accessed keys.
- `get_analytics() -> Dict[str, Any]`: Get cache analytics and optimization recommendations.

### CacheDecorator
 Decorator for automatic caching of function results.

**Methods**:
- `invalidate(func_name: str, *args, **kwargs) -> None`: Invalidate cache entries for a function.

### CloneConfig
 Configuration for repository cloning operations.

### TargetRepository
 Configuration for a target repository to clone.

### TargetUser
 Configuration for repositories from a specific user.

### ConfigLoader
 Configuration loader and validator for GEO-INFER-GIT.

**Methods**:
- `load_yaml_config(filename: str) -> Dict[str, Any]`: Load a YAML configuration file with validation.
- `load_json_config(filename: str) -> Dict[str, Any]`: Load a JSON configuration file with validation.
- `load_clone_config(config_dir: Optional[str]) -> CloneConfig`: Load and merge clone configuration from multiple sources.
- `load_target_repos_config(config_dir: Optional[str]) -> List[TargetRepository]`: Load target repositories configuration.
- `load_target_users_config(config_dir: Optional[str]) -> List[TargetUser]`: Load target users configuration.
- `save_config(config: Dict[str, Any], filename: str) -> None`: Save configuration to file.
- `validate_config(config: Dict[str, Any], schema_name: str) -> List[str]`: Validate configuration against schema.
- `clear_cache() -> None`: Clear the configuration cache.

### ErrorSeverity
 Error severity levels.

### ErrorCategory
 Error categories for classification.

### GeoInferGitError
 Base exception class for GEO-INFER-GIT errors.

### NetworkError
 Network-related errors.

### AuthenticationError
 Authentication-related errors.

### PermissionError
 Permission-related errors.

### GitOperationError
 Git operation errors.

### FilesystemError
 Filesystem-related errors.

### ConfigurationError
 Configuration-related errors.

### APILimitError
 API rate limit errors.

### ValidationError
 Validation-related errors.

### RetryConfig
 Configuration for retry behavior.

### ErrorRecoveryManager
 Manager for handling error recovery strategies.

**Methods**:
- `attempt_recovery(error: GeoInferGitError, context: Dict[str, Any]) -> bool`: Attempt to recover from an error.

### JSONFormatter
 JSON formatter for structured logging.

**Methods**:
- `format(record: logging.LogRecord) -> str`: Format log record as JSON.

### TextFormatter
 text formatter for human-readable logs.

**Methods**:
- `format(record: logging.LogRecord) -> str`: Format log record as human-readable text.

### GeoInferGitLogger
 logger for GEO-INFER-GIT with structured logging support.

**Methods**:
- `log_repo_operation(operation: str, repo_name: str, **kwargs) -> None`: Log a repository operation with context.
- `log_api_call(endpoint: str, method: str, status_code: int, **kwargs) -> None`: Log an API call with details.
- `log_performance(operation: str, duration: float, **kwargs) -> None`: Log performance metrics.
- `log_error_with_context(error: Exception, operation: str, **kwargs) -> None`: Log an error with additional context.

### LogContext
 Context manager for adding temporary context to log records.

### PerformanceTimer
 Timer for measuring operation performance.

### Metric
 A single metric measurement.

### TraceSpan
 A distributed trace span.

**Methods**:
- `duration() -> float`: Get span duration in seconds.
- `finish(status: str) -> None`: Finish the span.
- `log(message: str, **fields) -> None`: Add a log entry to the span.

### AlertRule
 An alerting rule configuration.

### Alert
 An alert notification.

### MetricsCollector
 metrics collection system.

**Methods**:
- `counter(name: str, value: int, tags: Dict[str, str]) -> None`: Record a counter metric.
- `gauge(name: str, value: float, tags: Dict[str, str]) -> None`: Record a gauge metric.
- `histogram(name: str, value: float, tags: Dict[str, str]) -> None`: Record a histogram metric.
- `summary(name: str, value: float, tags: Dict[str, str]) -> None`: Record a summary metric.
- `get_metric_summary(name: str) -> Dict[str, Any]`: Get summary statistics for a metric.
- `export_metrics(format: str) -> str`: Export metrics in specified format.

### Tracer
 Distributed tracing system for tracking operations across services.

**Methods**:
- `start_span(operation_name: str, parent_span_id: Optional[str], tags: Dict[str, str]) -> TraceSpan`: Start a trace span.
- `finish_span(span: TraceSpan) -> None`: Finish a trace span.
- `get_trace(trace_id: str) -> Optional[List[TraceSpan]]`: Get a trace by ID.
- `export_traces(format: str) -> str`: Export traces in specified format.

### HealthChecker
 health checking system.

**Methods**:
- `register_check(name: str, check_func: Callable[[], Dict[str, Any]]) -> None`: Register a health check function.
- `check_all() -> Dict[str, Any]`: Run all registered health checks.
- `get_status() -> str`: Get current overall health status.

### AlertManager
 Alert management and notification system.

**Methods**:
- `add_rule(rule: AlertRule) -> None`: Add an alert rule.
- `remove_rule(rule_name: str) -> None`: Remove an alert rule.
- `add_notification_handler(handler: Callable[[Alert], None]) -> None`: Add a notification handler.
- `evaluate_metrics(metrics_collector: MetricsCollector) -> None`: Evaluate metrics against alert rules.

### ObservabilityManager
 observability management system.

**Methods**:
- `start_span(operation_name: str, tags: Dict[str, str]) -> TraceSpan`: Start a trace span.
- `record_metric(metric_type: str, name: str, value: Union[int, float], tags: Dict[str, str]) -> None`: Record a metric.
- `get_health_status() -> Dict[str, Any]`: Get current health status.
- `get_metrics_summary() -> Dict[str, Any]`: Get metrics summary.
- `export_observability_data(format: str) -> str`: Export all observability data.

### PerformanceMetrics
 Performance metrics for operations.

**Methods**:
- `duration() -> float`: Get operation duration in seconds.
- `memory_used() -> int`: Get memory used during operation.
- `to_dict() -> Dict[str, Any]`: Convert metrics to dictionary.

### PerformanceMonitor
 Monitor performance metrics for operations.

**Methods**:
- `start_operation(operation_name: str) -> PerformanceMetrics`: Start monitoring an operation.
- `end_operation(operation_name: str) -> Optional[PerformanceMetrics]`: End monitoring an operation.
- `get_metrics(operation_name: str) -> Optional[PerformanceMetrics]`: Get metrics for an operation.
- `get_all_metrics() -> Dict[str, PerformanceMetrics]`: Get all current metrics.

### MemoryManager
 Memory management utilities for large-scale operations.

**Methods**:
- `get_memory_usage() -> Dict[str, Any]`: Get current memory usage information.
- `should_trigger_gc() -> bool`: Check if garbage collection should be triggered.
- `trigger_gc(force: bool) -> Dict[str, Any]`: Trigger garbage collection if needed.
- `check_memory_pressure() -> Dict[str, Any]`: Check for memory pressure and return recommendations.

### CacheManager
 Caching utilities for performance optimization.

**Methods**:
- `get(key: str) -> Any`: Get item from cache.
- `put(key: str, value: Any) -> None`: Put item in cache.
- `clear() -> None`: Clear all cached items.
- `get_stats() -> Dict[str, Any]`: Get cache statistics.

### BatchProcessor
 Batch processing utilities for large-scale operations.

**Methods**:
- `calculate_optimal_batch_size(item_size_bytes: int, target_memory_mb: int) -> int`: Calculate optimal batch size based on memory constraints.
- `process_in_batches(items: List[Any], processor: Callable[[List[Any]], Any], batch_size: int, show_progress: bool) -> List[Any]`: Process items in batches with memory management.
- `get_batch_stats() -> Dict[str, Any]`: Get batch processing statistics.

### ResourceManager
 Resource management utilities for system optimization.

**Methods**:
- `get_system_load() -> Dict[str, Any]`: Get current system load information.
- `calculate_optimal_workers(operation_complexity: str) -> int`: Calculate optimal number of workers based on system resources.
- `should_throttle_operations() -> bool`: Check if operations should be throttled due to high system load.

### PerformanceOptimizer
 performance optimization manager.

**Methods**:
- `optimize_operation(operation_name: str, func: Callable, *args, **kwargs)`: Optimize and execute an operation with performance monitoring.
- `get_performance_report() -> Dict[str, Any]`: Get performance report.

### ConfigValidator
 Configuration file validator with validation rules.

**Methods**:
- `add_custom_schema(name: str, schema: Dict[str, Any]) -> None`: Add a custom validation schema.
- `validate_config(config: Dict[str, Any], schema_name: str) -> List[str]`: Validate configuration against a schema.
- `validate_github_url(url: str) -> List[str]`: Validate GitHub repository URL format.
- `validate_directory_path(path: str, must_exist: bool, writable: bool) -> List[str]`: Validate directory path.
- `validate_github_token(token: str) -> List[str]`: Validate GitHub token format.
- `validate_branch_name(branch: str) -> List[str]`: Validate Git branch name.

### RepositoryValidator
 Repository data validator for ensuring data integrity.

**Methods**:
- `validate_repository_data(repo_data: Dict[str, Any]) -> List[str]`: Validate repository data structure.
- `validate_github_url(url: str) -> List[str]`: Validate GitHub URL format.
- `validate_owner_repo_format(owner: str, repo: str) -> List[str]`: Validate owner and repository name format.

### InputValidator
 Input validation utilities for user inputs and command-line arguments.

**Methods**:
- `validate_positive_integer(value: Any, field_name: str) -> List[str]`: Validate that a value is a positive integer.
- `validate_string_length(value: str, field_name: str, min_length: int, max_length: int) -> List[str]`: Validate string length.
- `validate_enum_value(value: Any, field_name: str, allowed_values: List[str]) -> List[str]`: Validate that a value is in a list of allowed values.

### create_optimized_cache
 `create_optimized_cache(memory_size: int, disk_size_gb: float, redis_host: str) -> MultiLevelCache` Create an optimized multi-level cache configuration.

### wrapper
 `wrapper(*args, **kwargs)`

### load_clone_config
 `load_clone_config(config_dir: Optional[str]) -> CloneConfig` Load clone configuration.

### load_target_repos_config
 `load_target_repos_config(config_dir: Optional[str]) -> List[TargetRepository]` Load target repositories configuration.

### load_target_users_config
 `load_target_users_config(config_dir: Optional[str]) -> List[TargetUser]` Load target users configuration.

### classify_error
 `classify_error(error: Exception) -> Tuple[ErrorCategory, ErrorSeverity, bool]` Classify an exception into category, severity, and recoverability.

### retry_on_error
 `retry_on_error(max_attempts: int, base_delay: float, max_delay: float, exponential_base: float, jitter: bool, retryable_errors: Tuple[Type[Exception], ...], logger_instance: logging.Logger)` Decorator for retrying functions on errors.

### handle_error
 `handle_error(error: Exception, operation: str, logger_instance: logging.Logger, reraise: bool) -> Optional[GeoInferGitError]` Handle and classify an error.

### with_error_handling
 `with_error_handling(operation: str, logger_instance: logging.Logger, max_retries: int)` Decorator for error handling.

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### wrapper
 `wrapper(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

### setup_logging
 `setup_logging(config: Optional[Dict[str, Any]]) -> GeoInferGitLogger` Set up logging for GEO-INFER-GIT.

### get_logger
 `get_logger(name: str) -> logging.Logger` Get a logger instance for a specific module.

### log_with_context
 `log_with_context(logger: logging.Logger, level: int, message: str, **context)` Log a message with additional context.

### time_operation
 `time_operation(operation: str, logger: Optional[logging.Logger])` Decorator for timing function execution.

### decorator
 `decorator(func)`

### record_factory
 `record_factory(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

### create_observability_manager
 `create_observability_manager(service_name: str) -> ObservabilityManager` Create an observability manager with default configuration.

### memory_check
 `memory_check()`

### cpu_check
 `cpu_check()`

### disk_check
 `disk_check()`

### performance_optimized
 `performance_optimized(func: Optional[Callable], operation_name: str, memory_threshold_mb: int)` Decorator for performance-optimized function execution.

### adaptive_batch_size
 `adaptive_batch_size(initial_size: int, max_size: int, memory_threshold_mb: int) -> Callable` Create an adaptive batch size function.

### decorator
 `decorator(f: Callable) -> Callable`

### get_batch_size
 `get_batch_size() -> int` Get adaptive batch size based on memory usage.

### wrapper
 `wrapper(*args, **kwargs)`

### validate_config_file
 `validate_config_file(config_path: str) -> Tuple[bool, List[str]]` Validate a configuration file.

### validate_github_credentials
 `validate_github_credentials(token: str, username: str, password: str) -> List[str]` Validate GitHub authentication credentials.

## Capabilities

- **54 classes** for core functionality
- **31 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-GIT/src/geo_infer_git/utils`
- **Type**: Directory Node
