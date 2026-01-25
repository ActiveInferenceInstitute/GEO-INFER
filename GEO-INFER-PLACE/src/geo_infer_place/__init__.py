"""
GEO-INFER-PLACE: Place-Based Geospatial Analysis Framework

This module provides comprehensive place-based analysis capabilities for specific
geographic locations, integrating multiple GEO-INFER modules to create deep,
location-specific insights.

Key Features:
- Location-specific data integration and analysis
- Multi-domain analysis (forest health, coastal resilience, fire risk, community development)
- Real-time data access from government and research APIs
- Interactive visualization and dashboard generation
- Community engagement and stakeholder integration

Core Components:
- Place Analyzer: Main orchestration engine
- Location Modules: Specific implementations for different places
- Data Integrators: Real-time data access and processing
- Visualization Engine: Interactive dashboard and map generation
- Community Interface: Stakeholder engagement tools

Supported Locations:
- Del Norte County, California (forest health, coastal resilience, fire risk)
- Cascadia Bioregion (agricultural land analysis)
- Additional locations can be added following the same framework

Example Usage:
    >>> from geo_infer_place import CascadianAgriculturalH3Backend
    >>> backend = CascadianAgriculturalH3Backend(h3_resolution=8, target_counties=["CA:Del Norte"])
    >>> backend.generate_interactive_map()
"""

from typing import Dict, List, Optional, Any, Tuple
import logging

# Version information
__version__ = "1.0.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# --- GEO-INFER-SPACE Core Imports ---
from geo_infer_space import PlaceAnalyzer
from geo_infer_space.core.data_integrator import DataIntegrator
from geo_infer_space.utils.config_loader import LocationConfigLoader

# --- Local Core Imports ---
from .core.visualization_engine import InteractiveVisualizationEngine
from .core import CascadianAgriculturalH3Backend, BaseAnalysisModule

# --- Location-specific Imports ---
from .locations.del_norte_county.forest_health_monitor import ForestHealthMonitor
from .locations.del_norte_county.coastal_resilience_analyzer import CoastalResilienceAnalyzer
from .locations.del_norte_county.fire_risk_assessor import FireRiskAssessor

# --- Utilities ---
from .utils.data_sources import CaliforniaDataSources
from .utils.h3_operations import (
    latlng_to_cell,
    cell_to_latlng,
    polygon_to_cells,
    grid_disk,
    is_valid_cell,
)

# --- API Clients ---
from .core.api_clients import (
    CaliforniaAPIManager,
    NOAAClient,
    CALFIREClient,
    USGSClient,
    CDECClient,
)

# Export public API
__all__ = [
    # Core components
    'PlaceAnalyzer',
    'DataIntegrator',
    'InteractiveVisualizationEngine',
    'CascadianAgriculturalH3Backend',
    'BaseAnalysisModule',
    'LocationConfigLoader',
    
    # Del Norte County specific
    'ForestHealthMonitor',
    'CoastalResilienceAnalyzer',
    'FireRiskAssessor',
    
    # Utilities
    'CaliforniaDataSources',
    'latlng_to_cell',
    'cell_to_latlng',
    'polygon_to_cells',
    'grid_disk',
    'is_valid_cell',
    
    # API clients
    'CaliforniaAPIManager',
    'NOAAClient',
    'CALFIREClient',
    'USGSClient',
    'CDECClient',
]


def get_supported_locations() -> List[str]:
    """
    Get list of supported analysis locations.
    
    Returns:
        List of location codes that can be analyzed
    """
    return [
        'del_norte_county',
        'cascadia',
    ]


def create_analyzer(location_code: str, config_path: Optional[str] = None) -> PlaceAnalyzer:
    """
    Create a PlaceAnalyzer instance for a specific location.
    
    Args:
        location_code: Code for the location to analyze
        config_path: Optional path to custom configuration file
        
    Returns:
        Configured PlaceAnalyzer instance
        
    Raises:
        ValueError: If location_code is not supported
    """
    if location_code not in get_supported_locations():
        raise ValueError(f"Location '{location_code}' not supported. "
                        f"Available locations: {get_supported_locations()}")
    
    return PlaceAnalyzer(location_code=location_code, config_path=config_path)