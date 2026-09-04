"""Tests for the passive logging contract of GEO-INFER-OPS.

Library modules expose only passive ``get_logger`` accessors; global
logging configuration belongs to the single documented app-level entry
``geo_infer_ops.utils.shared_logging.configure_logging``, called from CLI
entrypoints.
"""

import logging

import structlog

from geo_infer_ops.core.logging import get_logger
from geo_infer_ops.utils.shared_logging import configure_logging


def test_get_logger_is_passive() -> None:
    """get_logger returns a structlog bound logger without configuring root."""
    before = list(logging.root.handlers)
    logger = get_logger("geo_infer_ops.test")
    assert isinstance(logger, structlog.stdlib.BoundLoggerBase)
    assert logging.root.handlers == before



def test_configure_logging_adds_root_handlers() -> None:
    """The documented app-level entry installs a root handler set."""
    previous = list(logging.root.handlers)
    try:
        configure_logging(log_level="DEBUG", json_format=False)
        new_handlers = [h for h in logging.root.handlers if h not in previous]
        assert any(
            isinstance(h, logging.StreamHandler) for h in new_handlers
        ), "configure_logging installed no console handler"
    finally:
        for handler in logging.root.handlers[:]:
            if handler not in previous:
                logging.root.removeHandler(handler)
        logging.root.handlers[:] = previous
        logging.root.setLevel(logging.WARNING)


def test_configure_logging_is_idempotent_on_repeat() -> None:
    """Repeated configuration does not accumulate duplicate handlers."""
    previous = list(logging.root.handlers)
    try:
        configure_logging(log_level="INFO", json_format=False)
        count_first = len(logging.root.handlers)
        configure_logging(log_level="INFO", json_format=False)
        count_second = len(logging.root.handlers)
        assert count_second <= count_first + 1
    finally:
        logging.root.handlers[:] = previous
        logging.root.setLevel(logging.WARNING)


def test_module_loggers_do_not_add_handlers() -> None:
    """Every geo_infer_ops subpackage imports without adding root handlers."""
    import importlib

    modules = [
        "geo_infer_ops",
        "geo_infer_ops.core",
        "geo_infer_ops.core.backup.logging",
        "geo_infer_ops.utils.logger",
        "geo_infer_ops.utils.shared_logging",
    ]
    before = list(logging.root.handlers)
    for module_name in modules:
        importlib.import_module(module_name)
        assert logging.root.handlers == before, (
            f"importing {module_name} mutated the root logger"
        )
