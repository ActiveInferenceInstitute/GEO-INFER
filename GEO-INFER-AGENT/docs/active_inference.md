# Active Inference for Agents

## Introduction

This document describes how Active Inference is implemented in the GEO-INFER agent framework, enabling autonomous agents that perceive, act, and learn in geospatial environments.

## Agent Architecture

### Core Components

An Active Inference agent consists of:

1. **Generative Model**: Internal model of how the world works
2. **Belief State**: Current beliefs about hidden states
3. **Policy Evaluator**: Selects actions via expected free energy
4. **Learning Module**: Updates model parameters

```python
class ActiveInferenceAgent:
    def __init__(self, generative_model):
        self.model = generative_model
        self.beliefs = initialize_beliefs()
        self.policy_evaluator = PolicyEvaluator(self.model)
        self.learner = ModelLearner(self.model)
```

## The Perception-Action Loop

### 1. Observation

Agent receives sensory input from environment:

```python
observation = environment.observe(agent.location)
```

### 2. Belief Update (Perception)

Update beliefs to minimize variational free energy:

```python
agent.beliefs = agent.model.infer_states(
    observation=observation,
    prior=agent.beliefs
)
```

### 3. Policy Evaluation

Evaluate policies by computing expected free energy:

```python
G = []
for policy in agent.policies:
    efe = agent.policy_evaluator.expected_free_energy(
        beliefs=agent.beliefs,
        policy=policy
    )
    G.append(efe)
```

### 4. Action Selection

Select action from best policy:

```python
policy_probs = softmax(-precision * G)
selected_policy = sample(policies, policy_probs)
action = selected_policy[0]
```

### 5. Learning

Update model from experience:

```python
agent.learner.update(
    observation=observation,
    beliefs=agent.beliefs,
    action=action
)
```

## Geospatial Agent Types

### Survey Agent

```python
from geo_infer_agent import SurveyAgent

agent = SurveyAgent(
    region=study_area,
    sensors=["camera", "lidar"],
    goal="complete_coverage"
)
```

### Monitoring Agent

```python
from geo_infer_agent import MonitoringAgent

agent = MonitoringAgent(
    target="air_quality",
    threshold=50,  # alert level
    update_rate=60  # seconds
)
```

### Coordination Agent

```python
from geo_infer_agent import CoordinationAgent

coordinator = CoordinationAgent(
    subordinates=[agent1, agent2],
    objective="maximize_coverage"
)
```

## Multi-Agent Systems

### Decentralized Coordination

Multiple agents share beliefs and coordinate:

```python
swarm = AgentSwarm(agents=[a1, a2, a3])

# Agents share observations
swarm.share_beliefs()

# Coordinate actions to avoid overlap
swarm.coordinate_actions()
```

## Integration with GEO-INFER

| Module | Agent Integration |
|--------|-------------------|
| **GEO-INFER-ACT** | Core inference |
| **GEO-INFER-SPACE** | Spatial states |
| **GEO-INFER-IOT** | Sensor data |
| **GEO-INFER-COMMS** | Agent messaging |

---

**Last Updated**: 2026-01-26
