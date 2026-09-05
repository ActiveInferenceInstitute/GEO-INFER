"""
Geospatial message data models for the GEO-INFER-COMMS module.

This module defines comprehensive data models for messages, channels, notifications,
and collaboration sessions with full geospatial support and metadata tracking.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Literal, cast
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, ConfigDict, Field
import uuid

from geo_infer_comms.models.spatial import GeospatialMetadata


class MessagePriority(str, Enum):
    """Message priority levels for routing and processing."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageType(str, Enum):
    """Types of messages supported in the system."""

    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    LOCATION = "location"
    ALERT = "alert"
    SENSOR_DATA = "sensor_data"
    COMMAND = "command"
    STATUS = "status"


class MessageStatus(str, Enum):
    """Status of message delivery and processing."""

    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    QUEUED = "queued"
    PROCESSING = "processing"


class ChannelType(str, Enum):
    """Types of communication channels."""

    PUBLIC = "public"
    PRIVATE = "private"
    DIRECT = "direct"
    GROUP = "group"


class ChannelStatus(str, Enum):
    """Status of communication channels."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    SUSPENDED = "suspended"


class NotificationType(str, Enum):
    """Types of notifications."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REMINDER = "reminder"


class NotificationStatus(str, Enum):
    """Status of notifications."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    EXPIRED = "expired"


class EventType(str, Enum):
    """Types of events in the system."""

    DATA_UPDATE = "data_update"
    SYSTEM_ALERT = "system_alert"
    USER_ACTION = "user_action"
    SENSOR_TRIGGER = "sensor_trigger"
    GEOSPATIAL_CHANGE = "geospatial_change"


class CollaborationType(str, Enum):
    """Types of collaboration sessions."""

    MEETING = "meeting"
    WORKSHOP = "workshop"
    PLANNING = "planning"
    REVIEW = "review"


class ParticipantRole(str, Enum):
    """Roles of participants in collaboration."""

    HOST = "host"
    MODERATOR = "moderator"
    PARTICIPANT = "participant"
    OBSERVER = "observer"


class ParticipantStatus(str, Enum):
    """Status of participants in collaboration."""

    ONLINE = "online"
    OFFLINE = "offline"
    AWAY = "away"
    BUSY = "busy"


@dataclass
class MessageMetadata:
    """Metadata associated with messages."""

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MessageMetadata:
        """Create metadata from dictionary."""
        return cls(
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data.get("version", 1),
            tags=data.get("tags", []),
            custom_fields=data.get("custom_fields", {}),
        )


class MessageRequest(BaseModel):
    """Request model for creating a new message."""

    content: str = Field(..., min_length=1, max_length=10000)
    recipients: List[str] = Field(..., min_length=1)
    channel_id: Optional[str] = None
    message_type: MessageType = MessageType.TEXT
    priority: MessagePriority = MessagePriority.NORMAL
    metadata: Optional[Dict[str, Any]] = None
    geospatial_data: Optional[GeospatialMetadata] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(use_enum_values=True)


class MessageResponse(BaseModel):
    """Response model for message data."""

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    sender_id: str
    recipients: List[str]
    channel_id: Optional[str] = None
    message_type: MessageType
    priority: MessagePriority
    status: MessageStatus = MessageStatus.SENT
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)
    geospatial_data: Optional[GeospatialMetadata] = None
    delivery_stats: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        data = self.model_dump()
        data["metadata"] = self.metadata.to_dict()
        if self.geospatial_data:
            data["geospatial_data"] = self.geospatial_data.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MessageResponse:
        """Create message from dictionary."""
        if "metadata" in data and isinstance(data["metadata"], dict):
            data["metadata"] = MessageMetadata.from_dict(data["metadata"])
        return cls(**data)


class BroadcastRequest(BaseModel):
    """Request model for broadcasting messages."""

    content: str = Field(..., min_length=1, max_length=10000)
    target_type: Literal["all_users", "channel", "role", "location_based"] = Field(...)
    target_criteria: Dict[str, Any] = Field(...)
    message_type: Literal["announcement", "alert", "emergency", "notification"] = (
        "announcement"
    )
    priority: MessagePriority = MessagePriority.NORMAL
    geospatial_filter: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class BroadcastResponse(BaseModel):
    """Response model for broadcast operations."""

    broadcast_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: Literal["sent", "in_progress", "completed", "failed"] = "sent"
    recipient_count: int = 0
    delivery_stats: Dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class ChannelRequest(BaseModel):
    """Request model for creating channels."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    type: ChannelType = ChannelType.PUBLIC
    permissions: Dict[str, Any] = Field(default_factory=dict)
    settings: Dict[str, Any] = Field(default_factory=dict)
    geospatial_bounds: Optional[Dict[str, Any]] = None


