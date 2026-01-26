# Agent
: models ## Scope
 This directory contains models components for the module. It provides 48 classes and 8 functions. ## Classes
 and Functions ### MessagePriorit
y
 Message priority levels for routing and processing. ### MessageTyp
e
 Types of messages supported in the system. ### MessageStatu
s
 Status of message delivery and processing. ### ChannelTyp
e
 Types of communication channels. ### ChannelStatu
s
 Status of communication channels. ### NotificationTyp
e
 Types of notifications. ### NotificationStatu
s
 Status of notifications. ### EventTyp
e
 Types of events in the system. ### CollaborationTyp
e
 Types of collaboration sessions. ### ParticipantRol
e
 Roles of participants in collaboration. ### ParticipantStatu
s
 Status of participants in collaboration. ### MessageMetadat
a
 Metadata associated with messages. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert metadata to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> MessageMetadata`: Create metadata from dictionary. ### MessageReques
t
 Request model for creating a message. ### MessageRespons
e
 Response model for message data. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert message to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> MessageResponse`: Create message from dictionary. ### BroadcastReques
t
 Request model for broadcasting messages. ### BroadcastRespons
e
 Response model for broadcast operations. ### ChannelReques
t
 Request model for creating channels. ### ChannelRespons
e
 Response model for channel data. ### SubscriptionReques
t
 Request model for channel subscriptions. ### SubscriptionRespons
e
 Response model for subscription data. ### NotificationReques
t
 Request model for creating notifications. ### NotificationRespons
e
 Response model for notification data. ### EventPublishReques
t
 Request model for publishing events. ### EventPublishRespons
e
 Response model for event publishing. ### EventSubscriptionReques
t
 Request model for event subscriptions. ### EventSubscriptionRespons
e
 Response model for event subscriptions. ### CollaborationSessionReques
t
 Request model for creating collaboration sessions. ### Participan
t
 Model for collaboration participants. ### CollaborationSessionRespons
e
 Response model for collaboration sessions. ### JoinSessionRespons
e
 Response model for joining collaboration sessions. ### StreamReques
t
 Request model for creating data streams. ### StreamRespons
e
 Response model for data streams. ### WebSocketInfoRespons
e
 Response model for WebSocket connection information. ### MessageListRespons
e
 Response model for message lists. ### ChannelListRespons
e
 Response model for channel lists. ### NotificationListRespons
e
 Response model for notification lists. ### CollaborationSessionListRespons
e
 Response model for collaboration session lists. ### StreamListRespons
e
 Response model for stream lists. ### HealthRespons
e
 Response model for health checks. ### Erro
r
 Error response model. ### Confi
g
 Pydantic configuration. ### Confi
g
 Pydantic configuration. ### CoordinateSyste
m
 Supported coordinate reference systems. ### GeospatialPoin
t
 Represents a geospatial point with coordinates and metadata. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert point to dictionary representation. - `from_dict(cls, data: Dict[str, Any]) -> GeospatialPoint`: Create point from dictionary. - `distance_to(other: GeospatialPoint, method: str) -> float`: Calculate distance to another point in meters. - `is_within_bounds(bounds: GeospatialBounds) -> bool`: Check if point is within given bounds. ### GeospatialBound
s
 Represents geospatial bounding box or area. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert bounds to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> GeospatialBounds`: Create bounds from dictionary. - `contains_point(point: GeospatialPoint) -> bool`: Check if point is within these bounds. - `intersects(other: GeospatialBounds) -> bool`: Check if these bounds intersect with another bounds. - `area() -> float`: Calculate approximate area in square meters. - `center() -> GeospatialPoint`: Get center point of bounds. ### GeospatialMetadat
a
 geospatial metadata for messages and data. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert geospatial metadata to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> GeospatialMetadata`: Create geospatial metadata from dictionary. - `distance_to(other: GeospatialMetadata) -> float`: Calculate distance between two geospatial metadata objects. - `is_within_distance(other: GeospatialMetadata, distance_meters: float) -> bool`: Check if this location is within distance of another. ### SpatialFilte
r
 Represents a spatial filter for message routing and filtering. **Methods**: - `to_dict() -> Dict[str, Any]`: Convert filter to dictionary. - `from_dict(cls, data: Dict[str, Any]) -> SpatialFilter`: Create filter from dictionary. - `matches_location(location: GeospatialPoint) -> bool`: Check if location matches this spatial filter. ### SpatialInde
x
 Spatial indexing for efficient geospatial queries. **Methods**: - `insert(location: GeospatialPoint, data_id: str) -> None`: Insert location-data mapping into spatial index. - `query(filter_obj: SpatialFilter) -> List[str]`: Query spatial index for data matching filter. - `remove(location: GeospatialPoint, data_id: str) -> None`: Remove data from spatial index. - `clear() -> None`: Clear all data from spatial index. ### message_request_to_respons
e
 `message_request_to_response(request: MessageRequest, sender_id: str) -> MessageResponse` Convert message request to response model. ### validate_geospatial_bound
s
 `validate_geospatial_bounds(bounds: Dict[str, Any]) -> bool` Validate geospatial bounds for channels and filters. ### calculate_distanc
e
 `calculate_distance(point1: GeospatialPoint, point2: GeospatialPoint) -> float` Calculate distance between two points in meters. ### create_bounds_from_point
s
 `create_bounds_from_points(points: List[GeospatialPoint]) -> GeospatialBounds` Create bounding box from list of points. ### buffer_poin
t
 `buffer_point(point: GeospatialPoint, distance_meters: float) -> GeospatialBounds` Create a bounding box buffer around a point. ### validate_geojson_geometr
y
 `validate_geojson_geometry(geometry: Dict[str, Any]) -> bool` Validate GeoJSON geometry structure. ### geojson_to_geospatial_poin
t
 `geojson_to_geospatial_point(geojson: Dict[str, Any]) -> GeospatialPoint` Convert GeoJSON Point to GeospatialPoint. ### geospatial_point_to_geojso
n
 `geospatial_point_to_geojson(point: GeospatialPoint) -> Dict[str, Any]` Convert GeospatialPoint to GeoJSON Point. ## Capabilities
 - **48 classes** for core functionality - **8 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-COMMS/src/geo_infer_comms/models` - **Type**: Directory Node 