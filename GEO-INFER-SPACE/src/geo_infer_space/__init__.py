"""
GEO-INFER-SPACE - Advanced geospatial methods for the GEO-INFER framework.

This module provides powerful spatial indexing, analytics, and integration
with external geospatial tools and libraries.
"""

__version__ = "0.1.0"

# Import public modules and functions
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

# Import additional components
from .place_analyzer import PlaceAnalyzer
from .spatial_utils import SpatialUtils 