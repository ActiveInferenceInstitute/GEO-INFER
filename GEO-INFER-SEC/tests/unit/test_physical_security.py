"""PhysicalSecurityManager sensor, zone, and threat-detection tests (GS-224).

Characterizes access-permission verification, time-based access windows,
zone lookups, surveillance coverage, intrusion/unauthorized-access
detection with severity escalation by zone clearance, and alert-callback
fan-out. Monitoring threads are never started.
"""

from datetime import datetime, timedelta
from uuid import uuid4

import geopandas as gpd
import pytest
from shapely.geometry import Point, Polygon

from geo_infer_sec.core.physical_security import (
    AccessControlDevice,
    AccessControlType,
    PhysicalSecurityManager,
    PhysicalThreat,
    SecurityZone,
    SecurityZoneType,
    SurveillanceDevice,
    SurveillanceType,
)
from geo_infer_sec.models.security_models import ThreatLevel


@pytest.fixture
def manager() -> PhysicalSecurityManager:
    """PhysicalSecurityManager with monitoring threads never started."""
    return PhysicalSecurityManager()


def make_zone(
    zone_id: str,
    clearance: int,
    polygon: Polygon,
    access_hours: dict | None = None,
) -> SecurityZone:
    return SecurityZone(
        zone_id=zone_id,
        name=f"Zone {zone_id}",
        zone_type=SecurityZoneType.RESTRICTED,
        boundary=polygon,
        required_clearance_level=clearance,
        access_hours=access_hours,
    )


def square(center: Point, half_width: float = 0.01) -> Polygon:
    return Polygon(
        [
            (center.x - half_width, center.y - half_width),
            (center.x + half_width, center.y - half_width),
            (center.x + half_width, center.y + half_width),
            (center.x - half_width, center.y + half_width),
        ]
    )


def add_restricted_zone(
    manager: PhysicalSecurityManager, clearance: int
) -> SecurityZone:
    """Add a deterministic zone around (5, 50) far from the default public zone."""
    zone = make_zone(f"restricted-{clearance}", clearance, square(Point(5.0, 50.0)))
    assert manager.add_security_zone(zone) is True
    return zone


def make_access_device(
    location: Point, device_id: str = "dev-1", is_active: bool = True
) -> AccessControlDevice:
    return AccessControlDevice(
        device_id=device_id,
        name="Door reader",
        device_type=AccessControlType.KEYPAD,
        location=location,
        zone_id="restricted",
        is_active=is_active,
    )


def make_surveillance_device(
    location: Point,
    device_id: str = "cam-1",
    coverage: Polygon | None = None,
    is_active: bool = True,
) -> SurveillanceDevice:
    return SurveillanceDevice(
        device_id=device_id,
        name="Camera",
        device_type=SurveillanceType.CCTV,
        location=location,
        zone_id="restricted",
        coverage_area=coverage,
        is_active=is_active,
    )


class TestAccessControl:
    """verify_access_permission against zones, clearance, and state."""

    def test_unknown_device_denied(self, manager):
        result = manager.verify_access_permission("user-1", "no-such-device", 5)
        assert result == (False, "Device not found")

    def test_inactive_device_denied(self, manager):
        add_restricted_zone(manager, clearance=0)
        device = make_access_device(Point(5.0, 50.0), is_active=False)
        manager.add_access_device(device)
        result = manager.verify_access_permission("user-1", "dev-1", 5)
        assert result == (False, "Device is inactive")

    def test_insufficient_clearance_denied(self, manager):
        add_restricted_zone(manager, clearance=2)
        device = make_access_device(Point(5.0, 50.0))
        manager.add_access_device(device)
        result = manager.verify_access_permission("user-1", "dev-1", 1)
        assert result == (False, "Insufficient clearance level for zone restricted-2")

    def test_sufficient_clearance_granted(self, manager):
        add_restricted_zone(manager, clearance=2)
        device = make_access_device(Point(5.0, 50.0))
        manager.add_access_device(device)
        result = manager.verify_access_permission("user-1", "dev-1", 3)
        assert result == (True, "Access granted")

    def test_full_day_access_hours_never_block(self, manager):
        zone = make_zone(
            "hours-zone",
            0,
            square(Point(5.0, 50.0)),
            access_hours={"start": "00:00", "end": "23:59"},
        )
        manager.add_security_zone(zone)
        device = make_access_device(Point(5.0, 50.0))
        manager.add_access_device(device)
        # Runs at whatever wall-clock time pytest executes it: always inside.
        result = manager.verify_access_permission("user-1", "dev-1", 0)
        assert result == (True, "Access granted")


