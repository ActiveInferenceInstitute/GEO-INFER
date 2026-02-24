---
title: "GEO-INFER-REQ: Requirements and Dependencies"
description: "Requirements management, dependency resolution, and environment setup"
purpose: "Manage project requirements, dependencies, and deployment environments"
module_type: "Infrastructure"
status: "Stable"
last_updated: "2026-02-24"
dependencies: []
compatibility: ["All GEO-INFER modules"]
tags: ["requirements", "dependencies", "packaging", "deployment"]
difficulty: "Intermediate"
estimated_time: "30"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-REQ: Requirements and Dependencies

## Overview

**GEO-INFER-REQ** manages project dependencies and environments:

- **Requirements Parsing**: Parse and validate requirements files
- **Dependency Resolution**: Resolve complex dependency trees
- **Environment Management**: Create isolated environments
- **Compatibility Checking**: Verify version compatibility

## Features

### Requirements Analysis

```python
from geo_infer_req import RequirementsAnalyzer

# Analyze requirements
analyzer = RequirementsAnalyzer()

reqs = analyzer.parse("requirements.txt")

# Check compatibility
compat = analyzer.check_compatibility(
    requirements=reqs,
    python_version="3.11"
)

print(f"Compatible: {compat.is_compatible}")
print(f"Issues: {compat.issues}")
```

### Dependency Resolution

```python
from geo_infer_req import DependencyResolver

# Resolve dependencies
resolver = DependencyResolver()

solution = resolver.resolve(
    packages=["geo-infer-act", "geo-infer-space"],
    constraints={"numpy": ">=1.20,<2.0"}
)

print(f"Resolved: {solution.packages}")
print(f"Install order: {solution.order}")
```

### Environment Management

```python
from geo_infer_req import EnvironmentManager

# Manage environments
env_mgr = EnvironmentManager()

# Create environment
env = env_mgr.create(
    name="geo_analysis",
    requirements=["geo-infer-space", "geo-infer-data"],
    python="3.11"
)

# Activate environment
env_mgr.activate(env)
```

### Project Planning

```python
from geo_infer_req import ProjectPlanner

# Plan project requirements
planner = ProjectPlanner()

plan = planner.create(
    project_type="spatial_analysis",
    modules=["SPACE", "TIME", "DATA"]
)

print(f"Required packages: {plan.packages}")
print(f"Setup steps: {plan.steps}")
```

## Supported Formats

| Format | Description |
|--------|-------------|
| **requirements.txt** | Pip format |
| **pyproject.toml** | PEP 517/518 |
| **setup.py** | Legacy setuptools |
| **Pipfile** | Pipenv format |
| **poetry.lock** | Poetry format |

## Integration Points

| Module | Integration |
|--------|-------------|
| **GEO-INFER-OPS** | Deployment setup |
| **GEO-INFER-TEST** | Test environments |
| **All modules** | Dependency management |

## Installation

```bash
uv pip install -e "./GEO-INFER-REQ"
```

## Related Documentation

- [GEO-INFER-OPS](../GEO-INFER-OPS/README.md): Operations
- [AGENTS.md](./AGENTS.md): Requirements capabilities

---

**Status**: Stable

**Last Updated**: 2026-02-24
