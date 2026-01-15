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
    polygon_to_cells
)

from .core.geometric_operations import GeometricOperationsInterface
from .core.analytics import SpatialAnalyticsInterface
from .core.dispatcher import get_backend_dispatcher, configure_backends

# Provide backward-compatible names using the unified spatial interface
# These are REAL method wrappers, not mock implementations
def cell_to_latlng_boundary(cell: str):
    """Get cell boundary. Wraps SpatialIndexingInterface.get_cell_boundary."""
    return SpatialIndexingInterface().get_cell_boundary(cell)

def geo_to_cells(polygon, resolution: int):
    """Convert polygon to cells. Wraps SpatialIndexingInterface.polygon_to_cells."""
    return SpatialIndexingInterface().polygon_to_cells(polygon, resolution)

def grid_disk(cell: str, k: int = 1):
    """Get cells within k rings. Wraps SpatialIndexingInterface.get_cell_neighbors."""
    return SpatialIndexingInterface().get_cell_neighbors(cell, k)

def grid_distance(cell1: str, cell2: str):
    """Get grid distance between cells. Wraps SpatialIndexingInterface.get_cell_distance."""
    return SpatialIndexingInterface().get_cell_distance(cell1, cell2)

def compact_cells(cells):
    """Compact cells. Wraps SpatialIndexingInterface.compact_cells."""
    return SpatialIndexingInterface().compact_cells(cells)

def uncompact_cells(cells, resolution: int):
    """Uncompact cells. Wraps SpatialIndexingInterface.uncompact_cells."""
    return SpatialIndexingInterface().uncompact_cells(cells, resolution)


# Import additional components with error handling
try:
    from .place_analyzer import PlaceAnalyzer
except ImportError:
    PlaceAnalyzer = None

try:
    from .spatial_utils import SpatialUtils
except ImportError:
    SpatialUtils = None

# OSC Geo functionality has been removed in favor of UnifiedH3Backend

# Make core functionality easily accessible
__all__ = [
    # Generic spatial interfaces
    'SpatialIndexingInterface',
    'GeometricOperationsInterface',
    'SpatialAnalyticsInterface',
    'get_backend_dispatcher',
    'configure_backends',

    # Convenience functions
    'latlng_to_cell',
    'cell_to_latlng',
    'polygon_to_cells',

    # Backward-compatible H3 utilities (real implementations)
    'cell_to_latlng_boundary',
    'geo_to_cells',
    'grid_disk',
    'grid_distance',
    'compact_cells',
    'uncompact_cells',

    # Optional components
    'PlaceAnalyzer',
    'SpatialUtils',
]