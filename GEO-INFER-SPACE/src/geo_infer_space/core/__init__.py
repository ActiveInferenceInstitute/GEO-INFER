"""
Generic spatial methods core layer for GEO-INFER-SPACE.

This module provides generic spatial operations that can dispatch to
different backends (H3, SRAI, etc.) based on configuration.
"""

__version__ = "1.0.0"

from .dispatcher import SpatialBackendDispatcher, get_backend_dispatcher
from .spatial_indexing import SpatialIndexingInterface
from .geometric_operations import GeometricOperationsInterface
from .analytics import SpatialAnalyticsInterface

__all__ = [
    'SpatialBackendDispatcher',
    'get_backend_dispatcher',
    'SpatialIndexingInterface',
    'GeometricOperationsInterface',
    'SpatialAnalyticsInterface'
]
