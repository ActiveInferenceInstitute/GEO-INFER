---
name: geo-infer-api
description: REST API endpoints for geospatial services. Use when building API routes, defining spatial query endpoints, or exposing GEO-INFER functionality as web services.
prerequisites:
  required:
    - geo-infer-data
  recommended:
    - geo-infer-space
    - geo-infer-time
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-API

## Instructions

### Core Capabilities

- **REST endpoints**: FastAPI app with health, GeoJSON feature, and processing-algorithm routes (`/api/v1`)
- **GeoJSON utilities**: RFC 7946 models plus validation, ray-cast containment, buffering, and RDP simplification helpers
- **Middleware**: error handling and request logging wired into `create_app`
- **CORS**: explicit, wildcard-free origin lists enable credentialed CORS (fail-closed)

Out of scope for this module: GraphQL schema, JWT/API-key authentication middleware, rate limiting. There is no auth middleware today; `SECRET_KEY` is a required fail-closed setting only.

### Key Imports

```python
from geo_infer_api.app import create_app
from geo_infer_api.core.config import Settings, get_settings
from geo_infer_api.core.middleware import ErrorHandlerMiddleware, RequestLoggingMiddleware
from geo_infer_api import (
    Feature, FeatureCollection, Polygon, PolygonFeature,
)
from geo_infer_api.utils.geojson_helpers import (
    polygon_contains_point, create_buffer, simplify_polygon,
    calculate_polygon_area, validate_polygon_rings,
)
```

### Examples

Build the FastAPI application (requires `SECRET_KEY` to be set):

```python
import os
os.environ["SECRET_KEY"] = "change-me"

from geo_infer_api.app import create_app
app = create_app()  # serve with: uvicorn geo_infer_api.app:main_app
```

Point-in-polygon and buffering on GeoJSON polygons:

```python
from geo_infer_api.utils.geojson_helpers import polygon_contains_point, create_buffer

square = {"type": "Polygon", "coordinates": [[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]]}
assert polygon_contains_point(square, (5.0, 5.0)) is True
buffered = create_buffer(square, distance=1.0, unit="kilometers")
```

## Guidelines

- FastAPI with async handlers for spatial operations
- Response format defaults to GeoJSON (RFC 7946, `[lon, lat]` coordinate order)
- The polygon feature store is process-local memory — data does not survive worker restarts
- Test: `uv run python -m pytest GEO-INFER-API/tests/ -v`

### Integrations

- **SEC** → JWT/API-key authentication middleware
- **DATA** → Spatial query endpoint data sources
- **SPACE** → H3 and geographic query parameters (algorithms router proxies `geo_infer_space.core.algorithm_registry` when installed; 503 otherwise)
- **OPS** → API monitoring via `/health`
- **APP** → Frontend consuming API endpoints
