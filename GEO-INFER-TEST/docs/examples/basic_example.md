# Basic Example: Running the Test Suite

This example walks through all common test runner invocations, from running the full suite to targeting specific tests for debugging.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-TEST
uv pip install pytest pytest-cov
```

## 1. Run All Module Tests

The most common operation: run every test across all 44 modules.

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py
```

Expected output:

```
=== GEO-INFER Module Test Discovery ===
Found 44 modules with tests

Running ACT tests...
  Completed in 3.21s - 18 passed, 0 failed

Running AG tests...
  Completed in 2.87s - 12 passed, 0 failed

...

Running WATER tests...
  Completed in 4.12s - 15 passed, 0 failed

=== SUMMARY ===
Modules tested: 44
Total tests: 3247
Passed: 3241
Failed: 6
Errors: 0
Skipped: 23
Duration: 312.4s
```

## 2. Run a Single Module

Focus on one module during development:

```bash
# Run MATH module tests
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH
```

Or use pytest directly for more control:

```bash
# Verbose output showing each test
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Expected output:
# GEO-INFER-MATH/tests/unit/test_transforms.py::test_fourier_transform PASSED
# GEO-INFER-MATH/tests/unit/test_transforms.py::test_wavelet_transform PASSED
# GEO-INFER-MATH/tests/unit/test_spatial_statistics.py::test_moran_i PASSED
# ...
```

## 3. Run by Test Category

Filter tests by purpose:

```bash
# Unit tests only (fastest)
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit

# Integration tests (cross-component)
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# Performance benchmarks
uv run python GEO-INFER-TEST/run_unified_tests.py --category performance
```

Using pytest markers directly:

```bash
# Fast tests only
uv run python -m pytest GEO-INFER-SPACE/tests/ -m fast -v

# Geospatial tests
uv run python -m pytest GEO-INFER-SPACE/tests/ -m geospatial -v

# Exclude slow tests
uv run python -m pytest GEO-INFER-BAYES/tests/ -m "not slow" -v
```

## 4. Run a Single Test File

When debugging a specific issue:

```bash
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v
```

Run a single test function:

```bash
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py::test_moran_i -v
```

Run tests matching a keyword:

```bash
# All tests with "transform" in the name
uv run python -m pytest GEO-INFER-MATH/tests/ -k "transform" -v

# All tests with "h3" in the name
uv run python -m pytest GEO-INFER-SPACE/tests/ -k "h3" -v
```

## 5. Run with Coverage

Generate coverage reports to identify untested code:

```bash
# Terminal coverage summary
uv run python -m pytest GEO-INFER-MATH/tests/ \
  --cov=GEO-INFER-MATH/src \
  --cov-report=term-missing

# HTML coverage report
uv run python -m pytest GEO-INFER-MATH/tests/ \
  --cov=GEO-INFER-MATH/src \
  --cov-report=html

# Open the report
open htmlcov/index.html
```

## 6. Debugging Failed Tests

When a test fails, use these strategies:

### Stop on First Failure

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ -x -v
```

### Show Full Tracebacks

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ --tb=long -v
```

### Show Print Output

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ -s -v
```

### Rerun Only Failed Tests

```bash
# First run: some tests fail
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ -v

# Second run: only rerun failures
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ --lf -v
```

### List Tests Without Running

```bash
uv run python -m pytest GEO-INFER-TRANSPORT/tests/ --co
```

## 7. Using Validators Programmatically

Run domain-specific validation from Python:

```python
from geo_infer_test import DataQualityValidator, SpatialValidator

# Validate data quality
dq = DataQualityValidator()

import numpy as np
import xarray as xr

data = xr.DataArray(np.random.random((100, 100)), dims=["x", "y"])
result = dq.validate(data)
print(f"Data quality valid: {result.passed}")

# Validate spatial data
sv = SpatialValidator()
# result = sv.validate(my_geodataframe)
```

## 8. Run System-Wide Health Check

Execute the full system validation:

```python
from geo_infer_test import run_full_system_test

results = run_full_system_test()
print(f"System health: {results}")
```

## 9. Validate Module SKILL.md Files

Check that all modules have valid SKILL.md files:

```bash
uv run python GEO-INFER-TEST/validate_skills.py
```

## 10. Common pytest Configuration Flags

A reference table for everyday use:

| Command | What it does |
|---------|-------------|
| `pytest -v` | Show each test name |
| `pytest -vv` | Show assertion details |
| `pytest -s` | Show print/logging output |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Rerun only last failures |
| `pytest --co` | List tests without running |
| `pytest -k "name"` | Match test name pattern |
| `pytest -m unit` | Run marked tests only |
| `pytest --tb=short` | Shorter tracebacks |
| `pytest --durations=10` | Show 10 slowest tests |
| `pytest --cov=src` | Measure code coverage |
| `pytest -p no:warnings` | Suppress warnings |

## Key Takeaways

1. **Start broad, narrow down**: Begin with the unified runner for a full status check, then target specific modules or tests for debugging.
2. **Use markers for speed**: Running only `unit` or `fast` tests during development gives quick feedback. Save `integration` and `performance` for CI.
3. **Coverage reveals gaps**: Run coverage periodically to find untested code paths.
4. **Rerun failures**: The `--lf` flag saves time when fixing flaky or newly-broken tests.

## Next Steps

- See the [API Reference](../api_reference.md) for validator class details.
- Read [Writing Tests for a New Module](advanced_example.md) for a complete walkthrough.
