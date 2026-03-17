---
title: "GEO-INFER-TEST: Testing Framework"
description: "Unit testing, integration testing, and validation for GEO-INFER modules"
purpose: "Provide comprehensive testing infrastructure for geospatial components"
module_type: "Infrastructure"
status: "Stable"
last_updated: "2026-02-25"
dependencies: []
compatibility: ["All GEO-INFER modules"]
tags: ["testing", "validation", "quality", "ci-cd", "coverage"]
difficulty: "Intermediate"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> |
  <a href="../README.md#-module-overview">Module Index</a> |
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-TEST: Testing Framework

## Overview

**GEO-INFER-TEST** provides testing infrastructure for all 44 GEO-INFER modules:

- **Unit Testing**: Component-level tests for individual functions and classes
- **Integration Testing**: Cross-module interaction and data flow tests
- **Spatial Validation**: Geometry correctness, topology checks, CRS handling
- **Performance Testing**: Benchmarking with pytest-benchmark
- **Property-Based Testing**: Fuzzing with Hypothesis for edge case discovery

## Features

### Validators and test runner

```python
from geo_infer_test import (
    TestRunner,
    DataQualityValidator,
    SpatialValidator,
    PerformanceValidator,
    run_full_system_test,
)
from geo_infer_test.core.test_runner import TestConfiguration

# Run a minimal validation suite
qc = DataQualityValidator()
print(qc.validate({"name": "example_dataset", "records": []}))

# Run tests through the test runner (programmatic wrapper around pytest)
runner = TestRunner(
    TestConfiguration(
        modules_to_test=["TEST"],
        test_types=["unit"],
        parallel_execution=False,
        coverage_enabled=False,
        performance_benchmarks=False,
        log_integration_enabled=False,
    )
)
print(runner.run_all_tests())

# Or run an end-to-end system test
print(run_full_system_test())
```

### Notes

- This module focuses on **validators**, a **test runner**, and end-to-end system checks via `run_full_system_test`.
- Agent-specific fixtures and mock environments should be documented in the modules that implement them.

## Test Types

| Type | Description | Pytest Markers |
|------|-------------|----------------|
| **Unit** | Single function, isolated logic | `unit`, `fast` |
| **Integration** | Module interaction, data flow | `integration` |
| **E2E** | Full workflow, multi-module pipelines | `system` |
| **Performance** | Speed/memory benchmarks | `performance`, `slow` |
| **Spatial** | Geometry, CRS, topology validation | `geospatial`, `h3` |

## Installation

```bash
uv pip install -e "./GEO-INFER-TEST"
```

## Running Tests

```bash
# Run all tests across every module
uv run python GEO-INFER-TEST/run_unified_tests.py

# Run tests for a single module
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH

# Run by category
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit

# Run directly with pytest for a single module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Run a single test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# With coverage
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src --cov-report=html
```

---

## Test Runner Flags

Full flag reference for `run_unified_tests.py`:

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py [OPTIONS]

Options:
  --module MODULE        Run tests for a specific module (e.g., MATH, SPACE, BAYES)
  --category CATEGORY    Run by category: unit, integration, system, performance
  --verbose, -v          Verbose pytest output
  --coverage             Generate coverage report (HTML + terminal)
  --output FORMAT        Output format: text (default), json, junit
  --junit-xml PATH       Write JUnit XML to path (for CI pipelines)
  --markers MARKERS      Comma-separated pytest markers to filter
  --fail-fast            Stop on first failure
  --parallel N           Run N modules in parallel (default: 1)
  --timeout SECONDS      Per-test timeout in seconds (default: 60)
```

### Examples

```bash
# Run only unit tests for MATH module with coverage
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --module MATH --category unit --coverage

# Run all integration tests with JUnit output for CI
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --category integration --output junit --junit-xml results.xml

# Run with 4 parallel module workers, fail on first error
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --parallel 4 --fail-fast

# Run only tests marked as geospatial across all modules
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --markers geospatial

# Run SPACE module tests with 120-second timeout per test
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --module SPACE --timeout 120 --verbose

# Run performance benchmarks for BAYES
uv run python GEO-INFER-TEST/run_unified_tests.py \
  --module BAYES --category performance
```

### Running Tests Directly with pytest

For finer-grained control, invoke pytest directly:

```bash
# Run tests matching a keyword expression
uv run python -m pytest GEO-INFER-ACT/tests/ -k "free_energy" -v

# Run tests with a specific marker
uv run python -m pytest GEO-INFER-SPACE/tests/ -m "h3" -v

# Run with maximum verbosity and no capture
uv run python -m pytest GEO-INFER-BAYES/tests/ -vvs

