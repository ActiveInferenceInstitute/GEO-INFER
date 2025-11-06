# GEO-INFER-API Source Code

This directory contains the core implementation of the GEO-INFER-API module, providing RESTful APIs and web services for the GEO-INFER framework.

## Directory Structure

```
src/
├── geo_infer_api/
│   ├── __init__.py                    # Package initialization
│   ├── app.py                        # Main FastAPI application
│   ├── core/                         # Core API functionality
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuration management
│   │   ├── middleware.py             # Custom middleware
│   │   └── exceptions.py             # Custom exceptions
│   ├── endpoints/                    # API endpoint definitions
│   │   ├── __init__.py
│   │   ├── geojson_router.py         # GeoJSON API endpoints
│   │   ├── health_router.py          # Health check endpoints
│   │   └── spatial_router.py         # Spatial analysis endpoints
│   ├── models/                       # Data models and schemas
│   │   ├── __init__.py
│   │   ├── geojson.py                # GeoJSON data models
│   │   └── request_response.py       # API request/response models
│   ├── services/                     # Business logic services
│   │   ├── __init__.py
│   │   ├── spatial_service.py        # Spatial analysis service
│   │   └── data_service.py           # Data management service
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── geojson_helpers.py        # GeoJSON manipulation utilities
│       ├── validation.py             # Input validation utilities
│       └── serialization.py          # Data serialization helpers
```

## Core Components

### FastAPI Application

**Location**: `app.py`

Main FastAPI application with configuration:

```python
from geo_infer_api.app import create_app

# Create and configure FastAPI app
app = create_app()

# Add custom middleware
app.add_middleware(AuthenticationMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include API routers
app.include_router(geojson_router, prefix="/api/v1/geojson")
app.include_router(spatial_router, prefix="/api/v1/spatial")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Configuration Management

**Location**: `core/config.py`

Centralized configuration management:

```python
from geo_infer_api.core.config import Settings, get_settings

# Get application settings
settings = get_settings()

# Access configuration values
database_url = settings.database_url
api_version = settings.api_version
```

### GeoJSON API Endpoints

**Location**: `endpoints/geojson_router.py`

GeoJSON-specific API endpoints:

```python
from geo_infer_api.endpoints.geojson_router import router as geojson_router

@router.get("/collections", summary="List available feature collections")
async def list_collections(settings: Settings = Depends(get_settings)):
    """List all available GeoJSON collections"""
    collections = await get_collections()
    return collections

@router.post("/collections", summary="Create new collection")
async def create_collection(collection: GeoJSONFeatureCollection):
    """Create a new GeoJSON feature collection"""
    collection_id = await save_collection(collection)
    return {"collection_id": collection_id}
```

### Spatial Analysis Endpoints

**Location**: `endpoints/spatial_router.py`

Spatial analysis and processing endpoints:

```python
from geo_infer_api.endpoints.spatial_router import router as spatial_router

@router.post("/analysis/buffer", summary="Create buffer analysis")
async def buffer_analysis(geometry: dict, distance: float, unit: str = "meters"):
    """Create buffer around geometry"""
    buffered = await create_buffer(geometry, distance, unit)
    return buffered

@router.post("/analysis/intersection", summary="Compute intersection")
async def intersection_analysis(geometries: list):
    """Compute intersection of multiple geometries"""
    intersection = await compute_intersection(geometries)
    return intersection
```

## Data Models

### GeoJSON Models

**Location**: `models/geojson.py`

Pydantic models for GeoJSON data:

```python
from geo_infer_api.models.geojson import (
    Point, LineString, Polygon, Feature, FeatureCollection
)

# Create GeoJSON Point
point = Point(coordinates=[-122.4194, 37.7749])

# Create GeoJSON Feature
feature = Feature(
    geometry=point,
    properties={"name": "San Francisco", "population": 883305}
)

# Create GeoJSON FeatureCollection
collection = FeatureCollection(features=[feature])
```

### Request/Response Models

**Location**: `models/request_response.py`

API request and response models:

```python
from geo_infer_api.models.request_response import (
    APIResponse, ErrorResponse, PaginationParams
)

# Standard API response
response = APIResponse(
    success=True,
    data=feature_collection,
    message="Features retrieved successfully"
)

# Error response
error = ErrorResponse(
    success=False,
    error_code="NOT_FOUND",
    message="Feature collection not found"
)
```

## Services Layer

### Spatial Analysis Service

**Location**: `services/spatial_service.py`

Business logic for spatial operations:

```python
from geo_infer_api.services.spatial_service import SpatialService

# Initialize spatial service
spatial_service = SpatialService()

# Perform buffer analysis
buffered_geometry = spatial_service.buffer_analysis(
    geometry=point_geometry,
    distance=1000,
    unit="meters"
)

