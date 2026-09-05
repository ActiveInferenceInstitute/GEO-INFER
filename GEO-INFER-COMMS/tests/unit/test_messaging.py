"""Tests for the message broker: subscriptions and broadcast resolution."""
import time

import pytest

from geo_infer_comms.core.messaging import MessageBroker
from geo_infer_comms.models.message import (
    BroadcastRequest,
    MessageRequest,
    MessageStatus,
)
from geo_infer_comms.models.spatial import (
    GeospatialMetadata,
    GeospatialPoint,
    SpatialFilter,
)


BAY_AREA_BOUNDS = {
    "min_longitude": -122.6,
    "min_latitude": 37.6,
    "max_longitude": -122.2,
    "max_latitude": 37.9,
}


def _bay_area_filter() -> SpatialFilter:
    return SpatialFilter(filter_type="bounds", parameters={"bounds": BAY_AREA_BOUNDS})


class TestBroadcastRecipientResolution:
    def test_channel_target_requires_resolver(self) -> None:
        broker = MessageBroker(enable_persistence=False)

        with pytest.raises(ValueError, match="recipient_resolver"):
            broker._resolve_broadcast_recipients(
                BroadcastRequest(
                    content="hi",
                    target_type="channel",
                    target_criteria={"channel_id": "ch_1"},
                ),
                sender_id="system",
            )

    def test_resolver_callback_is_used_for_channel_target(self) -> None:
        calls: list[tuple[str, dict]] = []

        def resolver(target_type: str, criteria: dict) -> list:
            calls.append((target_type, criteria))
            return ["resolved_user_1", "resolved_user_2"]

        broker = MessageBroker(enable_persistence=False, recipient_resolver=resolver)
        recipients = broker._resolve_broadcast_recipients(
            BroadcastRequest(
                content="hi",
                target_type="channel",
                target_criteria={"channel_id": "ch_9"},
            ),
            sender_id="system",
        )

        assert recipients == ["resolved_user_1", "resolved_user_2"]
        assert calls == [("channel", {"channel_id": "ch_9"})]

    def test_unknown_target_type_raises(self) -> None:
        broker = MessageBroker(enable_persistence=False)

        with pytest.raises(ValueError, match="target_type"):
            broker._resolve_broadcast_recipients(
                BroadcastRequest(
                    content="hi",
                    target_type="location_based",
                    target_criteria={},
                ),
                sender_id="system",
            )

    def test_all_users_targets_registry_without_resolver(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        broker.subscribe("alice", lambda m: None)
        broker.subscribe("bob", lambda m: None)

        recipients = broker._resolve_broadcast_recipients(
            BroadcastRequest(content="hi", target_type="all_users", target_criteria={}),
            sender_id="system",
        )

        assert sorted(recipients) == ["alice", "bob"]

    def test_broadcast_fails_gracefully_without_resolver(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        broker.start()
        try:
            response = broker.broadcast_message(
                BroadcastRequest(
                    content="hi",
                    target_type="role",
                    target_criteria={"role": "admin"},
                ),
                "sender",
            )
        finally:
            broker.stop()

        assert response.status == "failed"
        assert response.recipient_count == 0


class TestSubscriptions:
    def test_unsubscribe_removes_callback_and_spatial_filter(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        received: list = []
        subscription_id = broker.subscribe(
            "alice", received.append, spatial_filter=_bay_area_filter()
        )

        assert broker.unsubscribe("alice", subscription_id) is True

        assert "alice" not in broker.subscribers
        assert subscription_id not in broker.spatial_subscriptions

    def test_unsubscribe_of_unknown_subscription_fails(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        broker.subscribe("alice", lambda m: None)

        assert broker.unsubscribe("alice", "sub_unknown") is False
        # Subscriber keeps their remaining callback
        assert "alice" in broker.subscribers

    def test_spatial_subscription_only_receives_matching_geospatial_messages(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        broker.start()
        received: list = []
        try:
            broker.subscribe(
                "bay_user", received.append, spatial_filter=_bay_area_filter()
            )

            inside = GeospatialMetadata(
                location=GeospatialPoint(longitude=-122.4, latitude=37.7)
            )
            outside = GeospatialMetadata(
                location=GeospatialPoint(longitude=-74.0, latitude=40.7)
            )

            broker.send_message(
                MessageRequest(
                    content="inside", recipients=["bay_user"], geospatial_data=inside
                ),
                "sender",
            )
            broker.send_message(
                MessageRequest(
                    content="outside", recipients=["bay_user"], geospatial_data=outside
                ),
                "sender",
            )
            broker.send_message(
                MessageRequest(content="no_location", recipients=["bay_user"]),
                "sender",
            )

            deadline = time.time() + 5
            while len(received) < 1 and time.time() < deadline:
                time.sleep(0.05)
        finally:
            broker.stop()

        assert [m.content for m in received] == ["inside"]
        assert received[0].status == MessageStatus.DELIVERED

    def test_unfiltered_subscription_receives_plain_messages(self) -> None:
        broker = MessageBroker(enable_persistence=False)
        broker.start()
        received: list = []
        try:
            broker.subscribe("plain_user", received.append)
            broker.send_message(
                MessageRequest(content="plain", recipients=["plain_user"]),
                "sender",
            )
            deadline = time.time() + 5
            while not received and time.time() < deadline:
                time.sleep(0.05)
        finally:
            broker.stop()

        assert [m.content for m in received] == ["plain"]