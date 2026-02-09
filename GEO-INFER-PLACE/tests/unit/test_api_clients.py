#!/usr/bin/env python3
"""
Tests for GEO-INFER-PLACE API clients.

Validates client initialization, URL construction,
and retry logic (using a mock HTTP server).
"""

import pytest
from unittest.mock import patch, MagicMock

from geo_infer_place.core.api_clients import (
    CaliforniaAPIManager,
    CALFIREClient,
    NOAAClient,
    USGSClient,
    USGSEarthquakeClient,
    CDECClient,
    _fetch_with_retry,
)


# -- Client instantiation -------------------------------------------------

class TestClientInit:
    """Test that API clients initialise without external calls."""

    def test_calfire_client(self):
        client = CALFIREClient()
        assert "arcgis" in client.base_url.lower() or "fire" in client.base_url.lower()
        assert client.session is not None

    def test_noaa_client(self):
        client = NOAAClient()
        assert "tidesandcurrents" in client.base_url or "noaa" in client.base_url
        assert hasattr(client, "weather_url")

    def test_usgs_client(self):
        client = USGSClient()
        assert "usgs" in client.base_url.lower()

    def test_earthquake_client(self):
        client = USGSEarthquakeClient()
        assert "earthquake" in client.base_url.lower()

    def test_cdec_client(self):
        client = CDECClient()
        assert "cdec" in client.base_url.lower()


class TestCaliforniaAPIManager:
    """Test the aggregator class."""

    def test_manager_has_all_clients(self):
        mgr = CaliforniaAPIManager()
        assert hasattr(mgr, "calfire")
        assert hasattr(mgr, "noaa")
        assert hasattr(mgr, "usgs")
        assert hasattr(mgr, "usgs_eq")
        assert hasattr(mgr, "cdec")


# -- retry logic -----------------------------------------------------------

class TestRetryLogic:
    """Test _fetch_with_retry helper."""

    def test_returns_json_on_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {"ok": True}

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        result = _fetch_with_retry(mock_session, "https://example.com/api", max_retries=0)
        assert result == {"ok": True}

    def test_returns_error_on_4xx(self):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        result = _fetch_with_retry(mock_session, "https://example.com/missing", max_retries=0)
        assert "error" in result
        assert result["error"]["status"] == 404

    def test_retries_on_connection_error(self):
        """Should retry on ConnectionError and eventually return error."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("refused")

        result = _fetch_with_retry(
            mock_session, "https://example.com/down",
            max_retries=1, timeout=1,
        )
        assert "error" in result
        assert mock_session.get.call_count == 2  # initial + 1 retry


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
