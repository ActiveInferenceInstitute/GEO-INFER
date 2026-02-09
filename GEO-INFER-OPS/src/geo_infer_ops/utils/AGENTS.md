# Agent
: utils

## Scope
 This directory contains utils components for the module. It provides 14 classes and 16 functions.

## Classes
 and Functions

### ErrorSeverity
 Error severity levels.

### ErrorCategory
 Error categories for classification.

### GeoInferError
 Base exception class for GEO-INFER errors.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert exception to dictionary for JSON serialization.

### NetworkError
 Network-related errors.

### AuthenticationError
 Authentication-related errors.

### PermissionError
 Permission-related errors.

### FilesystemError
 Filesystem-related errors.

### ConfigurationError
 Configuration-related errors.

### ValidationError
 Validation-related errors.

### ProcessingError
 Processing-related errors.

### DataError
 Data-related errors.

### RetryConfig
 Configuration for retry behavior.

### LoggingContext
 Context manager for temporarily adding context to log entries.

### LoggingContext
 Context manager for temporarily adding context to log entries.

### find_config_file
 `find_config_file(config_path: Optional[str]) -> str` Find the configuration file to use.

### load_config
 `load_config(config_path: Optional[str]) -> Dict[str, Any]` Load configuration from a YAML file.

### classify_error
 `classify_error(error: Exception) -> Tuple[ErrorCategory, ErrorSeverity, bool]` Classify an exception into category, severity, and recoverability.

### handle_error
 `handle_error(error: Exception, operation: Optional[str], logger_instance: Optional[logging.Logger], reraise: bool) -> Optional[GeoInferError]` Handle and classify an error.

### retry_on_error
 `retry_on_error(max_attempts: int, base_delay: float, max_delay: float, exponential_base: float, jitter: bool, retryable_errors: Optional[Tuple[Type[Exception], ...]], logger_instance: Optional[logging.Logger])` Decorator for retrying operations on error.

### with_error_handling
 `with_error_handling(operation: Optional[str], logger_instance: Optional[logging.Logger], max_retries: int)` Decorator for error handling.

### decorator
 `decorator(func: Callable) -> Callable`

### decorator
 `decorator(func: Callable) -> Callable`

### wrapper
 `wrapper(*args, **kwargs)`

### wrapper
 `wrapper(*args, **kwargs)`

### configure_logging
 `configure_logging(log_level: str, json_format: bool, log_file: Optional[str]) -> None` Configure the logging system for GEO-INFER-OPS.

### get_logger
 `get_logger(name: str) -> structlog.stdlib.BoundLogger` Get a configured logger instance.

### configure_logging
 `configure_logging(log_level: str, json_format: bool, log_file: Optional[str], module_name: Optional[str], enable_console: bool) -> None` Configure the logging system for GEO-INFER modules.

### get_logger
 `get_logger(name: Optional[str]) -> structlog.stdlib.BoundLogger` Get a configured logger instance.

### setup_module_logging
 `setup_module_logging(module_name: str, log_level: Optional[str], log_file: Optional[str]) -> structlog.stdlib.BoundLogger` Convenience function to set up logging for a GEO-INFER module.

## Capabilities

- **14 classes** for core functionality
- **16 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-OPS/src/geo_infer_ops/utils`
- **Type**: Directory Node
