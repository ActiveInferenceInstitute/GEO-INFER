"""
Middleware for the GEO-INFER-API.
"""
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .exceptions import APIError


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware for handling API errors consistently."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle requests and convert API exceptions to proper HTTP responses."""
        try:
            response = await call_next(request)
            return response
        except APIError as e:
            # Convert APIError to JSON response
            return JSONResponse(
                status_code=e.status_code,
                content=e.to_dict()
            )
        except Exception as e:
            # Handle unexpected errors
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "status_code": 500
                    }
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging API requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log API requests."""
        start_time = time.time()

        # Log request
        print(f"API Request: {request.method} {request.url}")

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        print(f"API Response: {response.status_code} in {process_time:.3f}s")

        # Add processing time to response headers
        response.headers["X-Process-Time"] = str(process_time)

        return response


class CORSHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding CORS headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add CORS headers to responses."""
        response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-API-Key"

        return response
