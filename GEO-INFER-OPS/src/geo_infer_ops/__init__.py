"""
GEO-INFER-OPS: Operations and infrastructure management for GEO-INFER framework.

This module provides the core infrastructure for the GEO-INFER framework, ensuring
reliable, scalable, and maintainable operations across all components.
"""

__version__ = "0.1.0"

from geo_infer_ops.core.monitoring import setup_monitoring
from geo_infer_ops.core.config import load_config, get_config
from geo_infer_ops.core.testing import setup_testing
from geo_infer_ops.core.orchestrator import Orchestrator, Task, TaskStatus
from geo_infer_ops.health.checks import HealthChecker, HealthStatus, HealthCheck

# Optional dependency: kubernetes (used by DeploymentManager)
try:
    from geo_infer_ops.core.deployment import DeploymentManager
except ImportError:
    DeploymentManager = None  # type: ignore[misc,assignment]

__all__ = [
    "setup_monitoring",
    "load_config",
    "get_config",
    "setup_testing",
    "Orchestrator",
    "Task",
    "TaskStatus",
    "DeploymentManager",
    "HealthChecker",
    "HealthStatus",
    "HealthCheck",
] 