# utils
 ## Overview
 This directory contains utils components. It includes 7 Python modules. ## Components
 ### advanced_cach
e
.py caching strategies for GEO-INFER-GIT. **Classes**: `CacheEntry`, `CacheStatistics`, `CachePolicy`, `LRUPolicy`, `LFUPolicy`, `TTLPolicy`, `AdaptivePolicy`, `MemoryCache`, `DiskCache`, `RedisCache`, `MultiLevelCache`, `IntelligentCache`, `CacheDecorator` **Functions**: `create_optimized_cache`, `wrapper` ### config_loade
r
.py Configuration loader utilities for GEO-INFER-GIT. **Classes**: `CloneConfig`, `TargetRepository`, `TargetUser`, `ConfigLoader` **Functions**: `load_clone_config`, `load_target_repos_config`, `load_target_users_config` ### error_handle
r
.py Error handling utilities for GEO-INFER-GIT. **Classes**: `ErrorSeverity`, `ErrorCategory`, `GeoInferGitError`, `NetworkError`, `AuthenticationError`, `PermissionError`, `GitOperationError`, `FilesystemError`, `ConfigurationError`, `APILimitError`, `ValidationError`, `RetryConfig`, `ErrorRecoveryManager` **Functions**: `classify_error`, `retry_on_error`, `handle_error`, `with_error_handling`, `decorator`, `decorator`, `wrapper`, `wrapper` ### logging_util
s
.py Logging utilities for GEO-INFER-GIT. **Classes**: `JSONFormatter`, `TextFormatter`, `GeoInferGitLogger`, `LogContext`, `PerformanceTimer` **Functions**: `setup_logging`, `get_logger`, `log_with_context`, `time_operation`, `decorator`, `record_factory`, `wrapper` ### observabilit
y
.py monitoring and observability for GEO-INFER-GIT. **Classes**: `Metric`, `TraceSpan`, `AlertRule`, `Alert`, `MetricsCollector`, `Tracer`, `HealthChecker`, `AlertManager`, `ObservabilityManager` **Functions**: `create_observability_manager`, `memory_check`, `cpu_check`, `disk_check` ### performanc
e
.py Performance optimization utilities for GEO-INFER-GIT. **Classes**: `PerformanceMetrics`, `PerformanceMonitor`, `MemoryManager`, `CacheManager`, `BatchProcessor`, `ResourceManager`, `PerformanceOptimizer` **Functions**: `performance_optimized`, `adaptive_batch_size`, `decorator`, `get_batch_size`, `wrapper` ### validatio
n
.py Validation utilities for GEO-INFER-GIT. **Classes**: `ConfigValidator`, `RepositoryValidator`, `InputValidator` **Functions**: `validate_config_file`, `validate_github_credentials` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 