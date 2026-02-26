# GEO-INFER-TEST Documentation

GEO-INFER-TEST provides the unified testing infrastructure for the entire GEO-INFER framework. It supports automated test execution across all 44 modules, data quality validation, performance benchmarking, spatial data verification, and cross-module integration testing.

## Module Architecture

The module serves as the central testing hub for the framework:

| Component | Class | Purpose |
|-----------|-------|---------|
| Test Runner | `GeoInferTestRunner` | Unified test execution across modules |
| Test Discoverer | `TestDiscoverer` | Dynamic discovery of test files across 44 modules |
| Validators | `DataQualityValidator`, `SpatialValidator`, `PerformanceValidator` | Domain-specific validation |
| Quality Controller | `QualityController` | Aggregated quality scoring |
| Performance Monitor | `BenchmarkRunner`, `LoadTester` | Performance testing and regression detection |
| Module Health | `ModuleHealthChecker`, `DependencyChecker` | Module status and dependency validation |
| IoT/Bayesian | `IoTValidator`, `BayesianValidator` | Specialized validation for sensor data and probabilistic models |

## Two Execution Paths

GEO-INFER-TEST provides two ways to run tests:

### 1. Unified Test Runner Script

The `run_unified_tests.py` script at the module root dynamically discovers and runs tests across all GEO-INFER modules:

```bash
# Run all tests
uv run python GEO-INFER-TEST/run_unified_tests.py

# Run tests for a specific module
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH

# Run by category
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
```

### 2. Python API

The `GeoInferTestRunner` class provides programmatic test execution:

```python
from geo_infer_test import TestRunner

runner = TestRunner()
results = runner.run_module("MATH")
```

## Test Categories

Tests are organized by pytest markers:

| Marker | Description | Typical Runtime |
|--------|-------------|-----------------|
| `unit` | Isolated function/class tests | < 1s each |
| `integration` | Cross-component tests | 1-10s each |
| `system` | Full pipeline tests | 10-60s each |
| `performance` | Benchmarks and load tests | Variable |
| `geospatial` | Spatial data operations | 1-30s each |
| `api` | REST API endpoint tests | 1-5s each |
| `slow` | Long-running tests | > 60s each |
| `fast` | Quick verification tests | < 0.5s each |

## Module Standard

Every GEO-INFER module contains at minimum 4 test files organized as:

```
GEO-INFER-MODULE/tests/
  unit/
    test_core.py         # Core functionality tests
    test_models.py       # Data model tests
  integration/
    test_pipeline.py     # End-to-end pipeline tests
    test_api.py          # API integration tests
```

## Integration with Other Modules

- **All 44 modules**: GEO-INFER-TEST discovers and runs tests from every module.
- **GEO-INFER-OPS**: Test results feed into CI/CD pipelines and quality dashboards.
- **GEO-INFER-LOG**: Test execution logging and reporting integration.
- **GEO-INFER-DATA**: Data quality validators use GEO-INFER-DATA schema definitions.

## Quick Links

- [Getting Started](getting_started.md) -- installation, running tests, understanding output
- [API Reference](api_reference.md) -- test runner, validators, benchmarks, configuration
- [Basic Example: Running Tests](examples/basic_example.md) -- all common invocations
- [Advanced Example: Writing Tests](examples/advanced_example.md) -- adding tests to a new module

## Package Structure

```
GEO-INFER-TEST/
  run_unified_tests.py       # CLI test runner script
  validate_skills.py         # SKILL.md validation tool
  src/geo_infer_test/
    __init__.py              # Exports TestRunner, validators, models
    core/
      test_runner.py         # GeoInferTestRunner, TestConfiguration
      test_discoverer.py     # TestDiscoverer
      test_orchestrator.py   # TestOrchestrator, TestSuiteManager
      validators.py          # All validator classes + QualityController
      log_integration.py     # LogIntegration, TestLogger
      module_health.py       # ModuleHealthChecker, DependencyChecker
      performance_monitor.py # BenchmarkRunner, LoadTester
    models/
      types.py               # TestResult, ValidationRule
    api/                     # REST API for test management
    utils/                   # Shared test utilities
  tests/
    unit/
    integration/
  docs/                      # This documentation
```

## Version

Current version: `1.0.0`
