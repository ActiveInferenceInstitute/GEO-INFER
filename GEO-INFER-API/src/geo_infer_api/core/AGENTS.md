# Agent: core

## Scope

This directory contains core API framework components for the module. It provides 12 classes and 1 function implementing error handling, middleware, configuration management, and API settings.

## Classes and Functions

### Settings

Application settings with environment variable support.

**Methods**:
- `assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]`: Parse CORS origins from string or list.

### Config

Configuration class for API settings.

### APIError

Base exception for API errors.

**Methods**:
- `to_dict() -> Dict[str, Any]`: Convert exception to dictionary for JSON response.

### ValidationError

Exception raised for validation errors.

### NotFoundError

Exception raised when a resource is not found.

### ConflictError

Exception raised when there's a conflict (e.g., duplicate resource).

### GeometryError

Exception raised for geometry-related errors.

### ProcessingError

Exception raised for processing-related errors.

### BadRequestError

Exception raised for bad request errors.

### ErrorHandlerMiddleware

Middleware for handling API errors consistently.

### RequestLoggingMiddleware

Middleware for logging API requests.

### CORSHeadersMiddleware

Middleware for adding CORS headers to responses.

### get_settings

`get_settings() -> Settings`

Get cached settings to avoid reloading from env every time.

## Capabilities

- **Error Handling**: Exception classes for API errors (ValidationError, NotFoundError, ConflictError, etc.)
- **Middleware**: Request logging, CORS headers, and error handling middleware
- **Configuration**: Settings management with environment variable support

## Agent Capabilities

### 1. Error Handling

```python
from geo_infer_api.core import APIError, ValidationError, NotFoundError

# Raise API errors
raise ValidationError(detail="Invalid input data", error_code="VALIDATION_001")
raise NotFoundError(detail="Resource not found", error_code="NOT_FOUND_001")```

### 2. Middleware

```python
from geo_infer_api.core import ErrorHandlerMiddleware, RequestLoggingMiddleware, CORSHeadersMiddleware

# Add middleware to FastAPI app
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CORSHeadersMiddleware)```

### 3. Configuration

```python
from geo_infer_api.core import get_settings

# Get application settings
settings = get_settings()
print(f"API prefix: {settings.api_prefix}")
print(f"CORS origins: {settings.cors_origins}")```

## Integration

- **Location**: `GEO-INFER-API/src/geo_infer_api/core`
- **Type**: Core Module Component
- **Dependencies**: `fastapi`, `pydantic`, `pydantic-settings`
- **Used By**: 
 
- `geo_infer_api.endpoints` for API endpoint implementations
  - All GEO-INFER modules for API interfaces
- **Provides**: Core API framework components for error handling, middleware, and configuration

---

This AGENTS.md documents core API framework components for GEO-INFER-API.
