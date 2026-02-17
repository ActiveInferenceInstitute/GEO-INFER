"""Tests for the access control module (RBAC and spatial permissions)."""
import pytest
from shapely.geometry import Polygon, Point
import geopandas as gpd

from geo_infer_sec.core.access_control import (
    SpatialPermission,
    Role,
    GeospatialAccessManager,
)


class TestSpatialPermission:
    def test_create_permission_no_geometry(self):
        perm = SpatialPermission(name="read_all")
        assert perm.name == "read_all"
        assert perm.geometry is None

    def test_contains_point_no_geometry_returns_true(self):
        perm = SpatialPermission(name="read_all")
        assert perm.contains_point(37.7749, -122.4194) is True

    def test_contains_point_with_geometry(self):
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        perm = SpatialPermission(name="read_area", geometry=poly)
        assert perm.contains_point(5, 5) is True
        assert perm.contains_point(15, 15) is False

    def test_create_from_wkt(self):
        wkt = "POLYGON ((0 0, 10 0, 10 10, 0 10, 0 0))"
        perm = SpatialPermission(name="test", wkt=wkt)
        assert perm.geometry is not None

    def test_create_from_geojson(self):
        geojson = {
            "type": "Polygon",
            "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
        }
        perm = SpatialPermission(name="test", geojson=geojson)
        assert perm.geometry is not None


class TestRole:
    def test_create_role(self):
        role = Role("admin")
        assert role.name == "admin"
        assert len(role.permissions) == 0

    def test_add_permission(self):
        role = Role("reader")
        role.add_permission(SpatialPermission(name="read"))
        assert len(role.permissions) == 1

    def test_has_permission(self):
        role = Role("reader")
        role.add_permission(SpatialPermission(name="read"))
        assert role.has_permission("read") is True
        assert role.has_permission("write") is False

    def test_get_accessible_area(self):
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        role = Role("geo_reader")
        role.add_permission(SpatialPermission(name="read", geometry=poly))
        area = role.get_accessible_area()
        assert area is not None

    def test_get_accessible_area_no_permissions(self):
        role = Role("empty")
        assert role.get_accessible_area() is None


class TestGeospatialAccessManager:
    def test_init(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        assert mgr.secret_key == "test-key"

    def test_add_role_and_assign(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        role = Role("viewer")
        mgr.add_role(role)
        assert mgr.assign_role_to_user("user-1", "viewer") is True

    def test_assign_nonexistent_role(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        assert mgr.assign_role_to_user("user-1", "nonexistent") is False

    def test_get_user_roles(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        mgr.add_role(Role("role-a"))
        mgr.add_role(Role("role-b"))
        mgr.assign_role_to_user("user-1", "role-a")
        mgr.assign_role_to_user("user-1", "role-b")
        roles = mgr.get_user_roles("user-1")
        assert len(roles) == 2

    def test_generate_and_validate_token(self):
        mgr = GeospatialAccessManager(secret_key="test-secret-key-xyz")
        mgr.add_role(Role("viewer"))
        mgr.assign_role_to_user("user-1", "viewer")
        token = mgr.generate_token("user-1")
        payload = mgr.validate_token(token)
        assert payload is not None
        assert payload["user_id"] == "user-1"

    def test_validate_invalid_token(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        assert mgr.validate_token("invalid-token") is None

    def test_can_access_location(self):
        mgr = GeospatialAccessManager(secret_key="test-key")
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        role = Role("geo_reader")
        role.add_permission(SpatialPermission(name="read", geometry=poly))
        mgr.add_role(role)
        mgr.assign_role_to_user("user-1", "geo_reader")
        assert mgr.can_access_location("user-1", 5, 5) is True
        assert mgr.can_access_location("user-1", 15, 15) is False