class ChannelResponse(BaseModel):
    """Response model for channel data."""

    channel_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    type: ChannelType
    status: ChannelStatus = ChannelStatus.ACTIVE
    member_count: int = 0
    permissions: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    geospatial_bounds: Optional[Dict[str, Any]] = None


class SubscriptionRequest(BaseModel):
    """Request model for channel subscriptions."""

    subscription_type: Literal["all_messages", "mentions_only", "important_only"] = (
        "all_messages"
    )
    notification_preferences: Dict[str, Any] = Field(default_factory=dict)


class SubscriptionResponse(BaseModel):
    """Response model for subscription data."""

    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    user_id: str
    subscription_type: str
    status: Literal["active", "paused", "cancelled"] = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NotificationRequest(BaseModel):
    """Request model for creating notifications."""

    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=2000)
    recipients: List[str] = Field(..., min_length=1)
    notification_type: NotificationType = NotificationType.INFO
    priority: MessagePriority = MessagePriority.NORMAL
    delivery_method: List[Literal["in_app", "email", "sms", "push"]] = Field(
        default_factory=lambda: cast(
            "list[Literal['in_app', 'email', 'sms', 'push']]", ["in_app"]
        )
    )
    schedule_time: Optional[datetime] = None
    expiry_time: Optional[datetime] = None
    geospatial_context: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Response model for notification data."""

    notification_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    notification_type: NotificationType
    priority: MessagePriority
    status: NotificationStatus = NotificationStatus.PENDING
    delivery_methods: List[str] = Field(default_factory=lambda: ["in_app"])
    recipients: List[str] = Field(default_factory=list)
    delivery_stats: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None
    schedule_time: Optional[datetime] = None
    geospatial_context: Optional[Dict[str, Any]] = None


class EventPublishRequest(BaseModel):
    """Request model for publishing events."""

    event_type: str = Field(...)
    payload: Dict[str, Any] = Field(...)
    source: Optional[str] = None
    target_channels: List[str] = Field(default_factory=list)
    priority: MessagePriority = MessagePriority.NORMAL
    persistence: bool = False
    geospatial_context: Optional[Dict[str, Any]] = None


class EventPublishResponse(BaseModel):
    """Response model for event publishing."""

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = Field(...)
    payload: Dict[str, Any] = Field(...)
    source: Optional[str] = None
    target_channels: List[str] = Field(default_factory=list)
    priority: MessagePriority = MessagePriority.NORMAL
    status: Literal["published", "queued", "failed"] = "published"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivery_count: int = 0
    geospatial_context: Optional[Dict[str, Any]] = None


class EventSubscriptionRequest(BaseModel):
    """Request model for event subscriptions."""

    event_types: List[str] = Field(..., min_length=1)
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    delivery_mode: Literal["real_time", "batched", "on_demand"] = "real_time"
    callback_url: Optional[str] = None


class EventSubscriptionResponse(BaseModel):
    """Response model for event subscriptions."""

    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_types: List[str]
    filter_criteria: Dict[str, Any] = Field(default_factory=dict)
    delivery_mode: Literal["real_time", "batched", "on_demand"] = "real_time"
    callback_url: Optional[str] = None
    status: Literal["active", "paused", "error"] = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CollaborationSessionRequest(BaseModel):
    """Request model for creating collaboration sessions."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    session_type: CollaborationType = CollaborationType.MEETING
    participants: List[str] = Field(..., min_length=1)
    duration: Optional[int] = Field(None, ge=1, le=480)  # minutes
    features: List[
        Literal["screen_share", "whiteboard", "file_share", "voice", "video"]
    ] = Field(default_factory=list)
    geospatial_context: Optional[Dict[str, Any]] = None


