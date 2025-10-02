# GEO-INFER-API Test Suite

This directory contains comprehensive tests for the GEO-INFER-API module, providing RESTful APIs and web services for the GEO-INFER framework.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                    # Test configuration and fixtures
├── test_geojson_helpers.py       # GeoJSON utility tests
├── test_geojson_router.py        # GeoJSON API endpoint tests
├── test_health_router.py         # Health check endpoint tests
├── test_spatial_router.py        # Spatial analysis endpoint tests
└── integration/
    └── test_api_integration.py   # Cross-endpoint integration tests
```

## Test Categories

### Unit Tests

#### GeoJSON Helpers
**File**: `test_geojson_helpers.py`

Tests GeoJSON manipulation utilities:

```python
def test_validate_polygon_rings_valid():
    """Test validation of valid polygon rings."""
    coordinates = [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
    assert validate_polygon_rings(coordinates) == True

def test_calculate_polygon_area():
    """Test polygon area calculation."""
    polygon = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
    area = calculate_polygon_area(polygon)
    assert area > 0

def test_polygon_contains_point():
    """Test point-in-polygon functionality."""
    polygon = {"type": "Polygon", "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]]}
    point = [1, 1]
    assert polygon_contains_point(polygon, point) == True
```

#### API Endpoints
**File**: `test_geojson_router.py`

Tests REST API endpoint functionality:

```python
def test_list_collections(client):
    """Test listing available collections."""
    response = client.get("/api/v1/geojson/collections")
    assert response.status_code == 200
    data = response.get_json()
    assert "collections" in data

def test_create_collection(client):
    """Test creating new collection."""
    collection_data = {
        "type": "FeatureCollection",
        "features": []
    }
    response = client.post("/api/v1/geojson/collections", json=collection_data)
    assert response.status_code == 201

def test_get_collection(client):
    """Test retrieving specific collection."""
    collection_id = "test_collection"
    response = client.get(f"/api/v1/geojson/collections/{collection_id}")
    # Collection not found initially
    assert response.status_code == 404
```

### Integration Tests

**File**: `integration/test_api_integration.py`

Tests cross-endpoint integration:

```python
def test_full_collection_workflow(client):
    """Test complete collection lifecycle."""
    # Create collection
    collection_data = {"type": "FeatureCollection", "features": []}
    create_response = client.post("/api/v1/geojson/collections", json=collection_data)
    assert create_response.status_code == 201

    collection_id = create_response.get_json()["collection_id"]

    # Add feature to collection
    feature_data = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [0, 0]},
        "properties": {"name": "Test Point"}
    }
    add_response = client.post(f"/api/v1/geojson/collections/{collection_id}/features", json=feature_data)
    assert add_response.status_code == 201

    # Retrieve collection
    get_response = client.get(f"/api/v1/geojson/collections/{collection_id}")
    assert get_response.status_code == 200

    collection = get_response.get_json()
    assert len(collection["features"]) == 1
    assert collection["features"][0]["properties"]["name"] == "Test Point"
```

## Running Tests

### Basic Test Execution

```bash
# Run all API tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_geojson_router.py

# Run specific test function
python -m pytest tests/test_geojson_router.py::test_list_collections
```

### Test with Coverage

```bash
# Generate coverage report
python -m pytest --cov=geo_infer_api --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

### Test Configuration

Tests use the following configuration:

- **Test Client**: FastAPI TestClient for endpoint testing
- **Database**: In-memory database for isolation
- **Fixtures**: Shared test data and setup
- **Mocking**: External service mocking where needed

### Test Fixtures

Common test fixtures in `conftest.py`:

```python
@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def sample_polygon_feature():
    """Sample polygon feature for testing."""
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        },
        "properties": {"name": "Test Polygon"}
    }
```

## Test Data

Test data is generated programmatically:

- **Sample GeoJSON**: Valid polygon and point features
- **Mock Responses**: Simulated external API responses
- **Error Cases**: Invalid data for error handling tests

## API Testing Best Practices

### Endpoint Testing

1. **Test all HTTP methods** (GET, POST, PUT, DELETE)
2. **Test status codes** (200, 201, 400, 404, 500)
3. **Test request/response schemas**
4. **Test error conditions**
5. **Test authentication/authorization**

### Data Validation

1. **Test valid input acceptance**
2. **Test invalid input rejection**
3. **Test boundary conditions**
4. **Test data type validation**
5. **Test schema compliance**

### Performance Testing

1. **Test response times** for typical requests
2. **Test concurrent request handling**
3. **Test large payload processing**
4. **Test database query performance**

## Test Coverage Goals

- **API Endpoints**: 100% coverage
- **Business Logic**: >90% coverage
- **Error Handling**: Complete coverage
- **Integration Points**: Cross-module testing
- **Performance**: Benchmark critical operations

## Writing New Tests

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient

class TestNewEndpoint:
    """Test suite for new API endpoint."""

    def test_endpoint_success(self, client):
        """Test successful endpoint operation."""
        response = client.get("/api/v1/new-endpoint")
        assert response.status_code == 200
        data = response.get_json()
        assert "result" in data

    def test_endpoint_validation_error(self, client):
        """Test endpoint with invalid input."""
        response = client.post("/api/v1/new-endpoint", json={"invalid": "data"})
        assert response.status_code == 400

    def test_endpoint_not_found(self, client):
        """Test endpoint with non-existent resource."""
        response = client.get("/api/v1/new-endpoint/999")
        assert response.status_code == 404
```

### Test Data Management

```python
def create_test_data():
    """Create test data for API testing."""
    return {
        "valid_polygon": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
            },
            "properties": {"name": "Test"}
        },
        "invalid_polygon": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[0, 0], [1, 0], [1, 1]]]  # Not closed
            }
        }
    }
```

## Debugging Tests

### Common Issues

1. **Database State**: Tests may interfere with each other
2. **Async Issues**: API may be async but tests are sync
3. **Configuration**: Test environment may differ from production
4. **External Dependencies**: Mock external services properly

### Debugging Tools

```bash
# Run with verbose output
python -m pytest -v tests/test_geojson_router.py

# Run with debugging
python -m pytest --pdb tests/test_geojson_router.py::test_create_collection

# Run specific test with output
python -m pytest -s tests/test_geojson_router.py::test_list_collections
```

## Contributing

1. **Add tests for new endpoints** before implementation
2. **Maintain test coverage** above 90%
3. **Include integration tests** for new features
4. **Test error conditions** comprehensively
5. **Update this README** for new test categories
