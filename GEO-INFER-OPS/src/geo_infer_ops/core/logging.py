"""Passive logging helpers for GEO-INFER-OPS.

Library modules must not mutate global logging state (no root-level
configuration, no handlers, no ``setLevel``). Use :func:`get_logger` to obtain
a structured logger bound to ``__name__``; application and CLI entrypoints
configure the process once via
``geo_infer_ops.utils.shared_logging.configure_logging``.
"""

from typing import cast

import structlog


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    This function is passive: it never configures handlers, formats, or
    levels on the root logger. Call ``shared_logging.configure_logging``
    from your CLI entrypoint before using it in production.

    Args:
        name: Logger name, typically ``__name__``.

    Returns:
        Structured logger instance.
    """
    logger = structlog.get_logger(name)
    bound_logger = logger.bind() if hasattr(logger, "bind") else logger
    return cast(structlog.stdlib.BoundLogger, bound_logger)
