# Agent: fixtures

## Scope
This agent handles test fixtures and reusable test data for GEO-INFER-DATA testing.

## Implementation Status

### Currently Implemented

- ✅ **Test Data**: Sample geospatial datasets for testing
- ✅ **Mock Data**: Mock data generators for various formats
- ✅ **Test Utilities**: Helper functions for test setup and teardown

## Fixture Types

### Geospatial Data Fixtures
- Sample GeoJSON files
- Sample Shapefiles
- Sample raster data
- Sample H3-indexed data

### Mock Data Generators
- Mock satellite data
- Mock sensor data
- Mock crowdsourced data

## Usage

```python
from tests.fixtures import sample_geodataframe, mock_satellite_data

# Use fixtures in tests
def test_ingestion(sample_geodataframe):
    result = ingestion.ingest(sample_geodataframe)
    assert result is not None
```

## Integration

- **Location**: `GEO-INFER-DATA/tests/fixtures`
- **Purpose**: Reusable test data and fixtures
- **Used By**: Unit and integration tests

---

This AGENTS.md documents test fixtures for GEO-INFER-DATA.
