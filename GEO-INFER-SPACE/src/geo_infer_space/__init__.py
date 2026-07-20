"""
GEO-INFER-SPACE - Advanced geospatial methods for the GEO-INFER framework.

This module provides powerful spatial indexing, analytics, and integration
with external geospatial tools and libraries through a unified, backend-agnostic API.
"""

__version__ = "1.0.0"

# Import the new generic spatial interfaces
from .core.spatial_indexing import (
    SpatialIndexingInterface,
    latlng_to_cell,
    cell_to_latlng,
    polygon_to_cells,
)

from .core.geometric_operations import GeometricOperationsInterface
from .core.analytics import SpatialAnalyticsInterface
from .core.dispatcher import get_backend_dispatcher, configure_backends

# Import additional components with error handling
try:
    from .place_analyzer import PlaceAnalyzer
except ImportError:
    PlaceAnalyzer = None

try:
    from .spatial_utils import SpatialUtils
except ImportError:
    SpatialUtils = None

# Import new GIS Submodule facade
try:
    from .gis import GISManager
except ImportError:
    GISManager = None

# OSC Geo functionality has been removed in favor of UnifiedH3Backend

# Make core functionality easily accessible
__all__ = [
    # Generic spatial interfaces
    "SpatialIndexingInterface",
    "GeometricOperationsInterface",
    "SpatialAnalyticsInterface",
    "get_backend_dispatcher",
    "configure_backends",
    # Convenience functions
    "latlng_to_cell",
    "cell_to_latlng",
    "polygon_to_cells",
    # Optional components
    "PlaceAnalyzer",
    "SpatialUtils",
    "GISManager",
]
