"""Core climate processing modules."""

from .climate_data import ClimateDataProcessor
from .climate_indices import ClimateIndicesCalculator
from .downscaling import DownscalingMethods
from .projections import ClimateProjections
from .extreme_events import ExtremeEventAnalyzer
from .impact_assessment import ClimateImpactAssessor
from .classification import ClimateClassifier
from .temperature_trends import TemperatureTrendAnalyzer
from .precipitation_analysis import PrecipitationAnalyzer

__all__ = [
    "ClimateDataProcessor",
    "ClimateIndicesCalculator",
    "DownscalingMethods",
    "ClimateProjections",
    "ExtremeEventAnalyzer",
    "ClimateImpactAssessor",
    "ClimateClassifier",
    "TemperatureTrendAnalyzer",
    "PrecipitationAnalyzer",
]
