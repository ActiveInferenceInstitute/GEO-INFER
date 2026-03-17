# GEO-INFER-OPS: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./README.md">📚 Module Documentation</a>
</div>

---

## Overview

The **GEO-INFER-OPS** module provides operational capabilities for running GEO-INFER components, including orchestration, deployment management, configuration, logging/monitoring setup, and health checks.

## Agent Capabilities

### 1. Agent Deployment

```python
from geo_infer_ops import DeploymentManager

# Deploy agents to production
deployer = DeploymentManager()

result = deployer.deploy(
    config={"agent_spec": agent_spec},
    environment="kubernetes",
)

print(result)```

### 2. Health Monitoring

```python
import asyncio

from geo_infer_ops import HealthChecker

# Monitor agent health
monitor = HealthChecker()

health = asyncio.run(monitor.run_all_checks())
print(health)```

### 3. Orchestration

```python
from geo_infer_ops import Orchestrator, Task

orchestrator = Orchestrator()
orchestrator.submit(Task(name="example_task", payload={"step": "noop"}))
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **Deployment** | ✅ Ready | Deployment manager facade |
| **Health Monitoring** | ✅ Ready | Health checks and status reporting |
| **Orchestration** | ✅ Ready | Task orchestration primitives |

### Aspirational/Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **SREAgent** | 🔮 High | Autonomous incident response |
| **CostOptimizer** | 🔮 Medium | Resource cost optimization |
| **ChaosAgent** | 🔮 Medium | Chaos engineering tests |

## Use Cases

### Production Agent Management

```python
from geo_infer_ops import ProductionManager

manager = ProductionManager(cluster="prod-west")

# Rolling update
manager.rolling_update(
    agent_type="spatial_agent",
    new_version="2.1.0",
    strategy="blue_green")

# Get deployment status
status = manager.get_status()```

---

This AGENTS.md documents how GEO-INFER-OPS provides operational capabilities for agents.

**Last Updated**: 2026-02-25

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
