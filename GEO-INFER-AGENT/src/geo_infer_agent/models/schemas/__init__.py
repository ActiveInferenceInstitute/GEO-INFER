"""
GEO-INFER-AGENT Model Schemas

This package provides JSON schema definitions for various agent model types,
including BDI agents, Active Inference agents, Reinforcement Learning agents,
and other architectures.

Schemas can be used for:
- Configuration validation
- API documentation
- Data structure validation
"""

from geo_infer_agent.models.schemas.active_inference_schema import (
    GENERATIVE_MODEL_SCHEMA,
    ACTIVE_INFERENCE_STATE_SCHEMA,
    ACTIVE_INFERENCE_AGENT_SCHEMA,
    SCHEMAS as ACTIVE_INFERENCE_SCHEMAS
)

__all__ = [
    # Active Inference schemas
    "GENERATIVE_MODEL_SCHEMA",
    "ACTIVE_INFERENCE_STATE_SCHEMA",
    "ACTIVE_INFERENCE_AGENT_SCHEMA",
    "ACTIVE_INFERENCE_SCHEMAS"
] 