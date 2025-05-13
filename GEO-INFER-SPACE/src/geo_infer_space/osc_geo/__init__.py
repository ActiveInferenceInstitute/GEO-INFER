"""
OSC-GEO - OS Climate geospatial integration module for GEO-INFER-SPACE.

This module provides integration with OS Climate geospatial tools, focusing on
H3 grid systems and geospatial data loading capabilities.
"""

__version__ = "0.1.0"

from .core.repos import clone_osc_repos
from .core.h3grid import H3GridManager
from .core.loader import H3DataLoader
from .core.status import (
    check_integration_status,
    run_diagnostics,
    detailed_report,
    IntegrationStatus,
    RepoStatus,
)
from .main import (
    setup_osc_geo,
    get_repo_list,
    create_h3_grid_manager,
    create_h3_data_loader,
    load_data_to_h3_grid,
)

__all__ = [
    # Repository management
    "clone_osc_repos",
    
    # Main implementation classes
    "H3GridManager",
    "H3DataLoader",
    
    # High-level API functions
    "setup_osc_geo",
    "get_repo_list",
    "create_h3_grid_manager",
    "create_h3_data_loader",
    "load_data_to_h3_grid",
    
    # Status and diagnostics
    "check_integration_status",
    "run_diagnostics",
    "detailed_report",
    "IntegrationStatus",
    "RepoStatus",
] 