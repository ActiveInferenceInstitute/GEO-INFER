# GEO-INFER-TEST: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-TEST** module provides testing infrastructure for the GEO-INFER ecosystem, focused on validators and a programmatic pytest runner.

## Agent Capabilities

### 1. Programmatic test running

```python
from geo_infer_test import TestRunner
from geo_infer_test.core.test_runner import TestConfiguration

runner = TestRunner(
    TestConfiguration(
        modules_to_test=["SPACE", "ACT"],
        test_types=["unit", "integration"],
        parallel_execution=False,
        coverage_enabled=False,
        performance_benchmarks=False,
        log_integration_enabled=False,
    )
)
report = runner.run_all_tests()
print(report["execution_summary"])

### 2. Validators

```python
from geo_infer_test import DataQualityValidator, SpatialValidator

dq = DataQualityValidator()
sv = SpatialValidator()

print(dq.validate({"name": "dataset", "records": []}))
print(sv.validate({"name": "spatial_dataset", "records": []}))
```

### 3. System-level test entrypoint

```python
from geo_infer_test import run_full_system_test

print(run_full_system_test())
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Test Runner** | ✅ Ready | Programmatic runner built around pytest |
| **Validators** | ✅ Ready | Data quality, spatial, performance, IoT, Bayesian validators |
| **System Test** | ✅ Ready | End-to-end system test entrypoint |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **Coverage workflow** | 🔮 Medium | Standardize coverage thresholds and reporting |
| **Regression workflow** | 🔮 Medium | Baseline comparisons for critical modules |

## Integration with CI/CD

```mermaid
graph LR
    subgraph Testing
        UNIT[Unit Tests]
        INTEG[Integration Tests]
        PERF[Performance Tests]
    end
    
    subgraph CI_Pipeline
        BUILD[Build]
        TEST[Test]
        DEPLOY[Deploy]
    end
    
    subgraph Agents
        AGENT[Agent Under Test]
    end
    
    AGENT --> UNIT
    AGENT --> INTEG
    AGENT --> PERF
    
    UNIT --> TEST
    INTEG --> TEST
    PERF --> TEST
    
    BUILD --> TEST
    TEST --> DEPLOY```

## Use Cases

### 1. Cross-module integration tests

This repository also includes cross-module integration tests under `GEO-INFER-TEST/tests/integration/`.

---

This AGENTS.md documents how GEO-INFER-TEST provides testing infrastructure for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
