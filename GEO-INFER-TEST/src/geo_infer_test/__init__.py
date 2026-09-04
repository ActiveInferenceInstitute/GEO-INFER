"""
GEO-INFER-TEST: Comprehensive Testing and Quality Assurance Module

This module provides testing, validation, and quality assurance capabilities
for the GEO-INFER framework. It supports unit testing, integration testing,
performance testing, and data quality validation.

Key Features:
- Automated test suite execution
- Data quality validation and monitoring
- Performance benchmarking and regression testing
- Integration testing across modules
- Spatial data validation
- IoT sensor data quality control
- Bayesian inference validation
"""

# Import core models
from .models.types import TestResult, ValidationRule

# Import validators
from .core.validators import (
    BaseValidator,
    DataQualityValidator,
    PerformanceValidator,
    SpatialValidator,
    IoTValidator,
    BayesianValidator,
    QualityController,
    run_full_system_test,
)

# Import the canonical test runner and its configuration.
from .core.test_runner import (
    GeoInferTestRunner,
    TestConfiguration,
)

from .testing import (
    LocalService,
    as_finite_array,
    assert_finite,
    assert_model_contract,
    assert_no_nan_statistics,
    assert_probability,
    assert_same_finite_values,
    assert_seed_replay,
    assert_stochastic_matrix,
    assert_visualization_manifest,
)

__version__ = "0.2.0"

__all__ = [
    "GeoInferTestRunner",
    "TestConfiguration",
    "TestResult",
    "ValidationRule",
    "BaseValidator",
    "DataQualityValidator",
    "PerformanceValidator",
    "SpatialValidator",
    "IoTValidator",
    "BayesianValidator",
    "QualityController",
    "run_full_system_test",
    "LocalService",
    "as_finite_array",
    "assert_finite",
    "assert_model_contract",
    "assert_no_nan_statistics",
    "assert_probability",
    "assert_same_finite_values",
    "assert_seed_replay",
    "assert_stochastic_matrix",
    "assert_visualization_manifest",
]
