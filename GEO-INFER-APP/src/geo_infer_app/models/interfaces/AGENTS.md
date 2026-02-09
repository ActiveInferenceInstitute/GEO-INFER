# Agent
: interfaces

## Scope
 This directory contains interfaces components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### BDIAgentInterface
 Implementation of AgentInterface for BDI agents.

**Methods**:
- `get_agent_state(agent_id: str) -> AgentState`: Retrieve the current state of the specified agent.
- `list_agents(filter_params: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]`: List all available BDI agents, with optional filtering.
- `send_command(agent_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]`: Send a command to a BDI agent.
- `register_event_handler(event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None`: Register a callback function to handle agent events.
- `create_agent(agent_type: AgentType, config: Dict[str, Any]) -> str`: Create a BDI agent instance.

### BDIAgent

**Methods**:
- `update_beliefs(beliefs)`:
- `add_desire(desire)`:
- `deliberate()`:
- `execute()`:

### BeliefBase

### DesireSet

### IntentionStructure

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `src/geo_infer_app/models/interfaces`
- **Type**: Directory Node
