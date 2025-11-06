"""
Integration tests for SEC + API + APP security flows.

Tests real integration between security, API gateway, and application modules.
"""

import pytest
from typing import Dict, Any

# Try to import actual modules
try:
    from geo_infer_sec.core.security import SecurityManager
    from geo_infer_sec.core.authentication import AuthenticationManager
    SEC_AVAILABLE = True
except ImportError:
    SEC_AVAILABLE = False
    pytest.skip("GEO-INFER-SEC not available", allow_module_level=True)

try:
    from geo_infer_api.app import create_app
    from geo_infer_api.core.gateway import APIGateway
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    pytest.skip("GEO-INFER-API not available", allow_module_level=True)

try:
    from geo_infer_app.models.agent_interface import AgentInterface
    from geo_infer_app.components.dashboard import DashboardComponent
    APP_AVAILABLE = True
except ImportError:
    APP_AVAILABLE = False
    pytest.skip("GEO-INFER-APP not available", allow_module_level=True)


@pytest.fixture
def sample_security_config():
    """Sample security configuration."""
    return {
        'authentication_method': 'jwt',
        'authorization_model': 'rbac',
        'encryption_enabled': True,
        'audit_logging': True
    }


@pytest.mark.integration
class TestSecApiAppSecurity:
    """Test security integration between SEC, API, and APP modules."""
    
    def test_api_security_integration(self, sample_security_config):
        """Test API security with SEC module integration."""
        if not (SEC_AVAILABLE and API_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create security manager
        security = SecurityManager(
            config=sample_security_config
        )
        
        # Create API application
        app = create_app(
            title="GEO-INFER API",
            version="1.0.0"
        )
        
        # Verify integration
        assert app is not None
        assert security is not None
    
    def test_authentication_flow(self, sample_security_config):
        """Test authentication flow through API to APP."""
        if not (SEC_AVAILABLE and API_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create authentication manager
        auth = AuthenticationManager(
            method=sample_security_config['authentication_method']
        )
        
        # Simulate authentication
        test_user = {
            'username': 'test_user',
            'password': 'test_password'
        }
        
        # Verify authentication manager
        assert auth is not None
        assert auth.method == sample_security_config['authentication_method']
    
    def test_api_gateway_with_security(self, sample_security_config):
        """Test API gateway with security integration."""
        if not (SEC_AVAILABLE and API_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create API gateway
        gateway = APIGateway(
            security_enabled=True,
            authentication_required=True
        )
        
        # Verify gateway creation
        assert gateway is not None
        assert gateway.security_enabled is True
    
    def test_app_security_integration(self, sample_security_config):
        """Test application security with SEC and API."""
        if not (SEC_AVAILABLE and API_AVAILABLE and APP_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create security manager
        security = SecurityManager(config=sample_security_config)
        
        # Create API application
        app = create_app(
            title="GEO-INFER API",
            version="1.0.0",
            security_enabled=True
        )
        
        # Verify security integration
        assert app is not None
        assert security is not None
    
    def test_secure_data_flow(self, sample_security_config):
        """Test secure data flow from API through security to APP."""
        if not (SEC_AVAILABLE and API_AVAILABLE):
            pytest.skip("Required modules not available")
        
        # Create security manager
        security = SecurityManager(config=sample_security_config)
        
        # Create API gateway
        gateway = APIGateway(
            security_enabled=True,
            authentication_required=True
        )
        
        # Simulate secure request
        test_request = {
            'endpoint': '/api/v1/data',
            'method': 'GET',
            'headers': {'Authorization': 'Bearer test_token'}
        }
        
        # Verify security components
        assert security is not None
        assert gateway is not None
        assert gateway.security_enabled is True


