# utils
 ## Overview
 This directory contains utils components. It includes 4 Python modules. ## Components
 ### confi
g
.py Configuration utilities for GEO-INFER-OPS. **Functions**: `find_config_file`, `load_config` ### error_handlin
g
.py Standardized error handling utilities for GEO-INFER modules. **Classes**: `ErrorSeverity`, `ErrorCategory`, `GeoInferError`, `NetworkError`, `AuthenticationError`, `PermissionError`, `FilesystemError`, `ConfigurationError`, `ValidationError`, `ProcessingError`, `DataError`, `RetryConfig` **Functions**: `classify_error`, `handle_error`, `retry_on_error`, `with_error_handling`, `decorator`, `decorator`, `wrapper`, `wrapper` ### logge
r
.py Logging utilities for GEO-INFER-OPS. **Classes**: `LoggingContext` **Functions**: `configure_logging`, `get_logger` ### shared_loggin
g
.py Shared logging configuration for GEO-INFER modules. **Classes**: `LoggingContext` **Functions**: `configure_logging`, `get_logger`, `setup_module_logging`, `_initialize_default_logging` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 