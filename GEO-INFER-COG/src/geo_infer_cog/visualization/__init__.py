"""
Human-Centered Visualization for GEO-INFER-COG

This module provides visualization adapters that create human-centered,
cognitively optimized geospatial visualizations. The adapters consider user
cognitive profiles, cognitive load preferences, and spatial cognition principles
to generate intuitive and effective visual representations.

Available Components:
- HumanCenteredVisualizer: Main visualization engine with cognitive adaptations
- VisualizationElement: Data model for visual elements with cognitive properties
- ColorScheme: Perceptually optimized color management
- Uncertainty communication strategies for spatial predictions

Integration Points:
- GEO-INFER-APP: Enhanced user interfaces with cognitive visualization
- GEO-INFER-AGENT: Visual decision support for autonomous agents
- GEO-INFER-SPACE: Cognitively optimized spatial data presentation
"""

from .adapters import (
    HumanCenteredVisualizer,
    VisualizationElement,
    ColorScheme
)

__all__ = [
    "HumanCenteredVisualizer",
    "VisualizationElement",
    "ColorScheme"
]
