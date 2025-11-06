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

# Import optional components (may be empty or not yet implemented)
try:
    from .test_orchestrator import TestOrchestrator, TestSuiteManager
except (ImportError, AttributeError):
    TestOrchestrator = None
    TestSuiteManager = None

try:
    from .log_integration import (
        LogIntegration,
        LoggingTestReporter,
        TestLogger,
        LogAnalyzer,
    )
except (ImportError, AttributeError):
    LogIntegration = None
    LoggingTestReporter = None
    TestLogger = None
    LogAnalyzer = None

try:
    from .module_health import (
        ModuleHealthChecker,
        HealthMetrics,
        SystemValidator,
        DependencyChecker,
    )
except (ImportError, AttributeError):
    ModuleHealthChecker = None
    HealthMetrics = None
    SystemValidator = None
    DependencyChecker = None

try:
    from .performance_monitor import (
        PerformanceMonitor,
        BenchmarkRunner,
        LoadTester,
        MetricsCollector,
        PerformanceAnalyzer,
    )
except (ImportError, AttributeError):
    PerformanceMonitor = None
    BenchmarkRunner = None
    LoadTester = None
    MetricsCollector = None
    PerformanceAnalyzer = None

# Package exports
__all__ = [
    # Test execution framework
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
    
    # Cross-module testing
    "IntegrationTester",
    "CrossModuleValidator",
    "APITester",
    "DataFlowValidator"
] 