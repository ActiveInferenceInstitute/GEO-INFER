---
name: geo-infer-api
description: REST and GraphQL API endpoints for geospatial services. Use when building API routes, defining spatial query endpoints, or exposing GEO-INFER functionality as web services.
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

- **REST endpoints**: FastAPI-based spatial query and analysis routes
- **GraphQL**: Schema for complex spatial queries
- **Authentication**: JWT/API key middleware
- **Rate limiting**: Per-endpoint and per-user throttling
- **Serialization**: GeoJSON response formatting

### Key Imports

```python
from geo_infer_api.core.router import SpatialRouter
from geo_infer_api.core.middleware import AuthMiddleware
from geo_infer_api.core.serializers import GeoJSONSerializer
```

## Examples

```python
from geo_infer_api.core.router import SpatialRouter
from geo_infer_api.core.serializers import GeoJSONSerializer

router = SpatialRouter(prefix="/v1/spatial")

@router.get("/query")
async def spatial_query(lat: float, lng: float, radius_km: float):
    results = await spatial_engine.query_radius(lat, lng, radius_km)
    return GeoJSONSerializer.to_feature_collection(results)

# Register with FastAPI app
app.include_router(router)
```

```python
from geo_infer_api.core.middleware import AuthMiddleware

# JWT authentication middleware
app.add_middleware(AuthMiddleware, secret_key="your-key", algorithm="HS256")
```

## Guidelines

- FastAPI with async handlers for spatial operations
- Response format defaults to GeoJSON (RFC 7946)
- Test: `uv run python -m pytest GEO-INFER-API/tests/ -v`

### Integrations

- **SEC** → JWT/API key authentication middleware
- **DATA** → Spatial query endpoint data sources
- **SPACE** → H3 and geographic query parameters
- **OPS** → API monitoring and rate limiting metrics
- **APP** → Frontend consuming API endpoints
