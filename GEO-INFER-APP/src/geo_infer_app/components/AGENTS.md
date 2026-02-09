# Agent
: components

## Scope
 This directory contains components components for the module. It provides 2 classes and 0 functions.

## Classes
 and Functions

### AgentWidget
 Widget for displaying and interacting with agents.

**Methods**:
- `register_status_callback(callback: Callable[[str], None]) -> None`: Register a callback for widget status changes.
- `unregister_status_callback(callback: Callable[[str], None]) -> bool`: Unregister a status callback.

### WebAgentWidget
 Web-specific implementation of the agent widget.

**Methods**:
- `render() -> str`: Render the widget as HTML.
- `get_javascript() -> str`: Get JavaScript code for widget functionality.

## Capabilities

- **2 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-APP/src/geo_infer_app/components`
- **Type**: Directory Node
