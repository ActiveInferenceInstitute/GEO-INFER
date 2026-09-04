"""
GEO-INFER-BIO: A bioinformatics module for the GEO-INFER framework.
"""

from .core.sequence_analysis import SequenceAnalyzer
from .utils.validation import DataValidator
from .utils.visualization import BioVisualizer

__version__ = "0.2.0"
__author__ = "GEO-INFER Team"
__email__ = "team@geo-infer.org"

__all__ = [
    "SequenceAnalyzer",
    "DataValidator",
    "BioVisualizer",
]
