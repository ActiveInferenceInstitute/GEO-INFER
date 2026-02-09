# Agent
: api

## Scope
 This directory contains api components for the module. It provides 7 classes and 4 functions.

## Classes
 and Functions

### CommunicationAPI
 REST API server for geospatial communication system.

**Methods**:
- `start_server() -> None`: Start the API server.
- `get_app() -> FastAPI`: Get the FastAPI application instance.

### WebSocketManager
 WebSocket connection manager for real-time communication.

**Methods**:
- `broadcast_message(message: Dict[str, Any]) -> None`: Broadcast a message to all connected clients.
- `get_connection_count() -> int`: Get the number of active connections.
- `get_connection_stats() -> Dict[str, Any]`: Get WebSocket connection statistics.

### WebSocketConnection
 WebSocket connection wrapper with geospatial capabilities.

### WebSocketServer
 WebSocket server for real-time communication.

**Methods**:
- `get_stats() -> Dict[str, Any]`: Get WebSocket server statistics.
- `broadcast_system_message(message: Dict[str, Any]) -> None`: Broadcast a system message to all connected clients.

### GeospatialWebSocketHandler
 geospatial WebSocket handler with spatial filtering.

**Methods**:
- `add_spatial_filter(connection_id: str, filter_config: Dict[str, Any]) -> None`: Add a spatial filter for a WebSocket connection.
- `remove_spatial_filter(connection_id: str) -> None`: Remove spatial filter for a WebSocket connection.
- `should_receive_message(connection_id: str, message: MessageResponse) -> bool`: Check if connection should receive a message based on spatial filters.

### RealTimeMessageBroadcaster
 Real-time message broadcaster for WebSocket connections.

**Methods**:
- `broadcast_message(message: MessageResponse) -> None`: Broadcast a message to appropriate WebSocket connections.

### WebSocketAPIManager
 WebSocket API manager.

**Methods**:
- `get_stats() -> Dict[str, Any]`: Get WebSocket API statistics.

### create_api_server
 `create_api_server(system: GeospatialCommunicationSystem, config: Optional[Dict[str, Any]]) -> CommunicationAPI` Create and configure a communication API server.

### broadcast_message_callback
 `broadcast_message_callback(message: MessageResponse) -> None`

### broadcast_event_callback
 `broadcast_event_callback(event: EventPublishResponse) -> None`

### broadcast_notification_callback
 `broadcast_notification_callback(notification: NotificationResponse) -> None`

## Capabilities

- **7 classes** for core functionality
- **4 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-COMMS/src/geo_infer_comms/api`
- **Type**: Directory Node
