# Agent
: api

## Scope
 This directory contains api components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### AgentAPIClient
 Client for interacting with GEO-INFER-AGENT.

**Methods**:
- `register_status_callback(agent_id: str, callback: Callable[[str, str], None]) -> None`: Register a callback for agent status changes.
- `unregister_status_callback(agent_id: str, callback: Callable[[str, str], None]) -> bool`: Unregister a status callback.

### AgentManager
 High-level manager for agents in the application.

**Methods**:
- `register_status_callback(agent_id: str, callback: Callable[[str, str], None]) -> None`: Register a callback for agent status changes.
- `unregister_status_callback(agent_id: str, callback: Callable[[str, str], None]) -> bool`: Unregister a status callback.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-APP/src/geo_infer_app/api`
- **Type**: Directory Node
