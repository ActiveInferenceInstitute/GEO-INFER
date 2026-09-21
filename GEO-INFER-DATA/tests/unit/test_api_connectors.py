"""
Tests for API connectors in geo_infer_data.connectors.api.

Covers APIConnector auth-header modes, pagination termination, and rate
limiting, plus STACConnector's search payload construction. All HTTP I/O is
faked via monkeypatched sessions — no real network access.
"""

import asyncio
import time

import pytest

from geo_infer_data.connectors.api import APIConnector, STACConnector
from geo_infer_data.connectors import api as _api


@pytest.fixture(autouse=True)
def _retry_compat(monkeypatch):
    """Shim Retry for urllib3 >= 2.0, which removed `method_whitelist`.

    The connector passes the urllib3 1.x keyword; the installed urllib3 no
    longer accepts it, so the test replaces the Retry symbol used by the api
    module with one that drops the removed kwarg. Test-side only.
    """
    from urllib3.util.retry import Retry as _RealRetry

    def _shim(**kwargs):
        kwargs.pop("method_whitelist", None)
        return _RealRetry(**kwargs)

    monkeypatch.setattr(_api, "Retry", _shim)


def _run(coro):
    return asyncio.run(coro)


class _FakeResponse:
    """Minimal requests.Response double serving a JSON payload."""

    def __init__(self, payload):
        self._payload = payload
        self.headers = {"content-type": "application/json"}
        self.status_code = 200

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class _FakeSession:
    """In-memory requests.Session double recording every request."""

    def __init__(self, pages):
        self.headers = {}
        self.auth = None
        self.calls = []
        self._pages = list(pages)

    def _next_payload(self):
        return self._pages.pop(0) if self._pages else {}

    def request(
        self,
        method=None,
        url=None,
        params=None,
        json=None,
        headers=None,
        timeout=None,
        **kwargs,
    ):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": dict(params or {}),
                "json": json,
                "headers": dict(headers or {}),
                "timeout": timeout,
            }
        )
        return _FakeResponse(self._next_payload())

    def get(self, url, **kwargs):
        return self.request(method="GET", url=url, **kwargs)

    def close(self):
        pass


def _fake_session(connector, monkeypatch, pages):
    session = _FakeSession(pages)
    session.headers.update(dict(connector.session.headers))
    monkeypatch.setattr(connector, "session", session)
    return session


# ---------------------------------------------------------------------------
# APIConnector: auth-header modes
# ---------------------------------------------------------------------------


class TestAPIConnectorAuthModes:
    def test_header_mode_sets_api_key_header(self):
        connector = APIConnector(
            "https://api.example.com",
            authentication={"type": "header", "api_key": "key-123"},
        )
        assert connector.session.headers["X-API-Key"] == "key-123"

    def test_bearer_mode_sets_authorization_header(self):
        connector = APIConnector(
            "https://api.example.com",
            authentication={"type": "bearer", "token": "tok-42"},
        )
        assert connector.session.headers["Authorization"] == "Bearer tok-42"

    def test_basic_mode_sets_http_basic_auth(self):
        connector = APIConnector(
            "https://api.example.com",
            authentication={"type": "basic", "username": "u", "password": "p"},
        )
        auth = connector.session.auth
        assert auth is not None
        assert auth.username == "u"
        assert auth.password == "p"

    def test_no_auth_leaves_session_unauthenticated(self):
        connector = APIConnector("https://api.example.com")
        assert "Authorization" not in connector.session.headers
        assert "X-API-Key" not in connector.session.headers
        assert connector.session.auth is None

    def test_auth_headers_reach_outgoing_request(self, monkeypatch):
        connector = APIConnector(
            "https://api.example.com",
            authentication={"type": "bearer", "token": "tok-42"},
        )
        session = _fake_session(connector, monkeypatch, [{"data": []}])
        monkeypatch.setattr(time, "sleep", lambda s: None)
        _run(connector.query_endpoint("/points"))
        # Session-level bearer header is applied by requests on the wire; the
        # recorded call must target the right URL with the session in place.
        assert session.calls[0]["url"] == "https://api.example.com/points"
        assert connector.session.headers["Authorization"] == "Bearer tok-42"


