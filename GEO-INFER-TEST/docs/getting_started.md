# Getting Started with GEO-INFER-TEST

This guide covers installation, running tests, understanding output, and the key commands for everyday testing of GEO-INFER modules.

## Installation

Install the test module in editable mode:

```bash
uv pip install -e ./GEO-INFER-TEST
```

The test runner depends on `pytest` and optionally on `pytest-cov` for coverage reports:

```bash
uv pip install pytest pytest-cov
```

Verify the installation:

```python
import geo_infer_test
print(geo_infer_test.__version__)
# 1.0.0
```

## Core Concept: Unified Testing Across 44 Modules

GEO-INFER contains 44 modules, each with its own `tests/` directory. GEO-INFER-TEST provides a single entry point to discover and run tests from any or all of them.

The system works in three stages:

1. **Discovery**: Scan `GEO-INFER-*/tests/` directories to find test files.
2. **Execution**: Run discovered tests through pytest with appropriate markers and configuration.
3. **Reporting**: Aggregate results into per-module and framework-wide reports.

## Running Tests: The Essential Commands

### Run All Tests

Execute the entire framework test suite:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py
```

This discovers all modules, runs their tests, and produces a summary report.

### Run Tests for a Specific Module

Target a single module by name (case-insensitive, without the GEO-INFER- prefix):

```bash
# Test the MATH module
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH

# Test the SPACE module
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE

# Test TRANSPORT
uv run python GEO-INFER-TEST/run_unified_tests.py --module TRANSPORT
```

### Run by Category

Run the canonical test-directory categories:

```bash
# Only unit tests
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit

# Only integration tests
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# Performance benchmarks
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
```

### Direct pytest Invocation

For finer control, use pytest directly:

```bash
# Run all tests in a module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Run a single test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# Run tests matching a pattern
uv run python -m pytest GEO-INFER-MATH/tests/ -k "test_transform" -v

# Run with coverage
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src --cov-report=html

# Run only fast tests
uv run python -m pytest GEO-INFER-MATH/tests/ -m fast

# Run only geospatial tests
uv run python -m pytest GEO-INFER-SPACE/tests/ -m geospatial -v
```

## Understanding Test Output

### Unified Runner Output

The `run_unified_tests.py` script produces structured output:

```
=== GEO-INFER Module Test Discovery ===
Found 44 modules with tests

Running MATH tests...
  Command: pytest GEO-INFER-MATH/tests/ -v
  Completed in 4.23s
  Tests: 42 passed, 0 failed, 0 errors

Running SPACE tests...
  Command: pytest GEO-INFER-SPACE/tests/ -v
  Completed in 6.81s
  Tests: 38 passed, 1 failed, 0 errors
  FAILURE: test_h3_resolution_bounds

...

=== Summary ===
Modules tested: 44
Total tests: 3247
Passed: 3241
Failed: 6
Errors: 0
Duration: 312.4s
```

### pytest Output Flags

Useful pytest flags for debugging:

| Flag | Description |
|------|-------------|
| `-v` | Verbose: show test names |
| `-vv` | Extra verbose: show assertion details |
| `-s` | Show stdout/stderr (print statements) |
| `-x` | Stop on first failure |
| `--tb=short` | Shorter tracebacks |
| `--tb=long` | Full tracebacks |
| `-k "pattern"` | Run tests matching name pattern |
| `-m marker` | Run tests with specific marker |
| `--lf` | Rerun only tests that failed last time |
| `--co` | Collect (list) tests without running them |

## Test Data and Fixtures

### Spatial Fixtures

GEO-INFER-TEST provides reusable spatial test fixtures:

```python
from geo_infer_test.core.validators import SpatialValidator

validator = SpatialValidator()

# Validate coordinate arrays
result = validator.validate(some_coordinate_array)
print(f"Valid: {result.passed}")
```

### Common Test Patterns

Tests across GEO-INFER modules follow consistent patterns:

```python
import pytest
import numpy as np
import xarray as xr

class TestSomeAnalyzer:
    """Tests for SomeAnalyzer class."""

    def setup_method(self):
        """Create fresh analyzer for each test."""
        self.analyzer = SomeAnalyzer()

    def test_basic_computation(self):
        """Verify basic computation produces valid output."""
        data = xr.DataArray(np.random.random((10, 10)), dims=["x", "y"])
        result = self.analyzer.compute(data)
        assert result is not None
        assert result.shape == (10, 10)

    def test_edge_case_empty_input(self):
        """Verify graceful handling of empty input."""
        data = xr.DataArray(np.array([]))
        # Should not raise, should return sensible default
        result = self.analyzer.compute(data)
        assert result is not None

    @pytest.mark.slow
    def test_large_dataset(self):
        """Verify performance on large datasets."""
        data = xr.DataArray(np.random.random((1000, 1000)), dims=["x", "y"])
        result = self.analyzer.compute(data)
        assert result.shape == (1000, 1000)
```

## Validators

GEO-INFER-TEST includes domain-specific validators:

| Validator | Purpose |
|-----------|---------|
| `DataQualityValidator` | Check completeness, consistency, accuracy |
| `SpatialValidator` | Validate CRS, bounds, resolution, geometry |
| `PerformanceValidator` | Verify runtime and memory thresholds |
| `IoTValidator` | Validate sensor data streams |
| `BayesianValidator` | Check posterior distributions and MCMC diagnostics |

### Using Validators

```python
from geo_infer_test import DataQualityValidator, SpatialValidator

# Data quality check
dq = DataQualityValidator()
result = dq.validate(my_dataset)
print(f"Quality score: {result.score}")

# Spatial validation
sv = SpatialValidator()
result = sv.validate(my_geodataframe)
print(f"CRS valid: {result.crs_valid}")
```

## Configuration

### pytest.ini / pyproject.toml

Tests use configuration from the root `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "system: System-level tests",
    "performance: Performance benchmarks",
    "geospatial: Geospatial operations",
    "api: API endpoint tests",
    "slow: Long-running tests",
    "fast: Quick tests",
]
```

### Module Discovery

The unified runner discovers modules by scanning for directories matching `GEO-INFER-*` with a non-empty `tests/` subdirectory. No manual registration is needed.

## Next Steps

- Read the [API Reference](api_reference.md) for validator and runner class details.
- Try the [Running Tests Example](examples/basic_example.md) for all common invocations.
- See [Writing Tests for a New Module](examples/advanced_example.md) for a complete walkthrough.