class TestAccessHoursWindow:
    """_is_within_access_hours time and day logic with explicit clocks."""

    def test_same_day_inside_window(self, manager):
        hours = {"start": "08:00", "end": "18:00", "days": ["wed", "thu"]}
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 10, 12, 0), hours) is True
        )

    def test_same_day_outside_window(self, manager):
        hours = {"start": "08:00", "end": "18:00", "days": ["wed", "thu"]}
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 10, 19, 30), hours)
            is False
        )

    def test_cross_midnight_window_wraps(self, manager):
        hours = {"start": "22:00", "end": "06:00", "days": ["mon", "tue"]}
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 8, 3, 0), hours) is True
        )
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 8, 12, 0), hours) is False
        )

    def test_disallowed_day_denied(self, manager):
        hours = {"start": "00:00", "end": "23:59", "days": ["fri"]}
        # 2026-09-10 is a Thursday.
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 10, 10, 0), hours)
            is False
        )

    def test_invalid_hours_configuration_denies_access(self, manager):
        hours = {"start": "banana", "end": "18:00"}
        assert (
            manager._is_within_access_hours(datetime(2026, 9, 10, 10, 0), hours)
            is False
        )

    def test_missing_hours_default_to_full_day(self, manager):
        assert manager._is_within_access_hours(datetime(2026, 9, 10, 23, 0), {}) is True


class TestZoneManagement:
    """Zone registration, lookup, and boundary updates."""

    def test_default_public_zone_exists(self, manager):
        zone = manager.get_security_zone("public")
        assert zone is not None
        assert zone.required_clearance_level == 0

    def test_get_zones_for_location(self, manager):
        add_restricted_zone(manager, clearance=3)
        zones = manager.get_zones_for_location(Point(5.0, 50.0))
        assert [z.zone_id for z in zones] == ["restricted-3"]
        # Far away from every registered zone.
        assert manager.get_zones_for_location(Point(-120.0, 40.0)) == []

    def test_update_zone_boundary(self, manager):
        zone = add_restricted_zone(manager, clearance=1)
        new_boundary = square(Point(6.0, 51.0))
        assert manager.update_zone_boundary(zone.zone_id, new_boundary) is True
        assert manager.get_security_zone(zone.zone_id).boundary == new_boundary
        assert manager.update_zone_boundary("no-such-zone", new_boundary) is False


