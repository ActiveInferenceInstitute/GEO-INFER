"""
GEO-INFER-TEST: Comprehensive testing framework for the GEO-INFER ecosystem.

This module provides comprehensive testing capabilities for all GEO-INFER modules including:
- Automated test discovery and execution
- Integration with GEO-INFER-LOG for detailed logging and reporting  
- Performance benchmarking and load testing
- Cross-module integration testing
- Quality assurance metrics and compliance checking
- Continuous monitoring and health checks
"""

__version__ = "0.1.0"

# Import core submodules
from . import api
from . import core
from . import models
from . import utils

# Import key testing components
from .core.test_runner import GeoInferTestRunner
from .core.test_discoverer import TestDiscoverer
from .core.test_orchestrator import TestOrchestrator
from .core.log_integration import LogIntegration
from .models.test_result import TestResult, TestSuite, TestReport
from .utils.test_helpers import TestHelpers
from .utils.data_generators import TestDataGenerator
from .utils.validators import ModuleValidator

# Export public API
__all__ = [
    # Core testing framework
    "GeoInferTestRunner",
    "TestDiscoverer", 
    "TestOrchestrator",
    "LogIntegration",
    
    # Testing models and results
    "TestResult",
    "TestSuite", 
    "TestReport",
    
    # Utilities and helpers
    "TestHelpers",
    "TestDataGenerator",
    "ModuleValidator",
    
    # Submodules
    "api",
    "core", 
    "models",
    "utils"
]

# Package metadata
__author__ = "GEO-INFER Team"
__email__ = "info@geo-infer.org"
__license__ = "MIT"
__description__ = "Comprehensive testing framework for the GEO-INFER ecosystem" 