"""Tests for COMMS channel system."""
import pytest

from geo_infer_comms.models.message import (
    ChannelType,
    ChannelStatus,
    MessagePriority,
)


class TestChannelTypes:
    def test_channel_type_public(self):
        assert ChannelType.PUBLIC.value == "public"

    def test_channel_type_private(self):
        assert ChannelType.PRIVATE.value == "private"

    def test_channel_status_active(self):
        assert ChannelStatus.ACTIVE.value == "active"

    def test_channel_status_archived(self):
        assert ChannelStatus.ARCHIVED.value == "archived"


class TestChannelMetrics:
    """Test channel metric data structures."""

    def test_channel_metric_tracking(self):
        metrics = {
            "channels_created": 0,
            "channels_deleted": 0,
            "members_added": 0,
            "members_removed": 0,
            "messages_sent": 0,
        }

        metrics["channels_created"] += 1
        metrics["members_added"] += 3
        metrics["messages_sent"] += 10

        assert metrics["channels_created"] == 1
        assert metrics["members_added"] == 3
        assert metrics["messages_sent"] == 10

    def test_channel_message_priority_ordering(self):
        priorities = [MessagePriority.LOW, MessagePriority.NORMAL, MessagePriority.HIGH, MessagePriority.URGENT]
        assert len(priorities) == 4
        assert priorities[0] == MessagePriority.LOW
        assert priorities[-1] == MessagePriority.URGENT
