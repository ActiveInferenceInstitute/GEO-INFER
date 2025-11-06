"""
Unit tests for authentication functionality.
"""

import pytest
from datetime import datetime, timedelta

from geo_infer_sec.core.authentication import (
    AuthenticationManager,
    UserCredentials,
    TokenInfo,
)


class TestAuthenticationManager:
    """Test AuthenticationManager class."""

    @pytest.fixture
    def auth_manager(self) -> AuthenticationManager:
        """Create an authentication manager instance."""
        return AuthenticationManager(secret_key="test_secret_key")

    def test_hash_password(self, auth_manager: AuthenticationManager) -> None:
        """Test password hashing."""
        password = "test_password_123"
        hash1, salt1 = auth_manager.hash_password(password)
        hash2, salt2 = auth_manager.hash_password(password, salt=bytes.fromhex(salt1.encode().hex()))

        assert hash1 != password
        assert len(hash1) > 0
        assert len(salt1) > 0

    def test_verify_password(self, auth_manager: AuthenticationManager) -> None:
        """Test password verification."""
        password = "test_password_123"
        password_hash, salt = auth_manager.hash_password(password)

        assert auth_manager.verify_password(password, password_hash, salt) is True
        assert auth_manager.verify_password("wrong_password", password_hash, salt) is False

    def test_register_user(self, auth_manager: AuthenticationManager) -> None:
        """Test user registration."""
        user = auth_manager.register_user(
            username="testuser",
            password="test_password_123",
            email="test@example.com",
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.enabled is True
        assert user.user_id is not None

    def test_register_user_duplicate(self, auth_manager: AuthenticationManager) -> None:
        """Test that duplicate user registration fails."""
        auth_manager.register_user(username="testuser", password="password123")

        with pytest.raises(ValueError, match="already exists"):
            auth_manager.register_user(username="testuser", password="password456")

    def test_register_user_short_password(self, auth_manager: AuthenticationManager) -> None:
        """Test that short passwords are rejected."""
        with pytest.raises(ValueError, match="at least"):
            auth_manager.register_user(username="testuser", password="short")

    def test_authenticate_success(self, auth_manager: AuthenticationManager) -> None:
        """Test successful authentication."""
        auth_manager.register_user(username="testuser", password="test_password_123")

        token_info = auth_manager.authenticate("testuser", "test_password_123")

        assert token_info is not None
        assert token_info.token is not None
        assert token_info.refresh_token is not None
        assert token_info.expires_in > 0

    def test_authenticate_failure(self, auth_manager: AuthenticationManager) -> None:
        """Test failed authentication."""
        auth_manager.register_user(username="testuser", password="test_password_123")

        token_info = auth_manager.authenticate("testuser", "wrong_password")

        assert token_info is None

    def test_validate_token(self, auth_manager: AuthenticationManager) -> None:
        """Test token validation."""
        auth_manager.register_user(username="testuser", password="test_password_123")
        token_info = auth_manager.authenticate("testuser", "test_password_123")

        payload = auth_manager.validate_token(token_info.token)

        assert payload is not None
        assert payload["username"] == "testuser"

    def test_validate_invalid_token(self, auth_manager: AuthenticationManager) -> None:
        """Test validation of invalid token."""
        payload = auth_manager.validate_token("invalid_token")

        assert payload is None

    def test_refresh_token(self, auth_manager: AuthenticationManager) -> None:
        """Test token refresh."""
        auth_manager.register_user(username="testuser", password="test_password_123")
        token_info = auth_manager.authenticate("testuser", "test_password_123")

        new_token_info = auth_manager.refresh_access_token(token_info.refresh_token)

        assert new_token_info is not None
        assert new_token_info.token is not None
        assert new_token_info.token != token_info.token

    def test_revoke_token(self, auth_manager: AuthenticationManager) -> None:
        """Test token revocation."""
        auth_manager.register_user(username="testuser", password="test_password_123")
        token_info = auth_manager.authenticate("testuser", "test_password_123")

        result = auth_manager.revoke_token(token_info.refresh_token)

        assert result is True

        # Try to refresh with revoked token
        new_token = auth_manager.refresh_access_token(token_info.refresh_token)
        assert new_token is None


