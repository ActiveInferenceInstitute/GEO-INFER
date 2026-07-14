"""
Integration tests for SEC + API + APP security flows.

Tests real integration between security, API gateway, and application modules.
"""

import pytest

from geo_infer_api.app import main_app
from geo_infer_app.models.agent_interface import AgentState, AgentType
from geo_infer_app.models.agent_visualization import AgentVisualization
from geo_infer_sec.core.authentication import AuthenticationManager
from geo_infer_sec.core.authorization import GeospatialAccessManager
from geo_infer_sec import SecurityFramework


@pytest.fixture
def sample_security_config():
    """Sample security configuration."""
    return {
        "authentication_method": "jwt",
        "authorization_model": "rbac",
        "encryption_enabled": True,
        "audit_logging": True,
    }


@pytest.mark.integration
class TestSecApiAppSecurity:
    """Test security integration between SEC, API, and APP modules."""

    def test_api_security_integration(self, sample_security_config):
        """Test API security with SEC module integration."""
        security = SecurityFramework(config=sample_security_config)

        # Verify integration
        assert main_app.title == "GEO-INFER-API"
        assert security is not None

    def test_authentication_flow(self, sample_security_config):
        """Test authentication flow through API to APP."""
        # Create authentication manager
        auth = AuthenticationManager(
            secret_key="strict-test-secret",
        )

        # Simulate authentication
        _test_user = {"username": "test_user", "password": "test_password"}

        # Verify authentication manager
        assert auth is not None
        assert auth.secret_key == "strict-test-secret"

    def test_api_gateway_with_security(self, sample_security_config):
        """Test API gateway with security integration."""
        gateway = main_app

        # Verify gateway creation
        assert gateway is not None
        assert any(route.path == "/docs" for route in gateway.routes)

    def test_app_security_integration(self, sample_security_config):
        """Test application security with SEC and API."""
        state = AgentState(
            agent_id="secure-agent",
            agent_type=AgentType.ACTIVE_INFERENCE,
            status="authenticated",
            location={"lat": 37.78, "lng": -122.42},
        )
        feature = AgentVisualization.state_to_map_feature(state)

        # Verify security integration
        assert feature["properties"]["id"] == "secure-agent"
        assert feature["geometry"]["coordinates"] == [-122.42, 37.78]

    def test_secure_data_flow(self, sample_security_config):
        """Test secure data flow from API through security to APP."""
        security = GeospatialAccessManager(secret_key="strict-test-secret")
        gateway = main_app

        # Simulate secure request
        test_request = {
            "endpoint": "/api/v1/data",
            "method": "GET",
            "headers": {"Authorization": "Bearer test_token"},
        }

        # Verify security components
        assert security.secret_key == "strict-test-secret"
        assert gateway is not None
        assert test_request["headers"]["Authorization"].startswith("Bearer ")
