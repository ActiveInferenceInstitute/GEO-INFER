# models
 ## Overview
 This directory contains models components. It includes 2 Python modules. ## Components
 ### messag
e
.py Geospatial message data models for the GEO-INFER-COMMS module. **Classes**: `MessagePriority`, `MessageType`, `MessageStatus`, `ChannelType`, `ChannelStatus`, `NotificationType`, `NotificationStatus`, `EventType`, `CollaborationType`, `ParticipantRole`, `ParticipantStatus`, `MessageMetadata`, `MessageRequest`, `MessageResponse`, `BroadcastRequest`, `BroadcastResponse`, `ChannelRequest`, `ChannelResponse`, `SubscriptionRequest`, `SubscriptionResponse`, `NotificationRequest`, `NotificationResponse`, `EventPublishRequest`, `EventPublishResponse`, `EventSubscriptionRequest`, `EventSubscriptionResponse`, `CollaborationSessionRequest`, `Participant`, `CollaborationSessionResponse`, `JoinSessionResponse`, `StreamRequest`, `StreamResponse`, `WebSocketInfoResponse`, `MessageListResponse`, `ChannelListResponse`, `NotificationListResponse`, `CollaborationSessionListResponse`, `StreamListResponse`, `HealthResponse`, `Error`, `Config`, `Config` **Functions**: `message_request_to_response`, `validate_geospatial_bounds` ### spatia
l
.py Geospatial metadata and spatial data models for GEO-INFER-COMMS. **Classes**: `CoordinateSystem`, `GeospatialPoint`, `GeospatialBounds`, `GeospatialMetadata`, `SpatialFilter`, `SpatialIndex` **Functions**: `calculate_distance`, `create_bounds_from_points`, `buffer_point`, `validate_geojson_geometry`, `geojson_to_geospatial_point`, `geospatial_point_to_geojson` ## Usage
 See individual component documentation for usage examples. ## Integration
 This directory integrates with other module components and may be used by higher-level modules. 