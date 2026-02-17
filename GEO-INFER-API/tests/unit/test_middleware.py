"""Tests for API middleware classes."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from geo_infer_api.core.middleware import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
    CORSHeadersMiddleware,
)
from geo_infer_api.core.exceptions import APIError


class TestErrorHandlerMiddleware:
    @pytest.mark.asyncio
    async def test_passes_through_normal_response(self):
        mock_response = MagicMock()
        mock_response.status_code = 200

        async def call_next(request):
            return mock_response

        middleware = ErrorHandlerMiddleware(app=MagicMock())
        request = MagicMock()
        result = await middleware.dispatch(request, call_next)
        assert result.status_code == 200


class TestCORSHeadersMiddleware:
    @pytest.mark.asyncio
    async def test_adds_cors_headers(self):
        mock_response = MagicMock()
        mock_response.headers = {}

        async def call_next(request):
            return mock_response

        middleware = CORSHeadersMiddleware(app=MagicMock())
        request = MagicMock()
        result = await middleware.dispatch(request, call_next)
        assert "Access-Control-Allow-Origin" in result.headers
        assert result.headers["Access-Control-Allow-Origin"] == "*"
