"""
GEO-INFER-RISK: Geospatial Risk Analysis and Catastrophe Modeling Framework

A comprehensive framework for modeling, analyzing, and visualizing geospatial risk 
across multiple hazards, vulnerabilities, and exposure types.
"""

__version__ = "0.1.0"
__author__ = "GEO-INFER Team"
__license__ = "MIT"

# Import core components for easier access
from geo_infer_risk.core import (
    RiskEngine, 
    RiskModel,
    HazardModel,
    VulnerabilityModel,
    ExposureModel
)

# Import specialized risk models
from geo_infer_risk.models import (
    FloodModel,
    EarthquakeModel,
    HurricaneModel,
    WildfireModel,
    DroughtModel,
    MultiHazardModel
)

# Import utility functions
from geo_infer_risk.utils import (
    config_loader,
    risk_metrics,
    spatial_utils,
    validation
)

# Import API components
from geo_infer_risk.api import (
    RiskAPI,
    ModelRegistry,
    ResultsFormatter
)

# Define module level constants
DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_RETURN_PERIODS = [10, 25, 50, 100, 250, 500, 1000]

# Convenience function to create a new risk analysis
def create_risk_analysis(config_path=None, **kwargs):
    """
    Create a new risk analysis engine with the specified configuration.
    
    Args:
        config_path (str, optional): Path to configuration file. If not provided,
                                     default configuration will be used.
        **kwargs: Additional configuration parameters that override file settings.
        
    Returns:
        RiskEngine: Configured risk analysis engine instance.
    """
    from geo_infer_risk.utils.config_loader import load_config
    
    # Load configuration (from file if provided, otherwise use defaults)
    if config_path:
        config = load_config(config_path)
    else:
        config = {}
    
    # Override with any kwargs provided
    for key, value in kwargs.items():
        config[key] = value
        
    # Initialize and return the risk engine
    return RiskEngine(config) 