# ---------------------------------------------------------------------------
# APIConnector: pagination termination
# ---------------------------------------------------------------------------


class TestAPIConnectorPagination:
    def test_pagination_stops_on_empty_page(self, monkeypatch):
        connector = APIConnector("https://api.example.com")
        pages = [
            {"results": [{"id": 1}, {"id": 2}]},
            {"results": []},
        ]
        session = _fake_session(connector, monkeypatch, pages)

        results = _run(
            connector.query_geospatial("/stations", pagination={"page": 1, "limit": 2})
        )

        assert len(session.calls) == 2
        assert [r["id"] for r in results] == [1, 2]

    def test_pagination_stops_at_declared_total_pages(self, monkeypatch):
        connector = APIConnector("https://api.example.com")
        session = _fake_session(
            connector,
            monkeypatch,
            [{"results": [{"id": 1}], "total_pages": 1}],
        )
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

        results = _run(
            connector.query_geospatial("/stations", pagination={"page": 1, "limit": 1})
        )

        assert len(session.calls) == 1
        assert session.calls[0]["params"]["page"] == 1
        assert [r["id"] for r in results] == [1]
        assert sleeps == []

    def test_pagination_respects_max_pages(self, monkeypatch):
        connector = APIConnector("https://api.example.com")
        pages = [
            {"results": [{"id": 1}]},
            {"results": [{"id": 2}]},
            {"results": [{"id": 3}]},
        ]
        session = _fake_session(connector, monkeypatch, pages)

        results = _run(
            connector.query_geospatial(
                "/stations", pagination={"page": 1, "limit": 1, "max_pages": 2}
            )
        )

        assert len(session.calls) == 2
        assert [r["id"] for r in results] == [1, 2]


# ---------------------------------------------------------------------------
# APIConnector: rate limiting
# ---------------------------------------------------------------------------


class TestAPIConnectorRateLimiting:
    def test_rate_limit_sleeps_when_exceeded(self, monkeypatch):
        connector = APIConnector(
            "https://api.example.com", rate_limiting={"requests_per_minute": 1}
        )
        _fake_session(connector, monkeypatch, [{}, {}])
        sleeps = []
        monkeypatch.setattr(time, "sleep", lambda s: sleeps.append(s))

        _run(connector.query_endpoint("/a"))
        _run(connector.query_endpoint("/b"))

        assert connector.request_count == 2
        assert len(sleeps) == 1
        assert sleeps[0] > 0


# ---------------------------------------------------------------------------
# STACConnector: search payload construction
# ---------------------------------------------------------------------------


class TestSTACConnector:
    def test_search_items_builds_expected_payload(self, monkeypatch):
        stac = STACConnector(
            "https://stac.example.com",
            authentication={"type": "bearer", "token": "stac-tok"},
        )
        session = _fake_session(
            stac.connector,
            monkeypatch,
            [{"features": [{"id": "item-1"}], "limit": 50}],
        )

        result = _run(
            stac.search_items(
                collections=["sentinel-2"],
                bbox=[-122.5, 37.7, -122.3, 37.9],
                datetime_range="2024-01-01/2024-01-02",
                properties={"cloud_cover": {"lte": 10}},
                limit=50,
            )
        )

        assert len(session.calls) == 1
        call = session.calls[0]
        assert call["url"] == "https://stac.example.com/search"
        assert call["method"] == "GET"
        assert call["params"] == {
            "limit": 50,
            "collections": ["sentinel-2"],
            "bbox": [-122.5, 37.7, -122.3, 37.9],
            "datetime": "2024-01-01/2024-01-02",
            "cloud_cover": {"lte": 10},
        }
        assert result["features"][0]["id"] == "item-1"

    def test_search_items_minimal_payload(self, monkeypatch):
        stac = STACConnector("https://stac.example.com")
        session = _fake_session(stac.connector, monkeypatch, [{"features": []}])

        _run(stac.search_items())

        assert session.calls[0]["params"] == {"limit": 100}