# Run and stop after 3 failures
uv run python -m pytest GEO-INFER-DATA/tests/ --maxfail=3
```

---

## Coverage Configuration

### pyproject.toml Settings

Add to a module's `pyproject.toml` for per-module coverage:

```toml
[tool.coverage.run]
source = ["src"]
omit = ["*/__init__.py", "*/tests/*", "*/conftest.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",  # only in abstract methods
]
```

### Coverage Targets by Category

| Category | Target | Rationale |
|----------|--------|-----------|
| Unit tests | >= 80% | Core logic must be well-tested |
| Integration tests | >= 70% | Cross-module paths covered |
| System tests | >= 60% | End-to-end critical paths |

### Generating Coverage Reports

```bash
# Terminal report with missing lines
uv run python -m pytest GEO-INFER-MATH/tests/ \
  --cov=GEO-INFER-MATH/src \
  --cov-report=term-missing

# HTML report (opens in browser)
uv run python -m pytest GEO-INFER-MATH/tests/ \
  --cov=GEO-INFER-MATH/src \
  --cov-report=html:test-results/math-coverage

# Combined terminal + HTML + XML (for CI)
uv run python -m pytest GEO-INFER-MATH/tests/ \
  --cov=GEO-INFER-MATH/src \
  --cov-report=term-missing \
  --cov-report=html:test-results/math-coverage \
  --cov-report=xml:test-results/math-coverage.xml \
  --cov-fail-under=80
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: GEO-INFER Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: |
          uv pip install -e "./GEO-INFER-MATH[dev]" \
            "./GEO-INFER-SPACE[dev]" \
            "./GEO-INFER-BAYES[dev]" \
            "./GEO-INFER-TEST[dev]"

      - name: Run GEO-INFER tests
        run: |
          uv run python GEO-INFER-TEST/run_unified_tests.py \
            --output junit \
            --junit-xml test-results/junit.xml \
            --coverage

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.python-version }}
          path: test-results/

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: test-results/coverage.xml
          fail_ci_if_error: false
```

### Integration with Other CI Systems

**GitLab CI:**

```yaml
test:
  image: python:3.11
  script:
    - pip install uv
    - uv pip install -e "./GEO-INFER-TEST[dev]"
    - uv run python GEO-INFER-TEST/run_unified_tests.py --output junit --junit-xml report.xml
  artifacts:
    reports:
      junit: report.xml
