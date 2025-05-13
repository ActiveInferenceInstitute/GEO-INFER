"""
GEO-INFER-OPS: Operations and infrastructure management for GEO-INFER framework.

This module provides the core infrastructure for the GEO-INFER framework, ensuring
reliable, scalable, and maintainable operations across all components.
"""

__version__ = "0.1.0"

from geo_infer_ops.core.logging import setup_logging
from geo_infer_ops.core.monitoring import setup_monitoring
from geo_infer_ops.core.config import load_config
from geo_infer_ops.core.testing import setup_testing

__all__ = [
    "setup_logging",
    "setup_monitoring",
    "load_config",
    "setup_testing",
] 