# Compute spatial intersections
intersection = spatial_service.intersection_analysis(
    geometries=[polygon1, polygon2]
)
```

### Data Management Service

**Location**: `services/data_service.py`

Business logic for data management:

```python
from geo_infer_api.services.data_service import DataService

# Initialize data service
data_service = DataService()

# Save GeoJSON collection
collection_id = data_service.save_collection(
    collection=feature_collection,
    name="San Francisco Points"
)

# Retrieve collection
retrieved = data_service.get_collection(collection_id)
```

## Utility Functions

### GeoJSON Helpers

**Location**: `utils/geojson_helpers.py`

Utilities for GeoJSON manipulation:

```python
from geo_infer_api.utils.geojson_helpers import (
    validate_polygon_rings, calculate_polygon_area, polygon_contains_point
)

# Validate polygon geometry
is_valid = validate_polygon_rings(coordinates)

# Calculate polygon area
area = calculate_polygon_area(polygon_geometry)

# Check point-in-polygon
contains = polygon_contains_point(polygon_geometry, point_coordinates)
```

### Validation Utilities

**Location**: `utils/validation.py`

Input validation utilities:

```python
from geo_infer_api.utils.validation import (
    validate_geojson, validate_coordinates, validate_bbox
)

# Validate GeoJSON structure
is_valid = validate_geojson(geojson_data)

# Validate coordinate bounds
is_valid = validate_coordinates(latitude, longitude)

# Validate bounding box
is_valid = validate_bbox(min_lon, min_lat, max_lon, max_lat)
```

### Serialization Helpers

**Location**: `utils/serialization.py`

Data serialization utilities:

```python
from geo_infer_api.utils.serialization import (
    serialize_geojson, deserialize_geojson, convert_to_geojson
)

# Serialize to GeoJSON
geojson_data = serialize_geojson(spatial_dataframe)

# Deserialize from GeoJSON
dataframe = deserialize_geojson(geojson_data)

# Convert other formats to GeoJSON
geojson = convert_to_geojson(spatial_data, format="shapefile")
```

## API Documentation

### OpenAPI Schema

The API automatically generates OpenAPI documentation:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

### API Features

#### Health Check
```bash
GET /health
```

#### GeoJSON Collections
```bash
GET /api/v1/geojson/collections
POST /api/v1/geojson/collections
GET /api/v1/geojson/collections/{collection_id}
```

#### Spatial Analysis
```bash
POST /api/v1/spatial/analysis/buffer
POST /api/v1/spatial/analysis/intersection
POST /api/v1/spatial/analysis/union
```

## Development Guidelines

### Adding New Endpoints

1. Create endpoint handler in appropriate `endpoints/` file
2. Define request/response models in `models/`
3. Implement business logic in appropriate `services/` file
4. Add comprehensive tests
5. Update API documentation

### Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings
- Write unit tests for all new functionality
- Follow established patterns from existing endpoints

### Testing

Run the API test suite:
```bash
python -m pytest tests/
```

Run specific endpoint tests:
```bash
python -m pytest tests/test_geojson_router.py
```

## Integration Points

The API module integrates with other GEO-INFER modules:

- **All GEO-INFER modules**: Provides RESTful access to all framework capabilities
- **GEO-INFER-DATA**: Data management and storage
- **GEO-INFER-SPACE**: Spatial analysis and processing
- **GEO-INFER-TIME**: Temporal analysis and processing
- **External systems**: RESTful integration with external applications

## Deployment

### Development Server

```bash
# Start development server
uvicorn geo_infer_api.app:app --host 0.0.0.0 --port 8000 --reload
```

### Production Deployment

```bash
# Start with production settings
uvicorn geo_infer_api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN uv pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "geo_infer_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dependencies

Core dependencies managed through main GEO-INFER framework:

- `fastapi`: Modern, fast web framework
- `uvicorn`: ASGI server for FastAPI
- `pydantic`: Data validation and serialization
- `geopandas`: Geospatial data handling
- `shapely`: Geometric operations
- `python-multipart`: Form data handling
- `jinja2`: Template rendering

## Configuration

Configure API module in `config/api_config.yaml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  timeout: 30

  cors:
    origins: ["*"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["*"]

  rate_limiting:
    enabled: true
    default_limit: "100 per minute"

  authentication:
    enabled: false
    secret_key: "your-secret-key"
    algorithm: "HS256"

  logging:
    level: "INFO"
    format: "json"
    file: "logs/api.log"
```

## Performance Considerations

- Use efficient serialization for large GeoJSON responses
- Implement caching for frequently accessed data
- Optimize spatial operations for large datasets
- Monitor API response times and error rates
- Implement proper pagination for large result sets