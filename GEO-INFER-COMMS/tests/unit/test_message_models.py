"""Tests for COMMS message data models."""
import pytest
from datetime import datetime, timezone

from geo_infer_comms.models.message import (
    MessagePriority,
    MessageType,
    MessageStatus,
    ChannelType,
    ChannelStatus,
    NotificationType,
    NotificationStatus,
    EventType,
    CollaborationType,
    ParticipantRole,
    ParticipantStatus,
    MessageMetadata,
)


class TestEnumModels:
    def test_message_priority_values(self):
        assert MessagePriority.LOW == "low"
        assert MessagePriority.NORMAL == "normal"
        assert MessagePriority.HIGH == "high"
        assert MessagePriority.URGENT == "urgent"

    def test_message_type_values(self):
        assert MessageType.TEXT == "text"
        assert MessageType.ALERT == "alert"
        assert MessageType.SENSOR_DATA == "sensor_data"

    def test_message_status_values(self):
        assert MessageStatus.SENT == "sent"
        assert MessageStatus.DELIVERED == "delivered"
        assert MessageStatus.FAILED == "failed"

    def test_channel_type_values(self):
        assert ChannelType.PUBLIC == "public"
        assert ChannelType.PRIVATE == "private"
        assert ChannelType.DIRECT == "direct"

    def test_notification_type_values(self):
        assert NotificationType.INFO == "info"
        assert NotificationType.WARNING == "warning"
        assert NotificationType.ERROR == "error"

    def test_event_type_values(self):
        assert EventType.DATA_UPDATE == "data_update"
        assert EventType.SYSTEM_ALERT == "system_alert"
        assert EventType.GEOSPATIAL_CHANGE == "geospatial_change"

    def test_collaboration_type_values(self):
        assert CollaborationType.MEETING == "meeting"
        assert CollaborationType.REVIEW == "review"

    def test_participant_role_values(self):
        assert ParticipantRole.HOST == "host"
        assert ParticipantRole.OBSERVER == "observer"


class TestMessageMetadata:
    def test_create_metadata(self):
        meta = MessageMetadata()
        assert meta.created_at is not None
        assert meta.updated_at is not None

    def test_metadata_timestamps_are_utc(self):
        meta = MessageMetadata()
        assert meta.created_at.tzinfo is not None
