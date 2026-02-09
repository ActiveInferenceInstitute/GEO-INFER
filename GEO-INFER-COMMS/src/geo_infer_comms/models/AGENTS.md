# Agent
: models

## Scope
 This directory contains models components for the module. It provides 48 classes and 8 functions.

## Classes
 and Functions

### MessagePriority
 Message priority levels for routing and processing.

### MessageType
 Types of messages supported in the system.

### MessageStatus
 Status of message delivery and processing.

### ChannelType
 Types of communication channels.

### ChannelStatus
 Status of communication channels.

### NotificationType
 Types of notifications.

### NotificationStatus
 Status of notifications.

### EventType
 Types of events in the system.

### CollaborationType
 Types of collaboration sessions.

### ParticipantRole
 Roles of participants in collaboration.

### ParticipantStatus
 Status of participants in collaboration.

### MessageMetadata
 Metadata associated with messages.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert metadata to dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> MessageMetadata`: Create metadata from dictionary.

### MessageRequest
 Request model for creating a message.

### MessageResponse
 Response model for message data.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert message to dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> MessageResponse`: Create message from dictionary.

### BroadcastRequest
 Request model for broadcasting messages.

### BroadcastResponse
 Response model for broadcast operations.

### ChannelRequest
 Request model for creating channels.

### ChannelResponse
 Response model for channel data.

### SubscriptionRequest
 Request model for channel subscriptions.

### SubscriptionResponse
 Response model for subscription data.

### NotificationRequest
 Request model for creating notifications.

### NotificationResponse
 Response model for notification data.

### EventPublishRequest
 Request model for publishing events.

### EventPublishResponse
 Response model for event publishing.

### EventSubscriptionRequest
 Request model for event subscriptions.

### EventSubscriptionResponse
 Response model for event subscriptions.

### CollaborationSessionRequest
 Request model for creating collaboration sessions.

### Participant
 Model for collaboration participants.

### CollaborationSessionResponse
 Response model for collaboration sessions.

### JoinSessionResponse
 Response model for joining collaboration sessions.

### StreamRequest
 Request model for creating data streams.

### StreamResponse
 Response model for data streams.

### WebSocketInfoResponse
 Response model for WebSocket connection information.

### MessageListResponse
 Response model for message lists.

### ChannelListResponse
 Response model for channel lists.

### NotificationListResponse
 Response model for notification lists.

### CollaborationSessionListResponse
 Response model for collaboration session lists.

### StreamListResponse
 Response model for stream lists.

### HealthResponse
 Response model for health checks.

### Error
 Error response model.

### Config
 Pydantic configuration.

### Config
 Pydantic configuration.

### CoordinateSystem
 Supported coordinate reference systems.

### GeospatialPoint
 Represents a geospatial point with coordinates and metadata.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert point to dictionary representation.
- `from_dict(cls, data: Dict[str, Any]) -> GeospatialPoint`: Create point from dictionary.
- `distance_to(other: GeospatialPoint, method: str) -> float`: Calculate distance to another point in meters.
- `is_within_bounds(bounds: GeospatialBounds) -> bool`: Check if point is within given bounds.

### GeospatialBounds
 Represents geospatial bounding box or area.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert bounds to dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> GeospatialBounds`: Create bounds from dictionary.
- `contains_point(point: GeospatialPoint) -> bool`: Check if point is within these bounds.
- `intersects(other: GeospatialBounds) -> bool`: Check if these bounds intersect with another bounds.
- `area() -> float`: Calculate approximate area in square meters.
- `center() -> GeospatialPoint`: Get center point of bounds.

### GeospatialMetadata
 geospatial metadata for messages and data.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert geospatial metadata to dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> GeospatialMetadata`: Create geospatial metadata from dictionary.
- `distance_to(other: GeospatialMetadata) -> float`: Calculate distance between two geospatial metadata objects.
- `is_within_distance(other: GeospatialMetadata, distance_meters: float) -> bool`: Check if this location is within distance of another.

### SpatialFilter
 Represents a spatial filter for message routing and filtering.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert filter to dictionary.
- `from_dict(cls, data: Dict[str, Any]) -> SpatialFilter`: Create filter from dictionary.
- `matches_location(location: GeospatialPoint) -> bool`: Check if location matches this spatial filter.

### SpatialIndex
 Spatial indexing for efficient geospatial queries.

**Methods**:
- `insert(location: GeospatialPoint, data_id: str) -> None`: Insert location-data mapping into spatial index.
- `query(filter_obj: SpatialFilter) -> List[str]`: Query spatial index for data matching filter.
- `remove(location: GeospatialPoint, data_id: str) -> None`: Remove data from spatial index.
- `clear() -> None`: Clear all data from spatial index.

### message_request_to_response
 `message_request_to_response(request: MessageRequest, sender_id: str) -> MessageResponse` Convert message request to response model.

### validate_geospatial_bounds
 `validate_geospatial_bounds(bounds: Dict[str, Any]) -> bool` Validate geospatial bounds for channels and filters.

### calculate_distance
 `calculate_distance(point1: GeospatialPoint, point2: GeospatialPoint) -> float` Calculate distance between two points in meters.

### create_bounds_from_points
 `create_bounds_from_points(points: List[GeospatialPoint]) -> GeospatialBounds` Create bounding box from list of points.

### buffer_point
 `buffer_point(point: GeospatialPoint, distance_meters: float) -> GeospatialBounds` Create a bounding box buffer around a point.

### validate_geojson_geometry
 `validate_geojson_geometry(geometry: Dict[str, Any]) -> bool` Validate GeoJSON geometry structure.

### geojson_to_geospatial_point
 `geojson_to_geospatial_point(geojson: Dict[str, Any]) -> GeospatialPoint` Convert GeoJSON Point to GeospatialPoint.

### geospatial_point_to_geojson
 `geospatial_point_to_geojson(point: GeospatialPoint) -> Dict[str, Any]` Convert GeospatialPoint to GeoJSON Point.

## Capabilities

- **48 classes** for core functionality
- **8 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-COMMS/src/geo_infer_comms/models`
- **Type**: Directory Node
