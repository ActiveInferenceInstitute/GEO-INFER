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
- Additional locations can be added following the same framework

Example Usage:
    >>> from geo_infer_place import PlaceAnalyzer
    >>> analyzer = PlaceAnalyzer('del_norte_county')
    >>> analyzer.run_comprehensive_analysis()
    >>> analyzer.generate_interactive_dashboard()
"""

from typing import Dict, List, Optional, Any, Tuple
import logging

# Version information
__version__ = "1.0.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# Core imports
from .core.place_analyzer import PlaceAnalyzer
# Optional imports for components that may not be available
try:
    from .core.data_integrator import RealDataIntegrator
except ImportError:
    RealDataIntegrator = None
    
from .core.visualization_engine import InteractiveVisualizationEngine

# Location-specific imports with fallbacks
try:
    from .locations.del_norte_county.del_norte_analyzer import DelNorteCountyAnalyzer
except ImportError:
    DelNorteCountyAnalyzer = None
    
from .locations.del_norte_county.forest_health_monitor import ForestHealthMonitor
from .locations.del_norte_county.coastal_resilience_analyzer import CoastalResilienceAnalyzer
from .locations.del_norte_county.fire_risk_assessor import FireRiskAssessor

# Note: CommunityDevelopmentTracker not yet implemented
# from .locations.del_norte_county.community_development_tracker import CommunityDevelopmentTracker

# Configuration and utilities
from .utils.config_loader import LocationConfigLoader
from .utils.data_sources import CaliforniaDataSources

# API clients - using core implementation for consistency
from .core.api_clients import CaliforniaAPIManager, NOAAClient, CALFIREClient, USGSClient, CDECClient

# Export public API (only include modules that are actually available)
__all__ = [
    # Core components
    'PlaceAnalyzer',
    'InteractiveVisualizationEngine',
    
    # Del Norte County specific
    'ForestHealthMonitor',
    'CoastalResilienceAnalyzer', 
    'FireRiskAssessor',
    
    # Utilities
    'LocationConfigLoader',
    'CaliforniaDataSources',
    
    # API clients
    'CaliforniaAPIManager',
    'NOAAClient', 
    'CALFIREClient', 
    'USGSClient',
    'CDECClient',
]

# Add optional components if they exist
if RealDataIntegrator is not None:
    __all__.append('RealDataIntegrator')
if DelNorteCountyAnalyzer is not None:
    __all__.append('DelNorteCountyAnalyzer')
if NOAAClient is not None:
    __all__.extend(['NOAAClient', 'CALFIREClient', 'USGSClient'])

def get_supported_locations() -> List[str]:
    """
    Get list of supported analysis locations.
    
    Returns:
        List of location codes that can be analyzed
    """
    return [
        'del_norte_county',
        # Additional locations can be added here
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