class Participant(BaseModel):
    """Model for collaboration participants."""

    user_id: str
    name: str
    role: ParticipantRole = ParticipantRole.PARTICIPANT
    status: ParticipantStatus = ParticipantStatus.OFFLINE
    joined_at: Optional[datetime] = None


class CollaborationSessionResponse(BaseModel):
    """Response model for collaboration sessions."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    session_type: CollaborationType
    status: Literal["scheduled", "active", "paused", "ended"] = "scheduled"
    participants: List[Participant] = Field(default_factory=list)
    join_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    geospatial_context: Optional[Dict[str, Any]] = None


class JoinSessionResponse(BaseModel):
    """Response model for joining collaboration sessions."""

    session_id: str
    participant_id: str
    join_status: Literal["joined", "waiting", "rejected"] = "joined"
    session_info: Dict[str, Any] = Field(default_factory=dict)


class StreamRequest(BaseModel):
    """Request model for creating data streams."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    stream_type: Literal["data", "video", "audio", "geospatial", "sensor"] = "data"
    source: Optional[str] = None
    configuration: Dict[str, Any] = Field(default_factory=dict)
    quality_settings: Dict[str, Any] = Field(default_factory=dict)
    geospatial_filter: Optional[Dict[str, Any]] = None


class StreamResponse(BaseModel):
    """Response model for data streams."""

    stream_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    stream_type: str
    status: Literal["active", "paused", "stopped", "error"] = "active"
    connection_url: Optional[str] = None
    viewer_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    geospatial_filter: Optional[Dict[str, Any]] = None


class WebSocketInfoResponse(BaseModel):
    """Response model for WebSocket connection information."""

    websocket_url: str
    protocols: List[str] = Field(default_factory=list)
    connection_token: str
    heartbeat_interval: int = 30


# Collection response models
class MessageListResponse(BaseModel):
    """Response model for message lists."""

    messages: List[MessageResponse]
    total_count: int
    pagination: Dict[str, Any] = Field(default_factory=dict)


class ChannelListResponse(BaseModel):
    """Response model for channel lists."""

    channels: List[ChannelResponse]
    total_count: int


class NotificationListResponse(BaseModel):
    """Response model for notification lists."""

    notifications: List[NotificationResponse]
    unread_count: int
    total_count: int


class CollaborationSessionListResponse(BaseModel):
    """Response model for collaboration session lists."""

    sessions: List[CollaborationSessionResponse]
    total_count: int


class StreamListResponse(BaseModel):
    """Response model for stream lists."""

    streams: List[StreamResponse]
    total_count: int


class HealthResponse(BaseModel):
    """Response model for health checks."""

    status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    connections: Dict[str, Any] = Field(default_factory=dict)


class Error(BaseModel):
    """Error response model."""

    error: str
    message: str


# Utility functions for model conversion
def message_request_to_response(
    request: MessageRequest, sender_id: str
) -> MessageResponse:
    """Convert message request to response model."""
    return MessageResponse(
        content=request.content,
        sender_id=sender_id,
        recipients=request.recipients,
        channel_id=request.channel_id,
        message_type=request.message_type,
        priority=request.priority,
        geospatial_data=request.geospatial_data,
    )


