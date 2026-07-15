"""
GEO-INFER-COMMS: Geospatial Communications Infrastructure

Comprehensive communication and messaging infrastructure for geospatial systems
enabling data exchange, messaging, networking, and outreach across distributed
applications with full geospatial context and real-time capabilities.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Core components
from geo_infer_comms.core.messaging import (
    MessageBroker,
    MessageRouter,
    MessageFormatter,
    MessageMetrics,  # noqa: F401
)
from geo_infer_comms.core.notifications import (
    NotificationManager,
    AlertSystem,
    EmergencyAlertSystem,
    NotificationMetrics,
    AlertRule,
    AlertResponse,  # noqa: F401
)
from geo_infer_comms.core.channels import (
    ChannelManager,
    ChannelPermissionManager,
    ChannelMessageFilter,  # noqa: F401
    ChannelAnalytics,
    ChannelMetrics,  # noqa: F401
)
from geo_infer_comms.core.events import (
    EventManager,
    EventScheduler,
    EventFilter,
    EventWebhookManager,
    EventMetrics,
    EventProcessor,  # noqa: F401
)

# Data models
from geo_infer_comms.models.message import (
    MessageRequest,
    MessageResponse,
    MessagePriority,
    MessageType,
    MessageStatus,
    ChannelRequest,
    ChannelResponse,
    ChannelType,  # noqa: F401
    NotificationRequest,
    NotificationResponse,
    NotificationType,
    EventPublishRequest,
    EventPublishResponse,
    CollaborationSessionRequest,
    CollaborationSessionResponse,
    StreamRequest,
    StreamResponse,
    BroadcastRequest,
    BroadcastResponse,
    SubscriptionRequest,
    SubscriptionResponse,
    MessageListResponse,
    ChannelListResponse,
    NotificationListResponse,
    CollaborationSessionListResponse,
    StreamListResponse,
    HealthResponse,
    Error,
    Participant,
    ParticipantRole,
    ParticipantStatus,
    MessageMetadata,  # noqa: F401
    EventSubscriptionRequest,
    validate_geospatial_bounds,  # noqa: F401
)

# Spatial models
from geo_infer_comms.models.spatial import (
    GeospatialPoint,
    GeospatialBounds,
    GeospatialMetadata,
    SpatialFilter,
    SpatialIndex,
    CoordinateSystem,
    calculate_distance,
    create_bounds_from_points,
    buffer_point,
    validate_geojson_geometry,
    geojson_to_geospatial_point,
    geospatial_point_to_geojson,
)

# Utilities
from geo_infer_comms.utils.validation import (
    validate_coordinates,
    validate_crs,
    validate_email,
    validate_phone,
    validate_message_content,
    validate_message_priority,
    validate_message_type,
    validate_user_id,
    validate_channel_id,
    validate_spatial_bounds,
    validate_geojson_feature,
    validate_notification_type,
    validate_delivery_methods,
    validate_event_type,
    validate_timestamp,
    validate_url,
    validate_file_size,
    validate_message_recipients,
    validate_spatial_filter,
    validate_collaboration_session,
    validate_stream_config,
    sanitize_message_content,
    validate_and_sanitize_inputs,
    validate_configuration,
)

# Set up module-level logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


class GeospatialCommunicationSystem:
    """
    Main geospatial communication system.

    Provides a unified interface to all GEO-INFER-COMMS functionality
    including messaging, notifications, channels, events, and collaboration.
    """

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        enable_all_components: bool = True,
    ):
        """
        Initialize the geospatial communication system.

        Args:
            config: Configuration dictionary for system settings
            enable_all_components: Whether to enable all system components
        """
        self.config = config or {}
        self.enable_all_components = enable_all_components

        # Initialize core components
        self.message_broker = MessageBroker(
            max_queue_size=self.config.get("message_queue_size", 10000),
            enable_persistence=self.config.get("enable_persistence", True),
            persistence_path=self.config.get("persistence_path"),
        )

        self.notification_manager = NotificationManager(
            max_notifications=self.config.get("max_notifications", 10000),
            enable_persistence=self.config.get("enable_persistence", True),
            persistence_path=self.config.get("persistence_path"),
        )

        self.channel_manager = ChannelManager(
            max_channels=self.config.get("max_channels", 1000),
            enable_persistence=self.config.get("enable_persistence", True),
            persistence_path=self.config.get("persistence_path"),
        )

        self.event_manager = EventManager(
            max_events=self.config.get("max_events", 10000),
            enable_persistence=self.config.get("enable_persistence", True),
            persistence_path=self.config.get("persistence_path"),
        )

        # Initialize advanced components
        self.alert_system = AlertSystem(self.notification_manager)
        self.emergency_system = EmergencyAlertSystem(self.notification_manager)
        self.channel_permissions = ChannelPermissionManager(self.channel_manager)
        self.channel_analytics = ChannelAnalytics(self.channel_manager)
        self.event_scheduler = EventScheduler(self.event_manager)
        self.event_filter = EventFilter(self.event_manager)
        self.event_webhooks = EventWebhookManager(self.event_manager)
        self.message_router = MessageRouter(self.message_broker)

        # System state
        self._started = False
        self.start_time: Optional[datetime] = None

        # Set up logging
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """Start all communication system components."""
        if self._started:
            return

        try:
            # Start core components
            self.message_broker.start()
            self.notification_manager.start()
            self.event_manager.start()
            self.event_scheduler.start()

            # Mark as started
            self._started = True
            self.start_time = datetime.now(timezone.utc)

            self.logger.info("Geospatial communication system started")

        except Exception as e:
            self.logger.error(f"Failed to start communication system: {e}")
            self.stop()  # Clean up any partially started components
            raise

    def stop(self) -> None:
        """Stop all communication system components."""
        if not self._started:
            return

        try:
            # Stop components in reverse order
            self.event_scheduler.stop()
            self.event_manager.stop()
            self.notification_manager.stop()
            self.message_broker.stop()

            self._started = False
            self.logger.info("Geospatial communication system stopped")

        except Exception as e:
            self.logger.error(f"Error stopping communication system: {e}")

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        if not self._started:
            return {"status": "stopped", "components": {}}

        components = {
            "message_broker": self.message_broker.get_metrics(),
            "notification_manager": self.notification_manager.get_metrics(),
            "channel_manager": self.channel_manager.get_channel_statistics(),
            "event_manager": self.event_manager.get_event_statistics(),
        }

        # Determine overall health
        all_healthy = all(
            comp.get("status", "unknown") != "error" for comp in components.values()
        )

        status = "healthy" if all_healthy else "degraded"

        return {
            "status": status,
            "components": components,
            "uptime_seconds": (
                (datetime.now(timezone.utc) - self.start_time).total_seconds()
                if self.start_time
                else 0
            ),
            "started_at": self.start_time.isoformat() if self.start_time else None,
        }

    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        return {
            "system_health": self.get_system_health(),
            "message_metrics": self.message_broker.get_metrics(),
            "notification_metrics": self.notification_manager.get_metrics(),
            "channel_metrics": self.channel_manager.get_channel_statistics(),
            "event_metrics": self.event_manager.get_event_statistics(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # Convenience methods for common operations
    def send_message(
        self, content: str, recipients: List[str], **kwargs
    ) -> MessageResponse:
        """Send a message with geospatial context."""
        request = MessageRequest(content=content, recipients=recipients, **kwargs)
        return self.message_broker.send_message(request, "system")

    def create_notification(
        self, title: str, content: str, recipients: List[str], **kwargs
    ) -> NotificationResponse:
        """Create a notification."""
        request = NotificationRequest(
            title=title, content=content, recipients=recipients, **kwargs
        )
        return self.notification_manager.create_notification(request)

    def create_channel(
        self, name: str, channel_type: ChannelType = ChannelType.PUBLIC, **kwargs
    ) -> ChannelResponse:
        """Create a communication channel."""
        request = ChannelRequest(name=name, type=channel_type, **kwargs)
        return self.channel_manager.create_channel(request, "system")

    def publish_event(
        self, event_type: str, payload: Dict[str, Any], **kwargs
    ) -> EventPublishResponse:
        """Publish an event."""
        request = EventPublishRequest(event_type=event_type, payload=payload, **kwargs)
        return self.event_manager.publish_event(request)

    def subscribe_to_events(
        self, subscriber_id: str, event_types: List[str], callback: Any, **kwargs
    ) -> str:
        """Subscribe to events."""
        request = EventSubscriptionRequest(event_types=event_types, **kwargs)
        return self.event_manager.subscribe_to_events(subscriber_id, request, callback)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Global system instance for convenience
_global_system: Optional[GeospatialCommunicationSystem] = None


def get_communication_system(
    config: Optional[Dict[str, Any]] = None,
) -> GeospatialCommunicationSystem:
    """Get or create the global communication system instance."""
    global _global_system

    if _global_system is None:
        _global_system = GeospatialCommunicationSystem(config)

    return _global_system


def configure_system(config: Dict[str, Any]) -> None:
    """Configure the global communication system."""
    global _global_system

    if _global_system is None:
        _global_system = GeospatialCommunicationSystem(config)
    else:
        # Update existing system configuration
        _global_system.config.update(config)


# Utility functions for common geospatial communication patterns
def send_location_update(
    location: GeospatialPoint,
    message: str,
    recipients: List[str],
    system: Optional[GeospatialCommunicationSystem] = None,
) -> MessageResponse:
    """Send a location-based message update."""
    if system is None:
        system = get_communication_system()

    geospatial_data = GeospatialMetadata(location=location)

    return system.send_message(
        content=message,
        recipients=recipients,
        message_type=MessageType.LOCATION,
        geospatial_data=geospatial_data,
    )


def create_geospatial_alert(
    location: GeospatialPoint,
    alert_type: str,
    message: str,
    recipients: List[str],
    system: Optional[GeospatialCommunicationSystem] = None,
) -> NotificationResponse:
    """Create a geospatial alert notification."""
    if system is None:
        system = get_communication_system()

    geospatial_context = {
        "location": {"latitude": location.latitude, "longitude": location.longitude},
        "alert_type": alert_type,
    }

    return system.create_notification(
        title=f"Geospatial Alert: {alert_type}",
        content=message,
        recipients=recipients,
        notification_type=NotificationType.WARNING,
        priority=MessagePriority.HIGH,
        geospatial_context=geospatial_context,
    )


def setup_emergency_monitoring(
    emergency_zones: List[GeospatialBounds],
    contact_info: Dict[str, Any],
    system: Optional[GeospatialCommunicationSystem] = None,
) -> None:
    """Set up emergency monitoring for specific zones."""
    if system is None:
        system = get_communication_system()

    # Register emergency zones
    for i, zone in enumerate(emergency_zones):
        system.emergency_system.define_emergency_zone(f"zone_{i}", zone)

    # Register emergency contacts
    for contact_id, info in contact_info.items():
        system.emergency_system.register_emergency_contact(contact_id, info)


# Version and metadata
__version__ = "1.0.0"
__author__ = "GEO-INFER Framework"
__description__ = "Geospatial Communications Infrastructure for distributed systems"

# Export main classes and functions
__all__ = [
    # Main system
    "GeospatialCommunicationSystem",
    "get_communication_system",
    "configure_system",
    # Core components
    "MessageBroker",
    "MessageRouter",
    "MessageFormatter",
    "NotificationManager",
    "NotificationMetrics",
    "AlertRule",
    "AlertSystem",
    "EmergencyAlertSystem",
    "ChannelManager",
    "ChannelPermissionManager",
    "EventManager",
    "EventScheduler",
    "EventFilter",
    "EventMetrics",
    # Data models
    "MessageRequest",
    "MessageResponse",
    "MessagePriority",
    "MessageType",
    "MessageStatus",
    "ChannelRequest",
    "ChannelResponse",
    "ChannelType",
    "NotificationRequest",
    "NotificationResponse",
    "NotificationType",
    "EventPublishRequest",
    "EventPublishResponse",
    "CollaborationSessionRequest",
    "CollaborationSessionResponse",
    "StreamRequest",
    "StreamResponse",
    "BroadcastRequest",
    "BroadcastResponse",
    "SubscriptionRequest",
    "SubscriptionResponse",
    "Participant",
    "ParticipantRole",
    "ParticipantStatus",
    "MessageListResponse",
    "ChannelListResponse",
    "NotificationListResponse",
    "CollaborationSessionListResponse",
    "StreamListResponse",
    "HealthResponse",
    "Error",
    # Spatial models
    "GeospatialPoint",
    "GeospatialBounds",
    "GeospatialMetadata",
    "SpatialFilter",
    "SpatialIndex",
    "CoordinateSystem",
    # Utility functions
    "validate_coordinates",
    "validate_crs",
    "validate_email",
    "validate_phone",
    "validate_message_content",
    "validate_message_priority",
    "validate_message_type",
    "validate_user_id",
    "validate_channel_id",
    "validate_spatial_bounds",
    "validate_geojson_feature",
    "validate_geojson_geometry",
    "validate_notification_type",
    "validate_delivery_methods",
    "validate_event_type",
    "validate_timestamp",
    "validate_url",
    "validate_file_size",
    "validate_message_recipients",
    "validate_spatial_filter",
    "validate_collaboration_session",
    "validate_stream_config",
    "sanitize_message_content",
    "validate_and_sanitize_inputs",
    "validate_configuration",
    # Geospatial utilities
    "calculate_distance",
    "create_bounds_from_points",
    "buffer_point",
    "validate_geojson_geometry",
    "geojson_to_geospatial_point",
    "geospatial_point_to_geojson",
    # Convenience functions
    "send_location_update",
    "create_geospatial_alert",
    "setup_emergency_monitoring",
    # Metadata
    "__version__",
    "__author__",
    "__description__",
]
