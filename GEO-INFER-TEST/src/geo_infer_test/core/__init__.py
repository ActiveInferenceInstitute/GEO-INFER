"""
Core functionality for the GEO-INFER-TEST module.

This submodule contains the essential components for comprehensive testing
of the GEO-INFER ecosystem, including integration with logging and reporting.
"""

# Import core components
from .test_runner import *
from .test_discoverer import *
from .test_orchestrator import *
from .log_integration import *
from .module_health import *
from .performance_monitor import *

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