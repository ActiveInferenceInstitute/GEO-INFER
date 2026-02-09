# Agent
: models

## Scope
 This directory contains models components for the module. It provides 11 classes and 0 functions.

## Classes
 and Functions

### ConfigFieldType
 Enumeration of supported configuration field types.

### ConfigField
 Definition of a configuration field for agent configuration.

### AgentConfigSchema
 Schema for agent configuration.

### AgentConfiguration
 Class for managing agent configurations.

**Methods**:
- `register_schema(cls, schema: AgentConfigSchema) -> None`: Register a configuration schema for an agent type.
- `get_schema(cls, agent_type: AgentType) -> AgentConfigSchema`: Get the configuration schema for the specified agent type.
- `validate_config(cls, agent_type: AgentType, config: Dict[str, Any]) -> List[str]`: Validate a configuration against the schema for the specified agent type.
- `get_default_config(cls, agent_type: AgentType) -> Dict[str, Any]`: Get a default configuration for the specified agent type.

### AgentFactory
 Factory class for creating agent interfaces.

**Methods**:
- `register_interface(cls, agent_type: AgentType, interface_class: Type[AgentInterface]) -> None`: Register an agent interface implementation for a specific agent type.
- `create_interface(cls, agent_type: AgentType, config: Optional[Dict[str, Any]]) -> AgentInterface`: Create an agent interface instance for the specified agent type.
- `get_available_agent_types(cls) -> Dict[str, str]`: Get a dictionary of available agent types.

### AgentType
 Enumeration of supported agent types matching GEO-INFER-AGENT implementations.

### AgentState
 Represents the current state of an agent for UI representation.

### AgentInterface
 Abstract base class for all agent interfaces in the application.

**Methods**:
- `get_agent_state(agent_id: str) -> AgentState`: Retrieve the current state of the specified agent.
- `list_agents(filter_params: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]`: List all available agents, with optional filtering.
- `send_command(agent_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]`: Send a command to an agent.
- `register_event_handler(event_type: str, callback: Callable[[Dict[str, Any]], None]) -> None`: Register a callback function to handle agent events.
- `create_agent(agent_type: AgentType, config: Dict[str, Any]) -> str`: Create a agent instance.

### VisualizationType
 Enumeration of supported visualization types for agents.

### VisualizationConfig
 Configuration for agent visualization.

### AgentVisualization
 Class for converting agent states into visualization-friendly formats.

**Methods**:
- `get_default_config(agent_type: AgentType) -> Dict[str, VisualizationConfig]`: Get default visualization configurations for the specified agent type.
- `state_to_map_feature(agent_state: AgentState) -> Dict[str, Any]`: Convert an agent state to a map feature representation.
- `state_to_dashboard_data(agent_state: AgentState) -> Dict[str, Any]`: Convert an agent state to dashboard data.

## Capabilities

- **11 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-APP/src/geo_infer_app/models`
- **Type**: Directory Node
