"""
GEO-INFER-BIO: A bioinformatics module for the GEO-INFER framework.
"""

try:
    from .core.sequence_analysis import SequenceAnalyzer
except ImportError:
    SequenceAnalyzer = None

try:
    from .core.network_analysis import NetworkAnalyzer
except ImportError:
    NetworkAnalyzer = None

try:
    from .core.spatial_mapping import SpatialMapper
except ImportError:
    SpatialMapper = None

try:
    from .models.biological_networks import BiologicalNetwork
except ImportError:
    BiologicalNetwork = None

try:
    from .models.population_dynamics import PopulationDynamics
except ImportError:
    PopulationDynamics = None

try:
    from .models.metabolic_pathways import MetabolicPathway
except ImportError:
    MetabolicPathway = None

try:
    from .utils.data_processing import DataProcessor
except ImportError:
    DataProcessor = None

try:
    from .utils.visualization import BioVisualizer
except ImportError:
    BioVisualizer = None

try:
    from .utils.validation import DataValidator
except ImportError:
    DataValidator = None

try:
    from .api.rest_api import BioAPI
except ImportError:
    BioAPI = None

try:
    from .api.graphql_api import BioGraphQL
except (ImportError, TypeError):
    BioGraphQL = None

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
