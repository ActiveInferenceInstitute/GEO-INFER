"""Tests for API middleware classes."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from geo_infer_api.core.middleware import (
    ErrorHandlerMiddleware,
    RequestLoggingMiddleware,
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

    @pytest.mark.asyncio
    async def test_converts_api_error_to_json(self):
        async def call_next(request):
            raise APIError(status_code=404, detail="Not found", error_code="NOT_FOUND")

        middleware = ErrorHandlerMiddleware(app=MagicMock())
        request = MagicMock()
        result = await middleware.dispatch(request, call_next)
        assert result.status_code == 404


class TestRequestLoggingMiddleware:
    @pytest.mark.asyncio
    async def test_adds_process_time_header(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}

        async def call_next(request):
            return mock_response

        middleware = RequestLoggingMiddleware(app=MagicMock())
        request = MagicMock()
        request.method = "GET"
        request.url = "http://testserver/health"
        result = await middleware.dispatch(request, call_next)
        assert "X-Process-Time" in result.headers
