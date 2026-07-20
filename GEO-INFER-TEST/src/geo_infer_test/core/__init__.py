"""
Core functionality for the GEO-INFER-TEST module.

This submodule contains the essential components for comprehensive testing
of the GEO-INFER ecosystem, including integration with logging and reporting.
"""

# Import core components with explicit imports
from .test_runner import (
    TestConfiguration,
    TestResult,
    GeoInferTestRunner,
)

from .test_discoverer import (
    TestDiscoverer,
)

from .test_orchestrator import TestOrchestrator, TestSuiteManager
from .log_integration import (
    LogIntegration,
    LoggingTestReporter,
    TestLogger,
    LogAnalyzer,
)
from .module_health import (
    ModuleHealthChecker,
    HealthMetrics,
    SystemValidator,
    DependencyChecker,
)
from .performance_monitor import (
    PerformanceMonitor,
    BenchmarkRunner,
    LoadTester,
    MetricsCollector,
    PerformanceAnalyzer,
)

# Package exports
__all__ = [
    # Test execution framework
    "TestConfiguration",
    "TestResult",
    "GeoInferTestRunner",
    "TestDiscoverer",
    "TestOrchestrator",
    "TestSuiteManager",
    # Logging and monitoring integration
    "LogIntegration",
    "LoggingTestReporter",
    "TestLogger",
    "LogAnalyzer",
    # Health monitoring
    "ModuleHealthChecker",
    "HealthMetrics",
    "SystemValidator",
    "DependencyChecker",
    # Performance monitoring
    "PerformanceMonitor",
    "BenchmarkRunner",
    "LoadTester",
    "MetricsCollector",
    "PerformanceAnalyzer",
]
