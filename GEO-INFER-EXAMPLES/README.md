---
title: "GEO-INFER-EXAMPLES: Examples and Tutorials"
description: "Example implementations, tutorials, and reference applications"
purpose: "Provide learning resources and reference implementations for GEO-INFER"
module_type: "Documentation"
status: "Stable"
last_updated: "2026-01-26"
dependencies: ["All modules"]
compatibility: ["All GEO-INFER modules"]
tags: ["examples", "tutorials", "learning", "reference", "demos"]
difficulty: "Beginner"
estimated_time: "Variable"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a>
</div>

---

# GEO-INFER-EXAMPLES: Examples and Tutorials

## Overview

**GEO-INFER-EXAMPLES** provides comprehensive learning resources:

- **Tutorials**: Step-by-step learning paths
- **Examples**: Working code examples by domain
- **Demos**: Interactive demonstration applications
- **Use Cases**: Real-world implementation patterns

## Features

### Tutorial Runner

```python
from geo_infer_examples import TutorialRunner

# Run interactive tutorial
runner = TutorialRunner()

tutorial = runner.start(
    topic="active_inference_basics",
    level="beginner",
    interactive=True
)

# Get progress
print(f"Progress: {tutorial.progress}%")
```

### Example Catalog

```python
from geo_infer_examples import ExampleCatalog

# Browse examples
catalog = ExampleCatalog()

# Search by domain
examples = catalog.search(
    domain="urban_planning",
    difficulty="intermediate"
)

# Run example
example = catalog.get("traffic_simulation")
result = example.run()
```

### Demo Applications

```python
from geo_infer_examples.demos import EnvironmentalMonitorDemo

# Run demo application
demo = EnvironmentalMonitorDemo(
    region="bay_area",
    sensors=["air_quality", "temperature"]
)

demo.run(visualize=True)
```

## Example Categories

| Category | Examples |
|----------|----------|
| **Getting Started** | Hello World, Basic Agent, First Map |
| **Active Inference** | Perception, Action, Learning loops |
| **Domain Applications** | Urban, Agriculture, Environment |
| **Multi-Agent** | Swarms, Coordination, Communication |
| **Integration** | APIs, Databases, Cloud deployment |

## Tutorial Tracks

| Track | Duration | Level |
|-------|----------|-------|
| **Quickstart** | 2 hours | Beginner |
| **Agent Development** | 8 hours | Intermediate |
| **Domain Expert** | 16 hours | Advanced |
| **System Architect** | 24 hours | Expert |

## Installation

```bash
uv pip install -e "./GEO-INFER-EXAMPLES"
```

## Running Examples

```bash
# List examples
python -m geo_infer_examples list

# Run specific example
python -m geo_infer_examples run urban_agent

# Start tutorial
python -m geo_infer_examples tutorial --topic basics
```

## Related Documentation

- [GEO-INFER-EDU](../GEO-INFER-EDU/README.md): Educational tools
- [AGENTS.md](./AGENTS.md): Examples capabilities

---

**Status**: Stable - Continuously updated

**Last Updated**: 2026-01-26
