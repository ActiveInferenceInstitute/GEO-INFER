# GEO-INFER-AGENT Source Code

This directory contains the core implementation of the GEO-INFER-AGENT intelligent agent framework.

## Directory Structure

```
src/
├── geo_infer_agent/
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Command-line interface
│   ├── core/                    # Core agent framework components
│   │   ├── __init__.py
│   │   ├── active_inference.py  # Active Inference agent implementation
│   │   ├── agent_base.py        # Base agent classes
│   │   └── agent_registry.py    # Agent registration and discovery
│   ├── models/                  # Agent architecture implementations
│   │   ├── __init__.py
│   │   ├── bdi.py              # Belief-Desire-Intention agents
│   │   ├── hybrid.py           # Hybrid agent architectures
│   │   ├── README.md           # Model architectures documentation
│   │   ├── rl.py               # Reinforcement Learning agents
│   │   └── rule_based.py       # Rule-based agents
│   ├── api/                    # API interfaces and communication
│   │   ├── __init__.py
│   │   ├── agent_endpoints.py  # REST API endpoints
│   │   ├── interface.py        # Agent interface definitions
│   │   ├── messaging.py        # Inter-agent messaging
│   │   └── telemetry.py        # Agent monitoring and telemetry
│   └── agents/                 # Pre-built agent implementations
│       ├── __init__.py
│       └── data_collector.py   # Data collection agent
```

## Core Components

### Agent Base Classes

**Location**: `core/agent_base.py`

The foundation classes for all agent types in the framework:

```python
from geo_infer_agent.core.agent_base import BaseAgent, AgentLifecycle

class BaseAgent:
    """Base class for all intelligent agents"""

    def __init__(self, agent_id, **kwargs):
        self.agent_id = agent_id
        self.lifecycle = AgentLifecycle.CREATED
        # Initialize agent components

    def perceive(self, observations):
        """Process sensory inputs"""
        raise NotImplementedError

    def decide(self, beliefs):
        """Make decisions based on beliefs"""
        raise NotImplementedError

    def act(self, actions):
        """Execute actions in environment"""
        raise NotImplementedError

    def learn(self, experiences):
        """Learn from experiences"""
        raise NotImplementedError
```

### Agent Registry

**Location**: `core/agent_registry.py`

Manages agent discovery, registration, and coordination:

```python
from geo_infer_agent.core.agent_registry import AgentRegistry

registry = AgentRegistry()
registry.register_agent(my_agent)
discovered_agents = registry.discover_agents(capabilities=['spatial_analysis'])
```

### Active Inference Implementation

**Location**: `core/active_inference.py`

Implements agents based on the Free Energy Principle:

```python
from geo_infer_agent.core.active_inference import ActiveInferenceAgent

agent = ActiveInferenceAgent(
    generative_model=spatial_model,
    precision_parameters={'sensory': 1.0, 'action': 0.8}
)
```

## Agent Models

### BDI Architecture

**Location**: `models/bdi/`

Belief-Desire-Intention agents for rational decision-making:

```python
from geo_infer_agent.models.bdi import BDIAgent

agent = BDIAgent(
    initial_beliefs={'location': 'warehouse', 'inventory': 'low'},
    goals=['maintain_inventory', 'optimize_routes'],
    plans=['reorder_protocol', 'routing_optimization']
)
```

### Reinforcement Learning Agents

**Location**: `models/rl.py`

Agents that learn through interaction with environments:

```python
from geo_infer_agent.models.rl import RLAgent

agent = RLAgent(
    state_space=['position', 'cargo_status'],
    action_space=['move_north', 'move_south', 'deliver'],
    reward_function='delivery_efficiency'
)
```

### Hybrid Agents

**Location**: `models/hybrid.py`

Agents combining multiple reasoning approaches:

```python
from geo_infer_agent.models.hybrid import HybridAgent

agent = HybridAgent(
    components={
        'bdi': BDIAgent(...),
        'rl': RLAgent(...),
        'rule_based': RuleBasedAgent(...)
    },
    integration_strategy='hierarchical'
)
```

## API Layer

### REST Endpoints

**Location**: `api/agent_endpoints.py`

Provides HTTP interfaces for agent management:

```python
from geo_infer_agent.api.agent_endpoints import AgentAPI

api = AgentAPI()
api.register_routes(app)
```

### Messaging System

**Location**: `api/messaging.py`

Handles inter-agent communication:

```python
from geo_infer_agent.api.messaging import AgentMessenger

messenger = AgentMessenger(agent_id='agent_001')
messenger.send_message(recipient='agent_002', content=task_update)
```

### Telemetry and Monitoring

**Location**: `api/telemetry.py`

Collects and reports agent performance metrics:

```python
from geo_infer_agent.api.telemetry import AgentTelemetry

telemetry = AgentTelemetry(agent_id='agent_001')
telemetry.record_metric('task_completion_time', 45.2)
```

## Command Line Interface

**Location**: `cli.py`

Provides command-line tools for agent management:

```bash
# Start an agent
python -m geo_infer_agent.cli start --agent-type bdi --config config.yaml

# List active agents
python -m geo_infer_agent.cli list

# Monitor agent performance
python -m geo_infer_agent.cli monitor --agent-id agent_001
```

## Development Guidelines

### Adding New Agent Types

1. Extend `BaseAgent` class in `core/agent_base.py`
2. Implement required methods: `perceive()`, `decide()`, `act()`, `learn()`
3. Add to appropriate model directory under `models/`
4. Register with agent registry
5. Add tests and documentation

### Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings
- Write unit tests for all new functionality

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific agent tests:
```bash
python -m pytest tests/models/test_bdi.py
```

## Dependencies

Core dependencies are managed through the main GEO-INFER framework. Agent-specific dependencies include:

- `numpy`: Numerical computations
- `scipy`: Scientific computing
- `networkx`: Graph algorithms for agent networks
- `requests`: HTTP communication
- `websockets`: Real-time messaging (optional)

## Integration Points

The agent framework integrates with other GEO-INFER modules:

- **GEO-INFER-SPACE**: Spatial reasoning and navigation
- **GEO-INFER-TIME**: Temporal reasoning and scheduling
- **GEO-INFER-ACT**: Active Inference components
- **GEO-INFER-ANT**: Swarm intelligence coordination
- **GEO-INFER-API**: RESTful interfaces
- **GEO-INFER-COMMS**: Inter-agent communication

