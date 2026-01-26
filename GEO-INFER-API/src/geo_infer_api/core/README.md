# core

## Overview

This directory contains core API framework components. It includes 3 Python modules implementing error handling, middleware, and configuration management.

## Components

### config.py

Configuration settings for the GEO-INFER-API.

**Classes**: `Settings`, `Config`

**Functions**: `get_settings`

### exceptions.py

Custom exceptions for the GEO-INFER-API.

**Classes**: `APIError`, `ValidationError`, `NotFoundError`, `ConflictError`, `GeometryError`, `ProcessingError`, `BadRequestError`

### middleware.py

Middleware for the GEO-INFER-API.

**Classes**: `ErrorHandlerMiddleware`, `RequestLoggingMiddleware`, `CORSHeadersMiddleware`

## Usage

```python
from geo_infer_api.core.settings import get_settings
from geo_infer_api.core.exceptions import ValidationError, NotFoundError
from geo_infer_api.core.middleware import ErrorHandlerMiddleware, CORSHeadersMiddleware

# Get settings
settings = get_settings()

# Use exceptions
try:
    # API logic
    pass
except ValidationError as e:
    error_dict = e.to_dict()

# Add middleware to FastAPI app
from fastapi import FastAPI
app = FastAPI()
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(CORSHeadersMiddleware)
```

## Integration

This directory provides core API functionality used by:
- `geo_infer_api.endpoints` for API endpoint implementations
- All GEO-INFER modules for API interfaces 