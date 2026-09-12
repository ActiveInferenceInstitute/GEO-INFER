"""Emergent Behavior Pattern Analysis for GEO-INFER-ANT.

Package split of the former single-file ``analysis.patterns`` module along its
public class boundaries:

- ``_config``: :class:`AnalysisConfiguration` dataclass
- ``analyzer``: :class:`SwarmPatternAnalyzer` engine
"""

from ._config import AnalysisConfiguration
from .analyzer import SwarmPatternAnalyzer

__all__ = ["AnalysisConfiguration", "SwarmPatternAnalyzer"]
