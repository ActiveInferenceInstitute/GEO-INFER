"""
Logging utilities for GEO-INFER-OPS.

This module provides structured logging capabilities with configurable outputs,
log levels, and formatting options suitable for both development and production
environments.
"""

import sys
import logging
import structlog
from typing import Optional, Dict, Any

# Define log levels according to GEO-INFER-OPS configuration
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

def configure_logging(
    log_level: str = "INFO",
    json_format: bool = False,
    log_file: Optional[str] = None,
) -> None:
    """
    Configure the logging system for GEO-INFER-OPS.
    
    Args:
        log_level: The minimum log level to capture (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to output logs as JSON (useful for production)
        log_file: Path to a file for writing logs (None means stdout only)
    """
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    # Configure structlog processors
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
    )

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Name of the logger, typically the module name
        
    Returns:
        A structured logger instance
    """
    return structlog.get_logger(name)

class LoggingContext:
    """
    Context manager for temporarily adding context to log entries.
    
    Example:
        with LoggingContext(request_id="123", user="admin"):
            logger.info("Processing request")
    """
    
    def __init__(self, **kwargs: Any) -> None:
        self.temp_context = kwargs
        self.old_context: Dict[str, Any] = {}
    
    def __enter__(self) -> "LoggingContext":
        for key, value in self.temp_context.items():
            self.old_context[key] = structlog.contextvars.get_contextvars().get(key)
            structlog.contextvars.bind_contextvars(**{key: value})
        return self
    
    def __exit__(self, *args: Any) -> None:
        for key, value in self.old_context.items():
            if value is None:
                structlog.contextvars.unbind_contextvars(key)
            else:
                structlog.contextvars.bind_contextvars(**{key: value}) 