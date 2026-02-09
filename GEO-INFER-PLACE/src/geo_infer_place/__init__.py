"""
GEO-INFER-PLACE: Place-Based Geospatial Analysis Framework

Comprehensive place-based analysis for specific geographic locations,
integrating multiple GEO-INFER modules (SPACE, DATA, TIME) to create
deep, location-specific insights.

Key Features:
- Location-specific data integration and analysis
- Multi-domain analysis (forest, coastal, fire, seismic hazard)
- Real-time data from USGS, NOAA, CAL FIRE with retry + caching
- GEO-INFER-DATA quality management and provenance tracking
- GEO-INFER-TIME temporal trend detection and forecasting
- Interactive H3 visualization and dashboard generation

Supported Locations:
- Del Norte County, California (forest health, coastal resilience, fire risk, seismic hazard)
- Cascadia Bioregion (agricultural land analysis, subduction zone seismicity)

Quick Start::

    from geo_infer_place import PlaceInterface

    pi = PlaceInterface("del_norte")
    results = pi.run_full_analysis()
    print(pi.status())
"""

from typing import Dict, List, Optional, Any
import logging

# Version information
__version__ = "1.1.0"
__author__ = "GEO-INFER Development Team"
__email__ = "geo-infer@activeinference.institute"

# Configure logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

# --- GEO-INFER-SPACE Core Imports (optional) ---
try:
    from geo_infer_space import PlaceAnalyzer
    from geo_infer_space.core.data_integrator import DataIntegrator
    from geo_infer_space.utils.config_loader import LocationConfigLoader
    _HAS_SPACE = True
except ImportError:
    PlaceAnalyzer = None  # type: ignore[misc,assignment]
    DataIntegrator = None  # type: ignore[misc,assignment]
    LocationConfigLoader = None  # type: ignore[misc,assignment]
    _HAS_SPACE = False
    logging.getLogger(__name__).info(
        "geo_infer_space not installed; PlaceAnalyzer/DataIntegrator unavailable"
    )

# --- Local Core Imports ---
from .core.visualization_engine import InteractiveVisualizationEngine
from .core import CascadianAgriculturalH3Backend, BaseAnalysisModule

# --- Unified Interface (new) ---
from .core.place_interface import PlaceInterface

# --- Module Bridge (new - GEO-INFER-DATA / GEO-INFER-TIME integration) ---
from .core.module_bridge import PlaceDataManager, PlaceTemporalAnalyzer

# --- Caching infrastructure (new) ---
from .utils.caching import CachedAPIWrapper

# --- Location-specific Imports ---
from .locations.del_norte_county.forest_health_monitor import ForestHealthMonitor
from .locations.del_norte_county.coastal_resilience_analyzer import CoastalResilienceAnalyzer
from .locations.del_norte_county.fire_risk_assessor import FireRiskAssessor
from .locations.del_norte_county.seismic_hazard_analyzer import SeismicHazardAnalyzer

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
    USGSEarthquakeClient,
    CDECClient,
)

# Export public API
__all__ = [
    # Unified interface (primary entry point)
    'PlaceInterface',

    # Module bridges
    'PlaceDataManager',
    'PlaceTemporalAnalyzer',

    # Core components (from SPACE, may be None if not installed)
    'PlaceAnalyzer',
    'DataIntegrator',
    'LocationConfigLoader',

    # Core components (local)
    'InteractiveVisualizationEngine',
    'CascadianAgriculturalH3Backend',
    'BaseAnalysisModule',

    # Infrastructure
    'CachedAPIWrapper',

    # Del Norte County analyzers
    'ForestHealthMonitor',
    'CoastalResilienceAnalyzer',
    'FireRiskAssessor',
    'SeismicHazardAnalyzer',

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
    'USGSEarthquakeClient',
    'CDECClient',
]


def get_supported_locations() -> List[str]:
    """Get list of supported analysis locations."""
    return ['del_norte_county', 'cascadia']


def create_analyzer(location_code: str, config_path: Optional[str] = None) -> "PlaceAnalyzer":
    """Create a PlaceAnalyzer instance for a specific location.

    Args:
        location_code: Code for the location to analyze.
        config_path: Optional path to custom configuration file.

    Returns:
        Configured PlaceAnalyzer instance.

    Raises:
        ValueError: If location_code is not supported.
        ImportError: If geo_infer_space is not installed.
    """
    if not _HAS_SPACE:
        raise ImportError(
            "geo_infer_space is required for create_analyzer. "
            "Install it with: pip install geo-infer-space"
        )
    if location_code not in get_supported_locations():
        raise ValueError(f"Location '{location_code}' not supported. "
                        f"Available locations: {get_supported_locations()}")

    return PlaceAnalyzer(location_code=location_code, config_path=config_path)


def create_place_interface(
    location: str = "del_norte",
    output_dir: Optional[str] = None,
) -> PlaceInterface:
    """Convenience factory for PlaceInterface.

    Args:
        location: Location key (``"del_norte"`` or ``"cascadia"``).
        output_dir: Optional output directory path.

    Returns:
        Configured PlaceInterface instance.
    """
    return PlaceInterface(location=location, output_dir=output_dir)
