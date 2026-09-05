"""
Data models for GEO-INFER-COMMS.

This module contains comprehensive data models for messages, channels,
notifications, events, and spatial data with full geospatial support.
"""

from geo_infer_comms.models.message import (
    MessageRequest, MessageResponse, MessageStatus as MessageStatus, ChannelRequest, ChannelResponse, ChannelType,
    NotificationRequest, NotificationResponse, NotificationType,
    EventPublishRequest, EventPublishResponse, CollaborationSessionRequest,
    CollaborationSessionResponse, StreamRequest, StreamResponse,
    BroadcastRequest, BroadcastResponse, SubscriptionRequest,
    SubscriptionResponse, MessageListResponse, ChannelListResponse,
    NotificationListResponse, CollaborationSessionListResponse,
    StreamListResponse, HealthResponse, Error, Participant,
    ParticipantRole as ParticipantRole, ParticipantStatus as ParticipantStatus, MessageMetadata as MessageMetadata,
    MessagePriority, MessageType
)
from geo_infer_comms.models.spatial import (
    GeospatialPoint, GeospatialBounds, GeospatialMetadata,
    SpatialFilter, SpatialIndex, CoordinateSystem,
    calculate_distance, create_bounds_from_points, buffer_point,
    validate_geojson_geometry, geojson_to_geospatial_point,
    geospatial_point_to_geojson
)

__all__ = [
    "MessageRequest", "MessageResponse", "MessagePriority", "MessageType",
    "ChannelRequest", "ChannelResponse", "ChannelType",
    "NotificationRequest", "NotificationResponse", "NotificationType",
    "EventPublishRequest", "EventPublishResponse",
    "CollaborationSessionRequest", "CollaborationSessionResponse",
    "StreamRequest", "StreamResponse", "BroadcastRequest", "BroadcastResponse",
    "SubscriptionRequest", "SubscriptionResponse", "Participant",
    "MessageListResponse", "ChannelListResponse", "NotificationListResponse",
    "CollaborationSessionListResponse", "StreamListResponse",
    "HealthResponse", "Error", "MessageMetadata",
    "GeospatialPoint", "GeospatialBounds", "GeospatialMetadata",
    "SpatialFilter", "SpatialIndex", "CoordinateSystem",
    "calculate_distance", "create_bounds_from_points", "buffer_point",
    "validate_geojson_geometry",
    "geojson_to_geospatial_point", "geospatial_point_to_geojson"
]
