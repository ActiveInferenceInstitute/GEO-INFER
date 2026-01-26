# Agent
: tests

## Scop
e
This agent handles test suites for GEO-INFER-DATA including unit tests, integration tests, performance tests, and test fixtures.

## Implementation
 Status

### Currentl
y
 Implemented

- ✅ **Unit Tests**: Component-level testing for ingestion, storage, validation, API, and error handling
- ✅ **Integration Tests**: End-to-end testing for complete workflows
- ✅ **Performance Tests**: Benchmarking and performance validation
- ✅ **Test Fixtures**: Reusable test data and fixtures

## Test
 Structure

### uni
t
/
Unit tests for individual components:

- **test_ingestion.py**: Tests for `MultiSourceDataIngestion`, `SatelliteDataConnector`, `SensorDataConnector`, `CrowdsourcedDataConnector`
- **test_storage.py**: Tests for `AdaptiveDataStorage`, `PostgreSQLBackend`, `MinIOBackend`, `LocalFileBackend`
- **test_validation.py**: Tests for `GeospatialValidator`, `DataQualityManager`, `ValidationConfig`
- **test_api.py**: Tests for `DataAPI`, `DatasetAPI`, `DataService`
- **test_error_handling.py**: Tests for error handling across all components

### integratio
n
/
End-to-end integration tests:

- **test_end_to_end.py**: Complete workflow testing from ingestion through storage and validation

### performanc
e
/
Performance benchmarks:

- **test_benchmarks.py**: Performance benchmarks for data operations

### fixture
s
/
Reusable test data and fixtures for consistent testing.

## Running
 Tests

```bash
# Run
 all tests
pytest tests/

# Run
 unit tests only
pytest tests/unit/

# Run
 integration tests
pytest tests/integration/

# Run
 performance tests
pytest tests/performance/

# Run
 specific test file
pytest tests/unit/test_ingestion.py
```

## Integratio
n

- **Location**: `GEO-INFER-DATA/tests`
- **Purpose**: Quality assurance and validation
- **Test Framework**: pytest
- **Coverage**: Unit, integration, and performance testing

---

This AGENTS.md documents test suites for GEO-INFER-DATA.
