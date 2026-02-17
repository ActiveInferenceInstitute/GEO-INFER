# GEO-INFER Testing Guide

## Overview

This document provides instructions for running tests across the GEO-INFER ecosystem. The testing infrastructure includes:

- Module-specific unit tests
- Cross-module integration tests
- Performance benchmarks
- Coverage analysis
- **Property-based fuzzing (Hypothesis)**

## Test Execution

### 1. Running All Tests (Recommended)

```bash
# Navigate to GEO-INFER-TEST
cd GEO-INFER-TEST

# Run full suite
python -m pytest
```

### 2. Property-Based Testing

We use [Hypothesis](https://hypothesis.readthedocs.io/) to generate thousands of test cases, fuzzing inputs for robustness.

```bash
# Run tests with execution statistics
python -m pytest --hypothesis-show-statistics

# key modules covered:
# - Spatial Functions (H3, Geometry)
# - Module Health (FileSystem resilience)
# - Test Orchestrator (DAG resolution)
# - Log Integration (Message fuzzing)
```

### 3. Running Specific Categories

```bash
# Run only unit tests
python -m pytest tests/unit

# Run only integration tests
python -m pytest tests/integration

# Run performance benchmarks
python -m pytest tests/unit/test_performance_monitor.py
```

## Test Reports

After test execution, results are available in:

- Console output (standard)
- `test_report_*.json` (if LogIntegration is configured)

## Adding Tests

1. **Standard Unit Tests**:
   - Create `tests/unit/test_<module>.py`
   - Use `pytest` fixtures

2. **Property-Based Tests**:
   - Import `from hypothesis import given, strategies as st`
   - Decorate test functions with `@given(...)`
   - Ensure tests are deterministic and stateless where possible

## Troubleshooting

- **Fixture Errors**: Ensure `conftest.py` is present or fixtures are defined in the test file.
- **Hypothesis Flakiness**: If a test fails only sometimes, run with `--hypothesis-seed=<SEED>` to reproduce.
