"""
GEO-INFER-BIO: A bioinformatics module for the GEO-INFER framework.
"""

from .core.sequence_analysis import SequenceAnalyzer
from .core.network_analysis import NetworkAnalyzer
from .core.spatial_mapping import SpatialMapper
from .models.biological_networks import BiologicalNetwork
from .models.population_dynamics import PopulationDynamics
from .models.metabolic_pathways import MetabolicPathway
from .utils.data_processing import DataProcessor
from .utils.visualization import BioVisualizer
from .utils.validation import DataValidator
from .api.rest_api import BioAPI
from .api.graphql_api import BioGraphQL

__version__ = "0.1.0"
__author__ = "GEO-INFER Team"
__email__ = "team@geo-infer.org"

__all__ = [
    "SequenceAnalyzer",
    "NetworkAnalyzer",
    "SpatialMapper",
    "BiologicalNetwork",
    "PopulationDynamics",
    "MetabolicPathway",
    "DataProcessor",
    "BioVisualizer",
    "DataValidator",
    "BioAPI",
    "BioGraphQL",
] 