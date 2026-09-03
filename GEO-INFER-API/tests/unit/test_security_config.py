"""Tests for API security configuration: secret key, CORS, and health endpoints."""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from geo_infer_api.app import cors_allow_credentials
from geo_infer_api.core.config import Settings, get_settings

pytestmark = [pytest.mark.unit]


@pytest.fixture(autouse=True)
def restore_settings_cache():
    """Keep the lru_cache across tests consistent with the real environment."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


class TestSecretKeyRequired:
    def test_settings_without_secret_key_raises(self, monkeypatch):
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(Exception) as excinfo:
            Settings()
        assert "secret_key" in str(excinfo.value).lower()

    def test_get_settings_without_secret_key_raises(self, monkeypatch):
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            get_settings()

    def test_get_settings_uses_environment_secret(self, monkeypatch):
        monkeypatch.setenv("SECRET_KEY", "env-provided-secret")
        settings = get_settings()
        assert settings.secret_key == "env-provided-secret"

    def test_no_default_secret_baked_in(self):
        assert "secret_key" in Settings.model_fields
        assert Settings.model_fields["secret_key"].is_required()


class TestCorsPolicy:
    def test_wildcard_without_credentials_rejected(self):
        assert cors_allow_credentials(["*"]) is False

    def test_empty_origins_rejected(self):
        assert cors_allow_credentials([]) is False

    def test_explicit_origins_allowed(self):
        assert cors_allow_credentials(["https://app.example.com"]) is True

    def test_explicit_origins_with_wildcard_rejected(self):
        assert (
            cors_allow_credentials(["https://app.example.com", "*"]) is False
        )

    def test_wildcard_origin_gets_no_credentials_header(self):
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=cors_allow_credentials(["*"]),
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/probe")
        async def probe() -> dict:
            return {"ok": True}

        client = TestClient(app)
        response = client.get(
            "/probe", headers={"Origin": "https://evil.example.com"}
        )
        assert response.status_code == 200
        assert "access-control-allow-credentials" not in response.headers

    def test_explicit_origin_gets_credentials_header(self):
        origins = ["https://trusted.example.com"]
        app = FastAPI()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=cors_allow_credentials(origins),
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/probe")
        async def probe() -> dict:
            return {"ok": True}

        client = TestClient(app)
        response = client.get(
            "/probe", headers={"Origin": "https://trusted.example.com"}
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-credentials"] == "true"
        assert (
            response.headers["access-control-allow-origin"]
            == "https://trusted.example.com"
        )


class TestDocsEndpoints:
    def test_docs_served(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower()

    def test_redoc_served(self, client):
        response = client.get("/redoc")
        assert response.status_code == 200
        assert "redoc" in response.text.lower()


class TestHealthEndpoints:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_detailed(self, client):
        response = client.get("/health/detailed")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
