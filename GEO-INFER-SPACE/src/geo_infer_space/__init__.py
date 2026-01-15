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

# OSC geo imports with optional dependency handling
try:
    from .osc_geo import (
        setup_osc_geo,
        clone_osc_repos,
        create_h3_grid_manager,
        create_h3_data_loader,
        load_data_to_h3_grid,
        H3GridManager,
        H3DataLoader,
        check_integration_status,
        run_diagnostics,
        detailed_report,
        IntegrationStatus,
        RepoStatus,
    )
    OSC_GEO_AVAILABLE = True
except ImportError:
    # OSC geo functionality not available
    OSC_GEO_AVAILABLE = False
    setup_osc_geo = None
    clone_osc_repos = None
    create_h3_grid_manager = None
    create_h3_data_loader = None
    load_data_to_h3_grid = None
    H3GridManager = None
    H3DataLoader = None
    check_integration_status = None
    run_diagnostics = None
    detailed_report = None
    IntegrationStatus = None
    RepoStatus = None

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

    # OSC geo (if available)
    'setup_osc_geo',
    'clone_osc_repos',
    'create_h3_grid_manager',
    'create_h3_data_loader',
    'load_data_to_h3_grid',
    'H3GridManager',
    'H3DataLoader',
    'check_integration_status',
    'run_diagnostics',
    'detailed_report',
    'IntegrationStatus',
    'RepoStatus',
    'OSC_GEO_AVAILABLE'
] 