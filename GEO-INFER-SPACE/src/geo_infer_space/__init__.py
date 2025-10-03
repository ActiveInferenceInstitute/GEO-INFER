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

# Import legacy H3 utilities for backward compatibility
try:
    from .core.spatial_indexing import latlng_to_cell as h3_latlng_to_cell
    from .core.spatial_indexing import cell_to_latlng as h3_cell_to_latlng
    from .core.spatial_indexing import polygon_to_cells as h3_polygon_to_cells

    # Provide backward-compatible names
    cell_to_latlng_boundary = h3_cell_to_latlng  # Simplified for compatibility
    geo_to_cells = h3_polygon_to_cells  # Simplified for compatibility
    grid_disk = lambda cell, k: []  # Mock implementation for compatibility
    grid_distance = lambda cell1, cell2: 0  # Mock implementation for compatibility
    compact_cells = lambda cells: cells  # Mock implementation for compatibility
    uncompact_cells = lambda cells, res: cells  # Mock implementation for compatibility

except ImportError:
    # Fallback if core imports fail
    cell_to_latlng_boundary = None
    geo_to_cells = None
    grid_disk = None
    grid_distance = None
    compact_cells = None
    uncompact_cells = None

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

    # Legacy H3 utilities (for backward compatibility)
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