```

**Pre-commit Hook (fast unit tests only):**

```bash
#!/bin/sh
# .git/hooks/pre-commit
uv run python -m pytest GEO-INFER-TEST/tests/unit/ -x -q --timeout=30
```

---

## Module Testing Quick Reference

All 44 modules with test file counts, primary markers, and coverage targets.

### Analytical Core

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| MATH | 16 | tests/unit/, tests/integration/ | unit, geospatial | 80% |
| ACT | 19 | tests/unit/, tests/integration/ | unit, active_inference | 80% |
| BAYES | 13 | tests/unit/, tests/integration/ | unit, bayesian | 80% |
| AI | 12 | tests/unit/, tests/integration/ | unit, ml | 80% |
| COG | 12 | tests/unit/, tests/integration/ | unit, cognitive | 80% |
| AGENT | 13 | tests/unit/, tests/integration/ | unit, agent | 80% |
| SPM | 16 | tests/unit/, tests/integration/ | unit, spatial | 80% |

### Spatial-Temporal

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| SPACE | 31 | tests/unit/, tests/integration/ | unit, geospatial, h3 | 80% |
| TIME | 14 | tests/unit/, tests/integration/ | unit, temporal | 80% |
| IOT | 7 | tests/unit/, tests/integration/ | unit, iot | 75% |

### Infrastructure

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| DATA | 19 | tests/unit/, tests/integration/ | unit, data | 80% |
| API | 8 | tests/unit/, tests/integration/ | unit, api | 80% |
| SEC | 8 | tests/unit/, tests/integration/ | unit, security | 80% |
| OPS | 12 | tests/unit/, tests/integration/ | unit, ops | 75% |
| METAGOV | 13 | tests/unit/, tests/integration/ | unit, governance | 75% |

### Domain-Specific

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| AG | 12 | tests/unit/, tests/integration/ | unit, agriculture | 75% |
| HEALTH | 10 | tests/unit/, tests/integration/ | unit, health | 75% |
| ECON | 12 | tests/unit/, tests/integration/ | unit, economics | 75% |
| RISK | 11 | tests/unit/, tests/integration/ | unit, risk | 80% |
| LOG | 9 | tests/unit/, tests/integration/ | unit, logistics | 75% |
| BIO | 6 | tests/unit/, tests/integration/ | unit, biology | 75% |
| CLIMATE | 8 | tests/unit/, tests/integration/ | unit, climate | 75% |
| ENERGY | 7 | tests/unit/, tests/integration/ | unit, energy | 75% |
| FOREST | 7 | tests/unit/, tests/integration/ | unit, forestry | 75% |
| MARINE | 7 | tests/unit/, tests/integration/ | unit, marine | 75% |
| EMERGENCY | 7 | tests/unit/, tests/integration/ | unit, emergency | 75% |
| EDU | 8 | tests/unit/, tests/integration/ | unit, education | 75% |
| TRANSPORT | 8 | tests/unit/, tests/integration/ | unit, transport | 75% |
| WATER | 6 | tests/unit/, tests/integration/ | unit, hydrology | 75% |

### Agent and Simulation

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| ANT | 7 | tests/unit/, tests/integration/ | unit, ant_colony | 75% |
| SIM | 5 | tests/unit/, tests/integration/ | unit, simulation | 75% |

### Community and Applications

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| CIV | 7 | tests/unit/, tests/integration/ | unit, civic | 75% |
| PEP | 9 | tests/unit/, tests/integration/ | unit, people | 75% |
| ORG | 7 | tests/unit/, tests/integration/ | unit, organization | 75% |
| COMMS | 8 | tests/unit/, tests/integration/ | unit, communications | 75% |
| APP | 8 | tests/unit/, tests/integration/ | unit, application | 75% |
| ART | 9 | tests/unit/, tests/integration/ | unit, creative | 75% |

### Governance

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| NORMS | 7 | tests/unit/, tests/integration/ | unit, norms | 80% |
| REQ | 7 | tests/unit/, tests/integration/ | unit, requirements | 75% |

### Operations

| Module | Test Files | Test Directories | Key Markers | Coverage Target |
|--------|-----------|------------------|-------------|-----------------|
| INTRA | 12 | tests/unit/, tests/integration/ | unit, intranet | 75% |
| GIT | 8 | tests/unit/, tests/integration/ | unit, git | 75% |
| TEST | 19 | tests/unit/, tests/integration/ | unit, meta_testing | 80% |
| EXAMPLES | 6 | tests/unit/, tests/integration/ | unit, examples | 70% |
| PLACE | 15 | tests/unit/, tests/integration/ | unit, geospatial, place | 80% |

**Totals: 44 modules | 466 test files | 3,000+ tests**

---

## Pytest Markers Reference

Available markers defined in the framework:

```ini
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (cross-module)",
    "system: System/E2E tests (full pipeline)",
    "performance: Performance benchmarks (slow)",
    "geospatial: Tests involving spatial operations",
    "h3: Tests using H3 hexagonal grid",
    "bayesian: Tests involving Bayesian inference",
    "active_inference: Tests involving Active Inference",
    "api: API endpoint tests",
    "slow: Tests that take >10 seconds",
    "fast: Tests that complete in <1 second",
]
```

Usage:

```bash
# Run only fast unit tests
uv run python -m pytest GEO-INFER-MATH/tests/ -m "unit and fast"

# Run geospatial tests excluding slow ones
uv run python -m pytest GEO-INFER-SPACE/tests/ -m "geospatial and not slow"

# Run all bayesian-related tests across the whole repo
uv run python -m pytest -m "bayesian" --rootdir=.
```

---

## Writing Tests

### Test File Naming Convention

```
tests/
  unit/
    test_<feature>.py         # Unit tests for a feature
    test_<class>_methods.py   # Unit tests for a class
  integration/
    test_<workflow>.py        # Integration workflow tests
    test_cross_module.py      # Cross-module interaction tests
```

### Test Function Naming

```python
def test_<function_name>_<scenario>_<expected_result>():
    """Descriptive docstring explaining the test."""
    ...

# Examples:
def test_buffer_positive_distance_returns_expanded_polygon():
    ...

def test_h3_index_invalid_resolution_raises_value_error():
    ...
```

### Fixture Conventions

Shared fixtures go in `conftest.py` at the test root:

```python
# tests/conftest.py
import pytest
from shapely.geometry import Point, Polygon

@pytest.fixture
def sample_point():
    return Point(0.0, 0.0)

@pytest.fixture
def sample_polygon():
    return Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])

@pytest.fixture
def h3_resolution():
    return 9
```

---

## Links

- [Unified Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md)
- [Performance Benchmarking Guide](../GEO-INFER-EXAMPLES/docs/PERFORMANCE_BENCHMARKING_GUIDE.md)
- [Integration Guide](../GEO-INFER-EXAMPLES/docs/INTEGRATION_GUIDE.md)
- [Root CLAUDE.md Testing Section](../CLAUDE.md)

---

**Status**: Stable

**Last Updated**: 2026-02-25

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