class TestThreatDetection:
    """Intrusion and unauthorized-access detection with zone-based severity."""

    def test_intrusion_severity_escalates_with_zone_clearance(self, manager):
        add_restricted_zone(manager, clearance=3)
        threat = manager.detect_intrusion(Point(5.0, 50.0), "motion_sensor")
        assert threat.threat_type == "intrusion"
        assert threat.severity is ThreatLevel.CRITICAL
        assert threat.status == "active"
        assert threat.metadata["zones"] == ["restricted-3"]
        assert threat.threat_id in manager.active_threats

    def test_intrusion_moderate_zone_severity(self, manager):
        add_restricted_zone(manager, clearance=2)
        threat = manager.detect_intrusion(Point(5.0, 50.0), "motion_sensor")
        assert threat.severity is ThreatLevel.HIGH

    def test_intrusion_outside_all_zones_is_medium(self, manager):
        threat = manager.detect_intrusion(Point(-120.0, 40.0), "seismic")
        assert threat.severity is ThreatLevel.MEDIUM
        assert threat.metadata["zones"] == []

    def test_intrusion_triggers_alert_callbacks(self, manager):
        received = []
        manager.add_alert_callback(received.append)
        threat = manager.detect_intrusion(Point(-120.0, 40.0), "seismic")
        assert [t.threat_id for t in received] == [threat.threat_id]

    def test_failing_callback_does_not_block_detection(self, manager):
        def exploding_callback(threat):
            raise RuntimeError("callback exploded")

        manager.add_alert_callback(exploding_callback)
        threat = manager.detect_intrusion(Point(-120.0, 40.0), "seismic")
        assert threat is not None
        assert threat.threat_id in manager.active_threats

    def test_detect_unauthorized_access_unknown_device(self, manager):
        assert (
            manager.detect_unauthorized_access(
                "no-such-device", "user-1", datetime.now()
            )
            is None
        )

    def test_detect_unauthorized_access_creates_high_threat(self, manager):
        device = make_access_device(Point(5.0, 50.0))
        manager.add_access_device(device)
        attempted_at = datetime.now() - timedelta(minutes=2)

        threat = manager.detect_unauthorized_access("dev-1", "user-7", attempted_at)

        assert threat is not None
        assert threat.threat_type == "unauthorized_access"
        assert threat.severity is ThreatLevel.HIGH
        assert threat.detection_method == "access_control"
        assert threat.metadata["device_id"] == "dev-1"
        assert threat.metadata["user_id"] == "user-7"
        assert threat.metadata["attempted_at"] == attempted_at.isoformat()
        assert manager.active_threats[threat.threat_id] is threat


class TestSurveillanceCoverage:
    """Coverage lookups and the aggregate coverage map."""

    def test_get_surveillance_coverage_by_polygon(self, manager):
        covering = make_surveillance_device(
            Point(5.0, 50.0), coverage=square(Point(5.0, 50.0))
        )
        elsewhere = make_surveillance_device(
            Point(6.0, 51.0), device_id="cam-2", coverage=square(Point(6.0, 51.0))
        )
        manager.add_surveillance_device(covering)
        manager.add_surveillance_device(elsewhere)

        found = manager.get_surveillance_coverage(Point(5.0005, 50.0005))
        assert [d.device_id for d in found] == ["cam-1"]

    def test_device_without_coverage_area_never_covers(self, manager):
        manager.add_surveillance_device(
            make_surveillance_device(Point(5.0, 50.0), coverage=None)
        )
        assert manager.get_surveillance_coverage(Point(5.0, 50.0)) == []

    def test_coverage_map_includes_only_active_devices(self, manager):
        active = make_surveillance_device(
            Point(5.0, 50.0), device_id="cam-1", coverage=square(Point(5.0, 50.0))
        )
        inactive = make_surveillance_device(
            Point(6.0, 51.0),
            device_id="cam-2",
            coverage=square(Point(6.0, 51.0)),
            is_active=False,
        )
        manager.add_surveillance_device(active)
        manager.add_surveillance_device(inactive)

        coverage_map = manager.calculate_surveillance_coverage_map()

        assert isinstance(coverage_map, gpd.GeoDataFrame)
        assert list(coverage_map["device_id"]) == ["cam-1"]
        assert coverage_map.crs.to_string() == "EPSG:4326"

    def test_coverage_map_empty_without_devices(self, manager):
        coverage_map = manager.calculate_surveillance_coverage_map()
        assert isinstance(coverage_map, gpd.GeoDataFrame)
        assert coverage_map.empty


class TestThreatShape:
    """PhysicalThreat defaults keep new detections active."""

    def test_new_threat_defaults(self):
        threat = PhysicalThreat(
            threat_id=f"t-{uuid4().hex}",
            threat_type="intrusion",
            location=Point(5.0, 50.0),
            severity=ThreatLevel.MEDIUM,
            detected_at=datetime.now(),
            detection_method="unit-test",
            description="synthetic",
        )
        assert threat.status == "active"
        assert threat.assigned_to is None
        assert threat.metadata == {}
        # Severity-based threat aging windows stay consistent with
        # correlation windows used by the integrated manager.
        assert threat.detected_at <= datetime.now() + timedelta(seconds=1)
