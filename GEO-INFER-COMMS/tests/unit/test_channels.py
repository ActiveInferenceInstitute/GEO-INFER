"""Tests for COMMS channel system."""
import pytest

from geo_infer_comms.core.channels import ChannelManager, ChannelPermissionManager
from geo_infer_comms.models.message import (
    ChannelRequest,
    ChannelType,
    ChannelStatus,
)
from geo_infer_comms.models.spatial import GeospatialPoint


BAY_AREA_BOUNDS = {
    "min_longitude": -122.6,
    "min_latitude": 37.6,
    "max_longitude": -122.2,
    "max_latitude": 37.9,
}


def _manager_with_bounded_channel() -> tuple[ChannelManager, object]:
    manager = ChannelManager(enable_persistence=False)
    request = ChannelRequest(
        name="Bay Area Response",
        type=ChannelType.PUBLIC,
        description="Channel with geospatial bounds",
        geospatial_bounds=BAY_AREA_BOUNDS,
    )
    channel = manager.create_channel(request, "creator")
    return manager, channel


class TestChannelTypes:
    def test_channel_type_public(self):
        assert ChannelType.PUBLIC.value == "public"

    def test_channel_type_private(self):
        assert ChannelType.PRIVATE.value == "private"

    def test_channel_status_active(self):
        assert ChannelStatus.ACTIVE.value == "active"

    def test_channel_status_archived(self):
        assert ChannelStatus.ARCHIVED.value == "archived"


class TestChannelsByLocation:
    """Regression tests: channel geospatial bounds are stored as dicts and
    must be parsed into GeospatialBounds before spatial comparison."""

    def test_finds_channel_inside_bounds(self) -> None:
        manager, channel = _manager_with_bounded_channel()

        found = manager.get_channels_by_location(
            GeospatialPoint(longitude=-122.4, latitude=37.7)
        )

        assert [c.channel_id for c in found] == [channel.channel_id]

    def test_excludes_channel_outside_bounds(self) -> None:
        manager, channel = _manager_with_bounded_channel()

        found = manager.get_channels_by_location(
            GeospatialPoint(longitude=-100.0, latitude=35.0)
        )

        assert found == []

    def test_unbounded_channel_is_never_matched(self) -> None:
        manager, _ = _manager_with_bounded_channel()
        request = ChannelRequest(name="Unbounded", type=ChannelType.PUBLIC)
        unbounded = manager.create_channel(request, "creator")

        inside = manager.get_channels_by_location(
            GeospatialPoint(longitude=-122.4, latitude=37.7)
        )

        assert unbounded.channel_id not in [c.channel_id for c in inside]


class TestGeospatialPermission:
    def test_inside_bounds_falls_through_to_permission_check(self) -> None:
        manager, channel = _manager_with_bounded_channel()
        permissions = ChannelPermissionManager(manager)

        allowed = permissions.check_geospatial_permission(
            channel.channel_id, "creator", "read",
            GeospatialPoint(longitude=-122.4, latitude=37.7),
        )

        assert allowed is True

    def test_outside_bounds_denied(self) -> None:
        manager, channel = _manager_with_bounded_channel()
        permissions = ChannelPermissionManager(manager)

        allowed = permissions.check_geospatial_permission(
            channel.channel_id, "creator", "read",
            GeospatialPoint(longitude=0.0, latitude=0.0),
        )

        assert allowed is False
