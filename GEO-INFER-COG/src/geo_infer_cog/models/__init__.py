"""
Models for GEO-INFER-COG

This module provides data models and schemas for cognitive representations
of spatial knowledge, user profiles, and other cognitive structures used
in geospatial reasoning and interface design.

Available Models:
- Cognitive Maps: Mental spatial models and landmark navigation
- Spatial Knowledge Graphs: Structured spatial knowledge representation
- User Cognitive Profiles: Individual spatial cognition characteristics
- Spatial Perception Models: Human-like spatial understanding
- Spatial Reasoning Models: Computational spatial inference
- Spatial Memory Models: Human memory systems for spatial knowledge

Integration Points:
- GEO-INFER-SPACE: Enhanced spatial operations with cognitive models
- GEO-INFER-APP: Improved interface design with cognitive principles
- GEO-INFER-AGENT: Cognitive models for agent decision-making
"""

from .cognitive_models import (
    SpatialNode,
    SpatialEdge,
    CognitiveMap,
    SpatialKnowledgeGraph
)

from .user_profiles import (
    UserCognitiveProfile,
    ProfileManager
)

__all__ = [
    # Cognitive Models
    "SpatialNode",
    "SpatialEdge",
    "CognitiveMap",
    "SpatialKnowledgeGraph",

    # User Profiles
    "UserCognitiveProfile",
    "ProfileManager"
]
