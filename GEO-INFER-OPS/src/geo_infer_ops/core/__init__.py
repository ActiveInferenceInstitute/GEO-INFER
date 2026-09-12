"""
Core functionality for GEO-INFER-OPS.
"""

from geo_infer_ops.core.config import Config, get_config
from geo_infer_ops.core.logging import get_logger
from geo_infer_ops.core.monitoring import setup_monitoring, reset_metrics
from geo_infer_ops.core.orchestrator import Orchestrator, Task, TaskStatus

__all__ = [
    "Config",
    "get_config",
    "get_logger",
    "setup_monitoring",
    "reset_metrics",
    "setup_testing",
    "create_test_client",
    "Orchestrator",
    "Task",
    "TaskStatus",
]


def __getattr__(name):
    """Lazily export test-support helpers so `import geo_infer_ops` stays
    clean-install safe: fastapi.testclient (via core.testing) requires
    httpx, which is a dev-only dependency, not a runtime one."""
    if name in ("setup_testing", "create_test_client"):
        from geo_infer_ops.core import testing

        return getattr(testing, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
