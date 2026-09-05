"""Tests for API configuration settings."""

import os
import pytest


class TestSettings:
    def test_get_settings_returns_object(self):
        from geo_infer_api.core.config import get_settings
        settings = get_settings()
        assert settings.app_name == "GEO-INFER-API"
        assert settings.app_version == "0.2.0"
        assert settings.api_prefix == "/api/v1"

    def test_cors_origins_default(self):
        from geo_infer_api.core.config import get_settings
        settings = get_settings()
        assert isinstance(settings.cors_origins, list)

    def test_cors_origins_json_string(self):
        """A JSON-array CORS_ORIGINS string parses into a real list."""
        from geo_infer_api.core.config import Settings
        settings = Settings(
            secret_key="test-secret",
            cors_origins='["https://a.example.com", "https://b.example.com"]',
            _env_file=None,
        )
        assert settings.cors_origins == ["https://a.example.com", "https://b.example.com"]

    def test_cors_origins_comma_string(self):
        """A comma-separated CORS_ORIGINS string parses into a list."""
        from geo_infer_api.core.config import Settings
        settings = Settings(
            secret_key="test-secret",
            cors_origins="https://a.example.com, https://b.example.com",
            _env_file=None,
        )
        assert settings.cors_origins == ["https://a.example.com", "https://b.example.com"]

    def test_ogc_features_enabled(self):
        from geo_infer_api.core.config import get_settings
        settings = get_settings()
        assert settings.ogc_api_features_enabled is True
        assert settings.ogc_api_processes_enabled is True
