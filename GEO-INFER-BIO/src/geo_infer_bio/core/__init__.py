"""
GEO-INFER-BIO core package.

Core analytical components:
- sequence_analysis: spatially-aware biological sequence analysis
"""

from .sequence_analysis import SequenceAnalyzer

__all__ = [
    "SequenceAnalyzer",
]
