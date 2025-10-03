"""
Core Components for GEO-INFER-COG

This module contains the core cognitive processing components that implement
human-like spatial cognition, including perception, reasoning, memory, and
decision-making systems.

Available Core Components:
- Cognitive Processing Engine: Main orchestration of spatial cognition
- Spatial Perception Models: Human-like spatial understanding
- Spatial Reasoning Engine: Computational spatial inference
- Spatial Memory Model: Human memory systems for spatial knowledge
- Supporting models and utilities for cognitive processing

Integration Points:
- GEO-INFER-SPACE: Enhanced spatial operations with cognitive models
- GEO-INFER-AI: Human-like spatial intelligence frameworks
- GEO-INFER-APP: Improved interface design with cognitive principles
"""

from .cognitive_engine import (
    CognitiveProcessingEngine,
    CognitiveState
)

from .spatial_perception import (
    SpatialPerceptionModel,
    SpatialPercept,
    AttentionModel
)

from .spatial_reasoning import (
    SpatialReasoningEngine,
    SpatialRelation,
    ReasoningStep
)

from .spatial_memory import (
    SpatialMemoryModel,
    SpatialMemoryItem,
    MemoryConsolidation
)

__all__ = [
    # Main cognitive processing components
    "CognitiveProcessingEngine",
    "CognitiveState",

    # Spatial perception components
    "SpatialPerceptionModel",
    "SpatialPercept",
    "AttentionModel",

    # Spatial reasoning components
    "SpatialReasoningEngine",
    "SpatialRelation",
    "ReasoningStep",

    # Spatial memory components
    "SpatialMemoryModel",
    "SpatialMemoryItem",
    "MemoryConsolidation"
]
