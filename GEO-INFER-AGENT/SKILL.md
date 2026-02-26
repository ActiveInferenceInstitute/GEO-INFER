---
name: geo-infer-agent
description: Multi-agent geospatial systems with Active Inference. Use when building spatial agents, implementing perception-action loops, managing agent telemetry, or coordinating multi-agent spatial exploration.
prerequisites:
  required:
    - geo-infer-act
    - geo-infer-space
  recommended:
    - geo-infer-ai
    - geo-infer-time
difficulty: advanced
estimated_time: 60min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-AGENT

## Instructions

### Core Capabilities

- **Agent base**: Transport pattern for agent communication
- **Active Inference**: Agent-level free energy minimization
- **Telemetry**: JSON snapshot + per-agent metrics tracking
- **Coordination**: Message passing, shared beliefs, swarm protocols
- **Rule-based**: Decision-tree agents for simple spatial tasks

### Key Imports

```python
from geo_infer_agent.core.agent_base import GeoAgent
from geo_infer_agent.core.active_inference import ActiveInferenceAgent
from geo_infer_agent.core.telemetry import AgentTelemetry
from geo_infer_agent.models.rule_based import RuleBasedAgent
```

## Examples

```python
from geo_infer_agent.core.agent_base import GeoAgent
from geo_infer_agent.core.telemetry import AgentTelemetry

agent = GeoAgent(agent_id="explorer_01", position=(45.5, -122.6))
telemetry = AgentTelemetry(agent)

# Perception-action loop
observation = agent.perceive(environment_state)
action = agent.decide(observation)
agent.act(action)

# Snapshot telemetry as JSON
snapshot = telemetry.snapshot()
print(f"Steps: {snapshot['total_steps']}, Position: {snapshot['position']}")
```

```python
from geo_infer_agent.core.active_inference import ActiveInferenceAgent
import numpy as np

ai_agent = ActiveInferenceAgent(n_states=8, n_observations=5, n_actions=4)
obs = np.random.dirichlet(np.ones(5))
action = ai_agent.act(obs)
print(f"Selected action: {action}, Free energy: {ai_agent.free_energy:.4f}")
```

## Guidelines

- Telemetry uses JSON snapshots and per-agent metrics (not TODOs)
- Agent base uses transport pattern for communication
- Test: `uv run python -m pytest GEO-INFER-AGENT/tests/ -v`

### Integrations

- **ACT** → Active Inference agent decision-making
- **SIM** → Multi-agent simulation environments
- **ANT** → Swarm intelligence coordination
- **SPACE** → Spatial state representation for agents
- **APP** → Agent configuration and control widgets
- **OPS** → Agent telemetry monitoring
