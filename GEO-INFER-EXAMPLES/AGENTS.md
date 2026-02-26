# GEO-INFER-EXAMPLES: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-EXAMPLES** module provides comprehensive examples, tutorials, and reference implementations demonstrating agent capabilities across the entire GEO-INFER framework.

## Agent Capabilities

### 1. Interactive Tutorials

```python
from geo_infer_examples import TutorialRunner

# Initialize tutorial system
runner = TutorialRunner()

# Run an Active Inference tutorial
tutorial = runner.run(
    topic="active_inference_agents",
    level="intermediate",
    interactive=True)

# Get tutorial progress
progress = tutorial.get_progress()
print(f"Completed: {progress.completed}/{progress.total} steps")```

### 2. Example Catalog

```python
from geo_infer_examples import ExampleCatalog

# Browse available examples
catalog = ExampleCatalog()

# Find examples by domain
spatial_examples = catalog.search(
    domain="spatial_analysis",
    difficulty="beginner")

# Run an example
example = catalog.get("urban_planning_agent")
result = example.run()```

### 3. Demo Applications

```python
from geo_infer_examples.demos import EnvironmentalMonitorDemo

# Run environmental monitoring demo
demo = EnvironmentalMonitorDemo(
    region="san_francisco_bay",
    sensors=["air_quality", "temperature", "humidity"])

# Execute demo with visualization
demo.run(visualize=True)```

### 4. Use Case Library

```python
from geo_infer_examples import UseCaseLibrary

# Access domain-specific use cases
library = UseCaseLibrary()

# Get agriculture use cases
ag_cases = library.get_domain("agriculture")

# Run precision farming example
case = ag_cases.get("precision_irrigation")
case.demonstrate()```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Example Catalog** | ✅ Ready | Curated collection of examples |
| **Tutorial Runner** | ✅ Ready | Interactive tutorial system |
| **Demo Applications** | ✅ Ready | Runnable demo applications |
| **Use Case Library** | ✅ Ready | Domain-specific examples |
| **Code Snippets** | ✅ Ready | Copy-paste code examples |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **TutorialGuideAgent** | 🔮 High | AI-powered learning assistance |
| **ExampleGeneratorAgent** | 🔮 Medium | Custom example generation |
| **AdaptiveLearningAgent** | 🔮 Medium | Personalized learning paths |

## Example Categories

### Active Inference Examples

```python
# Quick start Active Inference agent
from geo_infer_examples.active_inference import QuickStartAgent

agent = QuickStartAgent()
agent.demonstrate_perception_action_loop()```

### Multi-Agent Examples

```python
# Multi-agent coordination example
from geo_infer_examples.multi_agent import SwarmDemo

swarm = SwarmDemo(num_agents=10)
swarm.demonstrate_emergent_behavior()```

### Domain-Specific Examples

| Domain | Examples Available |
|--------|-------------------|
| **Agriculture** | Crop monitoring, irrigation, pest detection |
| **Urban Planning** | Traffic flow, land use, infrastructure |
| **Environmental** | Air quality, water monitoring, climate |
| **Emergency** | Disaster response, evacuation, resource allocation |
| **Health** | Disease surveillance, healthcare access |

## Integration with Learning

```mermaid
graph LR
    subgraph Examples
        CAT[Example Catalog]
        TUT[Tutorial Runner]
        DEMO[Demo Apps]
        USE[Use Cases]
    end
    
    subgraph Learning
        USER[User/Developer]
        AGENT[Agent Development]
    end
    
    CAT --> USER
    TUT --> USER
    DEMO --> USER
    USE --> AGENT
    
    USER --> AGENT```

## Running Examples

### Command Line

```bash
# List available examples
python -m geo_infer_examples list

# Run specific example
python -m geo_infer_examples run urban_planning_agent

# Start tutorial
python -m geo_infer_examples tutorial active_inference --level beginner```

### Jupyter Notebooks

```python
# Examples work seamlessly in notebooks
from geo_infer_examples.notebooks import load_notebook

notebook = load_notebook("agent_basics")
notebook.render()```

---

This AGENTS.md documents how GEO-INFER-EXAMPLES provides learning resources and reference implementations for agent development.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
