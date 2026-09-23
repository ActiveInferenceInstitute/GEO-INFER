"""Unit tests for the OPS FastAPI application entrypoint (M7-01).

Exercises create_app through TestClient: the config-fallback path,
health/version endpoints, the CORS wiring, and the conditional
Prometheus metrics mount.
"""

import pytest
from fastapi.testclient import TestClient

import geo_infer_ops
from geo_infer_ops.app import create_app

FALLBACK_CONFIG = {
    "service": {"host": "0.0.0.0", "port": 8000},
    "security": {"cors_origins": []},
    "monitoring": {"enabled": True, "metrics_path": "/metrics"},
    "logging": {"level": "INFO", "format": "json", "file": None},
    "development": {"hot_reload": False},
}


@pytest.fixture
def broken_config_loader(monkeypatch):
    """Force the app-level config loader to fail, triggering the fallback."""

    def _boom():
        raise RuntimeError("no config available")

    monkeypatch.setattr("geo_infer_ops.app.load_config", _boom)


def _configured_config(**overrides):
    """A fully-populated config whose shape satisfies the app loader block."""
    config = {
        "service": {"host": "127.0.0.1", "port": 9000},
        "security": {"cors_origins": ["http://testserver"]},
        "monitoring": {"enabled": True, "metrics_path": "/observability/metrics"},
        "logging": {"level": "INFO", "format": "text", "file": None},
        "development": {"hot_reload": False},
    }
    config.update(overrides)
    return config


class TestCreateAppFallbackPath:
    """The except-branch fallback configuration drives a working app."""

    def test_fallback_config_exposed_on_app_state(self, broken_config_loader) -> None:
        app = create_app()
        assert app.state.config == FALLBACK_CONFIG
        assert app.title == "GEO-INFER-OPS"
        assert app.version == geo_infer_ops.__version__

    def test_fallback_health_and_version(self, broken_config_loader) -> None:
        client = TestClient(create_app())

        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        version = client.get("/version")
        assert version.status_code == 200
        assert version.json() == {"version": geo_infer_ops.__version__}

    def test_fallback_mounts_default_metrics_path(self, broken_config_loader) -> None:
        """Fallback enables monitoring → /metrics serves Prometheus text."""
        client = TestClient(create_app())

        response = client.get("/metrics")
        assert response.status_code == 200
        assert "python_info" in response.text

    def test_fallback_rejects_unknown_cors_origin(self, broken_config_loader) -> None:
        """Empty fallback origins deny preflights from any origin."""
        client = TestClient(create_app())
        preflight = client.options(
            "/health",
            headers={
                "Origin": "http://stranger.example",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert preflight.status_code == 400


class TestConfiguredApp:
    """A loadable config drives CORS and the metrics mount path."""

    @pytest.fixture
    def configured_client(self, monkeypatch) -> TestClient:
        monkeypatch.setattr(
            "geo_infer_ops.app.load_config", lambda: _configured_config()
        )
        return TestClient(create_app())

    def test_allowed_origin_preflight_echoed(self, configured_client) -> None:
        response = configured_client.options(
            "/health",
            headers={
                "Origin": "http://testserver",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://testserver"

    def test_metrics_mounted_at_configured_path(self, configured_client) -> None:
        response = configured_client.get("/observability/metrics")
        assert response.status_code == 200
        assert "python_info" in response.text

    def test_configured_config_exposed_on_app_state(self, configured_client) -> None:
        client = configured_client
        app_state_config = client.app.state.config  # type: ignore[attr-defined]
        assert app_state_config == _configured_config()


class TestMonitoringDisabled:
    """monitoring.enabled=False removes the metrics route entirely."""

    def test_no_metrics_route_when_disabled(self, monkeypatch) -> None:
        monkeypatch.setattr(
            "geo_infer_ops.app.load_config",
            lambda: _configured_config(
                monitoring={"enabled": False, "metrics_path": "/metrics"}
            ),
        )
        client = TestClient(create_app())

        assert client.get("/metrics").status_code == 404
        # Core endpoints keep working.
        assert client.get("/health").json() == {"status": "ok"}
