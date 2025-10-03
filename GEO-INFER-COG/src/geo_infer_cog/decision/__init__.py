"""
Decision Support Systems for GEO-INFER-COG

This module provides human-centered decision support systems that integrate
cognitive processing capabilities with spatial decision-making. The systems
provide personalized decision recommendations based on cognitive profiles,
uncertainty quantification, and spatial reasoning.

Available Components:
- SpatialDecisionSupport: Main decision support engine with multiple frameworks
- DecisionAlternative: Data model for decision alternatives with cognitive properties
- DecisionRecommendation: Structured decision recommendations with rationale
- DecisionStrategy: Enumeration of supported decision-making approaches

Integration Points:
- GEO-INFER-ACT: Integration with active inference for decision-making
- GEO-INFER-AGENT: Decision support for autonomous spatial agents
- GEO-INFER-APP: User interface components for decision visualization
"""

from .support import (
    SpatialDecisionSupport,
    DecisionAlternative,
    DecisionRecommendation,
    DecisionStrategy
)

__all__ = [
    "SpatialDecisionSupport",
    "DecisionAlternative",
    "DecisionRecommendation",
    "DecisionStrategy"
]
