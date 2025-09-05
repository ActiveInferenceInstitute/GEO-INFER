"""
GEO-INFER-SPACE - Advanced geospatial methods for the GEO-INFER framework.

This module provides powerful spatial indexing, analytics, and integration
with external geospatial tools and libraries.
"""

__version__ = "0.1.0"

# Core imports that should always be available
from .utils.h3_utils import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,
    polygon_to_cells,
    geo_to_cells,
    grid_disk,
    grid_distance,
    compact_cells,
    uncompact_cells
)

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
    # H3 utilities
    'latlng_to_cell',
    'cell_to_latlng', 
    'cell_to_latlng_boundary',
    'polygon_to_cells',
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