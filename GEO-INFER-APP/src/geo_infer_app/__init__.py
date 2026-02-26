"""
GEO-INFER-APP

Human-computer interaction layer providing accessible geospatial applications,
dashboards, and UI components built on Active Inference principles.

This package bridges agent implementations in GEO-INFER-AGENT with user-facing
interfaces: configuration forms, visualisation widgets, and an async agent API.
"""

try:
    from geo_infer_app.models.agent_interface import AgentInterface, AgentState, AgentType
except ImportError:
    AgentInterface = None  # type: ignore[assignment,misc]
    AgentState = None  # type: ignore[assignment]
    AgentType = None  # type: ignore[assignment]

try:
    from geo_infer_app.models.agent_factory import AgentFactory
except ImportError:
    AgentFactory = None  # type: ignore[assignment]

try:
    from geo_infer_app.models.agent_visualization import AgentVisualization
except ImportError:
    AgentVisualization = None  # type: ignore[assignment]

try:
    from geo_infer_app.models.agent_configuration import AgentConfiguration
except ImportError:
    AgentConfiguration = None  # type: ignore[assignment]

try:
    from geo_infer_app.api.agent_api import AgentAPIClient, AgentManager
except ImportError:
    AgentAPIClient = None  # type: ignore[assignment,misc]
    AgentManager = None  # type: ignore[assignment,misc]

__version__ = "0.2.0"

__all__ = [
    "AgentInterface",
    "AgentState",
    "AgentType",
    "AgentFactory",
    "AgentVisualization",
    "AgentConfiguration",
    "AgentAPIClient",
    "AgentManager",
    "__version__",
]
