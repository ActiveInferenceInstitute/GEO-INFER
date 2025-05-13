# GEO-INFER-AGENT Models

This package provides different agent architectures and modeling approaches for the GEO-INFER-AGENT module.

## Overview

The models package implements several agent architectures:

- **BDI (Belief-Desire-Intention)**: Models agents based on beliefs about the world, desires (goals), and intentions (plans).
- **Active Inference**: Based on the free energy principle, these agents perceive and act to minimize surprise.
- **Reinforcement Learning**: Agents learn optimal behavior through trial and error with rewards.
- **Rule-Based**: Simple condition-action rules for reactive behavior.
- **Hybrid**: Combines multiple architectures to leverage the strengths of each approach.

## Modules

### BDI Module (`bdi.py`)

The BDI module implements agents based on the Belief-Desire-Intention architecture:

- `Belief`: Represents what the agent believes about the world
- `Desire`: Represents goals the agent wants to achieve
- `Plan`: Represents a sequence of actions designed to satisfy a desire
- `BDIState`: Maintains the agent's beliefs, desires, and intentions
- `BDIAgent`: Implementation of the BDI agent lifecycle

### Active Inference Module (`active_inference.py`)

The Active Inference module implements agents based on the Free Energy Principle:

- `GenerativeModel`: Internal model of how observations are generated
- `ActiveInferenceState`: Maintains the generative model and agent state
- `ActiveInferenceAgent`: Implementation of the active inference agent lifecycle

### Reinforcement Learning Module (`rl.py`)

The RL module implements agents that learn through rewards:

- `Experience`: Represents a single experience tuple (s, a, r, s', done)
- `QTable`: Table of state-action values for tabular Q-learning
- `ReplayBuffer`: Buffer for experience replay
- `RLState`: Maintains the agent's learning state
- `RLAgent`: Implementation of the RL agent lifecycle

### Rule-Based Module (`rule_based.py`)

The Rule-Based module implements agents based on simple condition-action rules:

- `Rule`: Represents a single condition-action rule
- `RuleSet`: Collection of rules with management functionality
- `RuleBasedState`: Maintains the agent's rules and facts
- `RuleBasedAgent`: Implementation of the rule-based agent lifecycle

### Hybrid Module (`hybrid.py`)

The Hybrid module implements agents that combine multiple architectures:

- `SubAgentWrapper`: Wrapper for a sub-agent with metadata
- `HybridState`: Maintains the shared context and sub-agents
- `HybridAgent`: Implementation of the hybrid agent lifecycle

## Usage

To use these agent models, import them from the `geo_infer_agent.models` package:

```python
from geo_infer_agent.models import BDIAgent, ActiveInferenceAgent, RLAgent, RuleBasedAgent, HybridAgent
```

### Basic Example

```python
import asyncio
from geo_infer_agent.models import BDIAgent

async def main():
    # Create a BDI agent
    agent = BDIAgent(agent_id="example_agent", config={
        "name": "Example Agent",
        "initial_beliefs": [
            {"name": "location", "value": {"x": 0, "y": 0}}
        ],
        "initial_desires": [
            {
                "name": "explore", 
                "description": "Explore the environment",
                "priority": 0.8
            }
        ]
    })
    
    # Initialize agent
    await agent.initialize()
    
    # Run agent cycle
    perceptions = await agent.perceive()
    decision = await agent.decide()
    
    if decision:
        result = await agent.act(decision)
    
    # Shutdown agent
    await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Agent Configuration

Agents can be configured using a dictionary that specifies their parameters:

```python
config = {
    "name": "Example Agent",
    # Agent-specific configuration...
}

agent = BDIAgent(agent_id="example_agent", config=config)
```

See the `schemas/agent_schema.json` file for a complete description of the configuration options for each agent type.

## Integration with GEO-INFER-APP

These agent models can be integrated with the GEO-INFER-APP module using the `agent_api.py` module in the GEO-INFER-APP package.

```python
from geo_infer_app.api.agent_api import AgentManager

async def example():
    # Create agent manager
    manager = AgentManager()
    await manager.initialize()
    
    # Create an agent
    agent_id = await manager.create_agent(
        agent_type="bdi",
        name="Map Explorer",
        config={
            "initial_beliefs": [
                {"name": "map_loaded", "value": True}
            ],
            "initial_desires": [
                {"name": "explore_map", "description": "Explore the map", "priority": 0.9}
            ]
        }
    )
    
    # Start the agent
    await manager.start_agent(agent_id)
    
    # Send a command to the agent
    result = await manager.send_command(
        agent_id,
        command_type="query",
        parameters={"query_type": "beliefs"}
    )
    
    # Shutdown
    await manager.shutdown()
```

## Extensions

The models in this package can be extended to create specialized geospatial agents:

1. Subclass the base agent class
2. Override the necessary methods (e.g., `perceive`, `decide`, `act`)
3. Register custom action and perception handlers

```python
from geo_infer_agent.models import BDIAgent

class GeospatialBDIAgent(BDIAgent):
    """Specialized BDI agent for geospatial applications."""
    
    async def initialize(self):
        await super().initialize()
        # Register custom handlers
        self.register_action_handler("spatial_query", self._handle_spatial_query)
    
    async def _handle_spatial_query(self, agent, action):
        # Handle spatial queries
        # ...
        return {"status": "success", "results": [...]}
``` 