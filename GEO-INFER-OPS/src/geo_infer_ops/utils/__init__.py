"""
Utility functions for GEO-INFER-OPS.

This submodule contains helper functions and utilities that are used
across the GEO-INFER-OPS module for common tasks.
"""

from .logger import get_logger, LoggingContext
# Single documented app-level logging entry: shared_logging.configure_logging
# (for CLI entrypoints). Library modules use get_logger only.
from .shared_logging import (
    configure_logging,
    get_logger as get_shared_logger,
    LoggingContext as SharedLoggingContext,
    setup_module_logging,
    LOG_LEVELS,
)

# Documented alias: cross-module callers historically imported
# ``configure_shared_logging``; it is the same app-level logging entry as
# ``configure_logging``.
configure_shared_logging = configure_logging
from .config import load_config, find_config_file
from .error_handling import (
    ErrorSeverity,
    ErrorCategory,
    GeoInferError,
    NetworkError,
    AuthenticationError,
    PermissionError,
    FilesystemError,
    ConfigurationError,
    ValidationError,
    ProcessingError,
    DataError,
    RetryConfig,
    classify_error,
    handle_error,
    retry_on_error,
    with_error_handling,
)

__all__ = [
    # Logging (module-specific)
    "configure_logging", 
    "get_logger", 
    "LoggingContext",
    # Shared logging (for cross-module use)
    "configure_shared_logging",
    "get_shared_logger",
    "SharedLoggingContext",
    "setup_module_logging",
    "LOG_LEVELS",
    # Configuration
    "load_config",
    "find_config_file",
    # Error handling
    "ErrorSeverity",
    "ErrorCategory",
    "GeoInferError",
    "NetworkError",
    "AuthenticationError",
    "PermissionError",
    "FilesystemError",
    "ConfigurationError",
    "ValidationError",
    "ProcessingError",
    "DataError",
    "RetryConfig",
    "classify_error",
    "handle_error",
    "retry_on_error",
    "with_error_handling",
] 