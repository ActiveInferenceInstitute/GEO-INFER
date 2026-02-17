---
title: "GEO-INFER-TEST: Testing Framework"
description: "Unit testing, integration testing, and validation for GEO-INFER modules"
purpose: "Provide comprehensive testing infrastructure for geospatial components"
module_type: "Infrastructure"
status: "Stable"
last_updated: "2026-01-26"
dependencies: []
compatibility: ["All GEO-INFER modules"]
tags: ["testing", "validation", "quality", "ci-cd", "coverage"]
difficulty: "Intermediate"
estimated_time: "40"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-TEST: Testing Framework

## Overview

**GEO-INFER-TEST** provides testing infrastructure:

- **Unit Testing**: Component-level tests
- **Integration Testing**: Cross-module tests
- **Spatial Validation**: Geometry validation
- **Performance Testing**: Benchmarking
- **Property-Based Testing**: Fuzzing with Hypothesis

## Features

### Spatial Test Fixtures

```python
from geo_infer_test import SpatialFixtures

# Generate test data
fixtures = SpatialFixtures()

points = fixtures.random_points(n=100, bbox=city)
polygons = fixtures.random_polygons(n=50)
grid = fixtures.hexagonal_grid(resolution=9)
```

### Geometry Validation

```python
from geo_infer_test import GeometryValidator

# Validate geometries
validator = GeometryValidator()

result = validator.validate(
    geometries=test_data,
    checks=["valid", "simple", "topology"]
)

print(f"Valid: {result.valid_count}")
print(f"Issues: {result.issues}")
```

### Agent Testing

```python
from geo_infer_test import AgentTester

# Test agent behavior
tester = AgentTester()

result = tester.test_agent(
    agent=my_agent,
    scenarios=test_scenarios,
    metrics=["accuracy", "efficiency"]
)
```

### Performance Benchmarks

```python
from geo_infer_test import Benchmarker

# Benchmark operations
bench = Benchmarker()

results = bench.run(
    operations=["buffer", "intersect", "h3_index"],
    data_sizes=[1000, 10000, 100000]
)
```

## Test Types

| Type | Description |
|------|-------------|
| **Unit** | Single function |
| **Integration** | Module interaction |
| **E2E** | Full workflow |
| **Performance** | Speed/memory |

## Installation

```bash
uv pip install -e "./GEO-INFER-TEST"
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=geo_infer
```

---

**Status**: Stable

**Last Updated**: 2026-01-26
