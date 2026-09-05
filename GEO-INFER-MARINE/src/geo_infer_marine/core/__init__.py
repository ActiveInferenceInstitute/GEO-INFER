"""Core marine and oceanographic analysis modules."""

from .oceanographic_data import OceanographicDataProcessor
from .coastal_analysis import CoastalAnalyzer
from .marine_ecosystems import (
    MarineEcosystemModeler,
    MarineHabitatType,
    SpeciesData,
)
from .sea_level import SeaLevelAnalyzer
from .marine_spatial_planning import MarineSpatialPlanner
from .ocean_currents import OceanCurrentModeler
from .water_quality import MarineWaterQuality
from .coral_reef import CoralReefAssessor

__all__ = [
    "OceanographicDataProcessor",
    "CoastalAnalyzer",
    "MarineEcosystemModeler",
    "MarineHabitatType",
    "SpeciesData",
    "SeaLevelAnalyzer",
    "MarineSpatialPlanner",
    "OceanCurrentModeler",
    "MarineWaterQuality",
    "CoralReefAssessor",
]
