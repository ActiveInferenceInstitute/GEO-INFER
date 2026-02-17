"""Tests for the authorization module."""
import os
import pytest

from geo_infer_sec.core.authorization import AuthorizationManager, PermissionType
from geo_infer_sec.core.access_control import GeospatialAccessManager, Role, SpatialPermission


@pytest.fixture
def secret_key():
    return "test-secret-key-for-auth-tests-12345"


@pytest.fixture
def auth_manager(secret_key):
    os.environ["GEO_INFER_SEC_SECRET_KEY"] = secret_key
    try:
        return AuthorizationManager(secret_key=secret_key)
    finally:
        os.environ.pop("GEO_INFER_SEC_SECRET_KEY", None)


class TestAuthorizationManager:
    def test_init(self, auth_manager):
        assert auth_manager.access_manager is not None

    def test_grant_and_check_permission(self, auth_manager):
        auth_manager.grant_permission("user-1", "dataset-a", PermissionType.READ)
        assert auth_manager.check_permission("user-1", "dataset-a", PermissionType.READ) is True

    def test_check_permission_denied(self, auth_manager):
        assert auth_manager.check_permission("user-1", "dataset-a", PermissionType.WRITE) is False

    def test_revoke_permission(self, auth_manager):
        auth_manager.grant_permission("user-1", "resource-x", PermissionType.WRITE)
        assert auth_manager.check_permission("user-1", "resource-x", PermissionType.WRITE) is True
        auth_manager.revoke_permission("user-1", "resource-x", PermissionType.WRITE)
        assert auth_manager.check_permission("user-1", "resource-x", PermissionType.WRITE) is False

    def test_list_user_permissions(self, auth_manager):
        auth_manager.grant_permission("user-2", "dataset-b", PermissionType.READ)
        auth_manager.grant_permission("user-2", "dataset-b", PermissionType.WRITE)
        perms = auth_manager.list_user_permissions("user-2")
        assert len(perms) == 2

    def test_admin_permission_grants_all(self, auth_manager):
        role = Role("admin_role")
        role.add_permission(SpatialPermission(name="admin"))
        auth_manager.access_manager.add_role(role)
        auth_manager.access_manager.assign_role_to_user("admin-user", "admin_role")
        assert auth_manager.check_permission("admin-user", "any-resource", PermissionType.DELETE) is True

    def test_wildcard_resource_permission(self, auth_manager):
        role = Role("ops_role")
        role.add_permission(SpatialPermission(name="monitoring:*"))
        auth_manager.access_manager.add_role(role)
        auth_manager.access_manager.assign_role_to_user("ops-user", "ops_role")
        assert auth_manager.check_permission("ops-user", "monitoring", PermissionType.READ) is True

    def test_init_requires_secret_key(self):
        os.environ.pop("GEO_INFER_SEC_SECRET_KEY", None)
        with pytest.raises(ValueError, match="Secret key must be provided"):
            AuthorizationManager()
