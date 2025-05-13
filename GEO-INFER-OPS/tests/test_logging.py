"""Tests for logging configuration."""
import os
import logging
from unittest.mock import patch, MagicMock

import pytest
import structlog

from geo_infer_ops.core.logging import (
    setup_logging,
    get_logger,
    configure_stdlib_logging,
)

def test_get_logger():
    """Test logger creation."""
    logger = get_logger("test")
    assert isinstance(logger, structlog.stdlib.BoundLogger)

def test_setup_logging_defaults():
    """Test logging setup with default configuration."""
    setup_logging()
    logger = get_logger("test")
    assert isinstance(logger, structlog.stdlib.BoundLogger)

def test_setup_logging_custom_config():
    """Test logging setup with custom configuration."""
    log_file = "test.log"
    setup_logging(
        log_level="DEBUG",
        json_format=True,
        log_file=log_file
    )

    logger = get_logger("test")
    assert isinstance(logger, structlog.stdlib.BoundLogger)

def test_configure_stdlib_logging():
    """Test standard library logging configuration."""
    log_file = "test.log"
    configure_stdlib_logging("DEBUG", log_file)

    logger = logging.getLogger("test")
    assert logger.level == logging.DEBUG

def test_log_levels():
    """Test different log levels."""
    setup_logging(log_level="DEBUG")
    logger = get_logger("test")

    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger.debug("debug message")
        mock_logger.debug.assert_called_once_with("debug message")

def test_log_formatting():
    """Test log message formatting."""
    setup_logging(json_format=False)
    logger = get_logger("test")

    with patch("structlog.get_logger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        logger.info("test message", extra={"key": "value"})
        mock_logger.info.assert_called_once_with(
            "test message",
            extra={"key": "value"}
        )

def test_log_file_rotation():
    """Test log file rotation."""
    log_file = "test.log"
    setup_logging(log_file=log_file)
    
    # Write some logs
    logger = get_logger("test")
    for i in range(1000):
        logger.info(f"Test log {i}")
    
    # Verify file size
    assert os.path.getsize(log_file) > 0
    
    # Cleanup
    os.remove(log_file) 