"""
Utility functions for GEO-INFER-OPS.

This submodule contains helper functions and utilities that are used
across the GEO-INFER-OPS module for common tasks.
"""

# Single documented app-level logging entry: shared_logging.configure_logging
# (for CLI entrypoints). Library modules use core.logging.get_logger only.
from .shared_logging import (
    configure_logging,
    get_logger,
    LoggingContext,
    setup_module_logging,
    LOG_LEVELS,
)
from .config import load_config, find_config_file

__all__ = [
    # Logging (app-level entry + passive accessors, single implementation
    # in shared_logging)
    "configure_logging",
    "get_logger",
    "LoggingContext",
    "setup_module_logging",
    "LOG_LEVELS",
    # Configuration
    "load_config",
    "find_config_file",
]
