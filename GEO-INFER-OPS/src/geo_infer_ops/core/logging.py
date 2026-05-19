"""Logging configuration module."""

import logging
from typing import Optional

import structlog


def configure_stdlib_logging(
    log_level: str = "INFO", log_file: Optional[str] = None
) -> None:
    """Configure standard library logging.

    Args:
        log_level: Logging level
        log_file: Optional log file path
    """
    level = getattr(logging, log_level.upper())
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    logging.getLogger().setLevel(level)
    logging.getLogger("test").setLevel(level)

    if log_file:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(handler)


def setup_logging(
    log_level: str = "INFO", json_format: bool = True, log_file: Optional[str] = None
) -> None:
    """Set up structured logging.

    Args:
        log_level: Logging level
        json_format: Whether to use JSON format
        log_file: Optional log file path
    """
    # Configure standard library logging first
    configure_stdlib_logging(log_level, log_file)

    # Configure structlog
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        (
            structlog.processors.JSONRenderer()
            if json_format
            else structlog.dev.ConsoleRenderer()
        ),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name

    Returns:
        Structured logger instance
    """
    logger = structlog.get_logger(name)
    bound_logger = logger.bind() if hasattr(logger, "bind") else logger
    if not isinstance(bound_logger, structlog.stdlib.BoundLogger):
        setup_logging()
        logger = structlog.get_logger(name)
        bound_logger = logger.bind() if hasattr(logger, "bind") else logger
    return bound_logger
