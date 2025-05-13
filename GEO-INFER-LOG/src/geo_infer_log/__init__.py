"""
GEO-INFER-LOG: Logistics and supply chain optimization with geospatial intelligence.

This module provides tools and frameworks for:
- Route optimization and fleet management
- Supply chain resilience modeling
- Last-mile delivery solutions
- Multimodal transportation planning
"""

__version__ = "0.1.0"

# Import core submodules
from geo_infer_log import core
from geo_infer_log import api
from geo_infer_log import models
from geo_infer_log import utils

# Export public API
__all__ = ["core", "api", "models", "utils"] 