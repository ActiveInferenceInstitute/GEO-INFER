"""
GEO-INFER-SPACE - Advanced geospatial methods for the GEO-INFER framework.

This module provides powerful spatial indexing, analytics, and integration
with external geospatial tools and libraries through a unified, backend-agnostic API.
"""

from typing import Any

__version__ = "0.2.0"

# Import the generic spatial interfaces
from .core.spatial_indexing import (
    SpatialIndexingInterface,
    latlng_to_cell,
    cell_to_latlng,
    polygon_to_cells,
)

from .core.geometric_operations import GeometricOperationsInterface
from .core.analytics import SpatialAnalyticsInterface
from .core.dispatcher import get_backend_dispatcher, configure_backends
from .core.interfaces import UnsupportedSpatialOperationError

# Import additional components with error handling
PlaceAnalyzer: Any
try:
    from .place_analyzer import PlaceAnalyzer as _PlaceAnalyzer
    PlaceAnalyzer = _PlaceAnalyzer
except ImportError:
    PlaceAnalyzer = None

SpatialUtils: Any
try:
    from .spatial_utils import SpatialUtils as _SpatialUtils
    SpatialUtils = _SpatialUtils
except ImportError:
    SpatialUtils = None

# Import the GIS submodule facade
GISManager: Any
try:
    from .gis import GISManager as _GISManager
    GISManager = _GISManager
except ImportError:
    GISManager = None

# Make core functionality easily accessible
__all__ = [
    # Generic spatial interfaces
    "SpatialIndexingInterface",
    "GeometricOperationsInterface",
    "SpatialAnalyticsInterface",
    "get_backend_dispatcher",
    "configure_backends",
    "UnsupportedSpatialOperationError",
    # Convenience functions
    "latlng_to_cell",
    "cell_to_latlng",
    "polygon_to_cells",
    # Optional components
    "PlaceAnalyzer",
    "SpatialUtils",
    "GISManager",
]
