"""
Tests for security management.
"""
import os
import base64
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509.oid import NameOID

from geo_infer_ops.core.security import SecurityManager
from geo_infer_ops.core.config import Config, SecurityConfig, TLSConfig, AuthConfig

@pytest.fixture
def mock_config():
    """Fixture providing a mock configuration."""
    return Config(
        security=SecurityConfig(
            tls=TLSConfig(
                enabled=True,
                cert_file="/tmp/test.crt",
                key_file="/tmp/test.key"
            ),
            auth=AuthConfig(
                enabled=True,
                jwt_secret="test-secret",
                token_expiry=3600
            )
        )
    )

@pytest.fixture
def security_manager(mock_config):
    """Fixture providing a security manager instance."""
    with patch("geo_infer_ops.core.security.get_config") as mock_get_config:
        mock_get_config.return_value = mock_config
        manager = SecurityManager()
        yield manager

def test_generate_tls_certificate(security_manager, tmp_path):
    """Test TLS certificate generation."""
    # Mock file operations
    with patch("builtins.open", mock_open()) as mock_file:
        result = security_manager.generate_tls_certificate(
            common_name="test.example.com",
            organization="Test Org",
            country="US"
        )
        
        assert result["cert_file"] == "/tmp/test.crt"
        assert result["key_file"] == "/tmp/test.key"
        assert mock_file.call_count == 2

def test_generate_csr(security_manager):
    """Test CSR generation."""
    # Mock file operations
    with patch("builtins.open", mock_open()) as mock_file:
        csr = security_manager.generate_csr(
            common_name="test.example.com",
            organization="Test Org",
            country="US"
        )
        
        assert isinstance(csr, str)
        assert "BEGIN CERTIFICATE REQUEST" in csr
        assert mock_file.call_count == 1

def test_generate_jwt_token(security_manager):
    """Test JWT token generation."""
    token = security_manager.generate_jwt_token(
        user_id="test-user",
        roles=["admin"],
        expires_in=3600
    )
    
    assert isinstance(token, str)
    payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
    assert payload["user_id"] == "test-user"
    assert payload["roles"] == ["admin"]
    assert "exp" in payload

def test_verify_jwt_token(security_manager):
    """Test JWT token verification."""
    # Generate token
    token = security_manager.generate_jwt_token(
        user_id="test-user",
        roles=["admin"]
    )
    
    # Verify token
    payload = security_manager.verify_jwt_token(token)
    assert payload["user_id"] == "test-user"
    assert payload["roles"] == ["admin"]

def test_verify_jwt_token_expired(security_manager):
    """Test verification of expired JWT token."""
    # Generate expired token
    payload = {
        "user_id": "test-user",
        "roles": ["admin"],
        "exp": datetime.utcnow() - timedelta(hours=1)
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    
    # Verify token
    with pytest.raises(jwt.ExpiredSignatureError):
        security_manager.verify_jwt_token(token)

def test_verify_jwt_token_invalid(security_manager):
    """Test verification of invalid JWT token."""
    with pytest.raises(jwt.InvalidTokenError):
        security_manager.verify_jwt_token("invalid-token")

def test_encrypt_decrypt_data(security_manager):
    """Test data encryption and decryption."""
    # Test data
    test_data = "sensitive information"
    
    # Encrypt data
    encrypted = security_manager.encrypt_data(test_data)
    assert isinstance(encrypted, str)
    assert encrypted != test_data
    
    # Decrypt data
    decrypted = security_manager.decrypt_data(encrypted)
    assert decrypted == test_data

def test_generate_password_hash(security_manager):
    """Test password hash generation."""
    # Generate hash
    result = security_manager.generate_password_hash("test-password")
    
    assert "hash" in result
    assert "salt" in result
    assert isinstance(result["hash"], bytes)
    assert isinstance(result["salt"], bytes)

def test_verify_password(security_manager):
    """Test password verification."""
    # Generate hash
    password = "test-password"
    result = security_manager.generate_password_hash(password)
    
    # Verify password
    assert security_manager.verify_password(
        password,
        result["hash"],
        result["salt"]
    ) is True
    
    # Verify wrong password
    assert security_manager.verify_password(
        "wrong-password",
        result["hash"],
        result["salt"]
    ) is False

def test_security_disabled(security_manager):
    """Test operations when security is disabled."""
    # Disable security
    security_manager.config.security.auth.enabled = False
    
    # Test JWT operations
    with pytest.raises(ValueError):
        security_manager.generate_jwt_token("test-user", ["admin"])
    
    with pytest.raises(ValueError):
        security_manager.verify_jwt_token("test-token")

def test_load_keys_failure(security_manager):
    """Test key loading failure."""
    with patch("builtins.open", side_effect=IOError("File not found")):
        with pytest.raises(Exception):
            security_manager._load_keys()

def test_certificate_validation(security_manager):
    """Test certificate validation."""
    # Generate certificate
    result = security_manager.generate_tls_certificate(
        common_name="test.example.com",
        organization="Test Org",
        country="US"
    )
    
    # Load and validate certificate
    with open(result["cert_file"], "rb") as f:
        cert = load_pem_x509_certificate(f.read())
    
    assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "test.example.com"
    assert cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value == "Test Org"
    assert cert.subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value == "US"

def test_csr_validation(security_manager):
    """Test CSR validation."""
    # Generate CSR
    csr = security_manager.generate_csr(
        common_name="test.example.com",
        organization="Test Org",
        country="US"
    )
    
    # Validate CSR
    assert "BEGIN CERTIFICATE REQUEST" in csr
    assert "END CERTIFICATE REQUEST" in csr
    assert "test.example.com" in csr
    assert "Test Org" in csr
    assert "US" in csr 