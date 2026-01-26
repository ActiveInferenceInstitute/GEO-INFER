# Agent: unit

## Scope
This agent handles unit tests for individual GEO-INFER-DATA components including ingestion, storage, validation, API, and error handling.

## Implementation Status

### Currently Implemented

- ✅ **test_ingestion.py**: Tests for `MultiSourceDataIngestion`, `SatelliteDataConnector`, `SensorDataConnector`, `CrowdsourcedDataConnector`
- ✅ **test_storage.py**: Tests for `AdaptiveDataStorage`, `PostgreSQLBackend`, `MinIOBackend`, `LocalFileBackend`
- ✅ **test_validation.py**: Tests for `GeospatialValidator`, `DataQualityManager`, `ValidationConfig`
- ✅ **test_api.py**: Tests for `DataAPI`, `DatasetAPI`, `DataService`
- ✅ **test_error_handling.py**: Tests for error handling across all components

## Test Classes

### TestMultiSourceDataIngestion
Tests for multi-source data ingestion functionality.

**Test Methods**:
- `test_ingest_multi_source()`
- `test_validate_and_clean()`
- `test_format_detection()`

### TestAdaptiveDataStorage
Tests for adaptive data storage operations.

**Test Methods**:
- `test_store_geospatial_data()`
- `test_adaptive_query()`
- `test_storage_optimization()`

### TestGeospatialValidator
Tests for geospatial data validation.

**Test Methods**:
- `test_validate_geometries()`
- `test_validate_coordinates()`
- `test_validate_attributes()`

### TestDataAPI
Tests for REST API functionality.

**Test Methods**:
- `test_api_start_stop()`
- `test_list_datasets()`
- `test_create_dataset()`

### TestIngestionErrorHandling
Tests for error handling in ingestion operations.

## Running Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_ingestion.py

# Run with coverage
pytest tests/unit/ --cov=src/geo_infer_data
```

## Integration

- **Location**: `GEO-INFER-DATA/tests/unit`
- **Purpose**: Component-level unit testing
- **Test Framework**: pytest
- **Coverage**: Individual component functionality

---

This AGENTS.md documents unit tests for GEO-INFER-DATA.
