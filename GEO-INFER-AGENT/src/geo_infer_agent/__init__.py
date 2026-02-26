"""
GEO-INFER-AGENT - Autonomous agent framework for geospatial applications

This module provides functionality for:
- Creating intelligent autonomous agents
- Orchestrating multi-agent systems
- Implementing active inference for decision-making
- Supporting various agent architectures
- Handling geospatial perception and action
"""

__version__ = "0.1.0"

try:
    from geo_infer_agent.core.agent_base import BaseAgent, AgentState
    from geo_infer_agent.core.agent_registry import AgentRegistry
except ImportError:
    pass

try:
    from geo_infer_agent.models import (
        BDIAgent, BDIState,
        ActiveInferenceAgent, ActiveInferenceState, GenerativeModel,
        RLAgent, RLState,
        RuleBasedAgent, RuleBasedState,
        HybridAgent, HybridState,
        Belief, Desire, Plan,
    )
except ImportError:
    pass

try:
    from geo_infer_agent.api.messaging import MessagingService, Message
    from geo_infer_agent.api.telemetry import TelemetryService
except ImportError:
    pass

__all__ = [
    "__version__",
    "BaseAgent", "AgentState",
    "AgentRegistry",
    "BDIAgent", "BDIState",
    "ActiveInferenceAgent", "ActiveInferenceState", "GenerativeModel",
    "RLAgent", "RLState",
    "RuleBasedAgent", "RuleBasedState",
    "HybridAgent", "HybridState",
    "Belief", "Desire", "Plan",
    "MessagingService", "Message",
    "TelemetryService",
] 