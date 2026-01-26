# api
 ## Overview
 This directory contains api components. It includes 2 Python modules. ## Components
 ### rest_ap
i
.py REST API implementation for GEO-INFER-COMMS. **Classes**: `CommunicationAPI` **Functions**: `create_api_server` ### websocket_ap
i
.py WebSocket API implementation for GEO-INFER-COMMS. **Classes**: `WebSocketManager`, `WebSocketConnection`, `WebSocketServer`, `GeospatialWebSocketHandler`, `RealTimeMessageBroadcaster`, `WebSocketAPIManager` **Functions**: `broadcast_message_callback`, `broadcast_event_callback`, `broadcast_notification_callback` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 