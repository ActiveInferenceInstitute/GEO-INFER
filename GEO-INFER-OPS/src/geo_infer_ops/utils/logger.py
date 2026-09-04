"""
Passive logging utilities for GEO-INFER-OPS.

This module provides a structured logger accessor and a context manager for
temporary log context. It never mutates global logging state (no root-level
configuration, no handlers, no ``setLevel``); application and CLI
entrypoints configure the process once via
``geo_infer_ops.utils.shared_logging.configure_logging``.
"""

import structlog
from typing import Any, Dict, cast


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    This function is passive: it never configures handlers, formats, or
    levels on the root logger.

    Args:
        name: Name of the logger, typically the module name

    Returns:
        A structured logger instance
    """
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))

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
