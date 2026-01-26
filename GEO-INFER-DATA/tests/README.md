# test
s

## Overvie
w

Test suite for GEO-INFER-DATA. This module contains tests for all GEO-INFER-DATA functionality including unit tests, integration tests, and performance tests.

## Test
 Structure

- **unit/**: Unit tests for individual components
- **integration/**: Integration tests for component interactions
- **performance/**: Performance tests and benchmarks
- **fixtures/**: Test data and fixtures

## Running
 Tests

```bash
# Run
 all tests
python -m pytest tests/

# Run
 unit tests only
python -m pytest tests/unit/

# Run
 integration tests
python -m pytest tests/integration/

# Run
 performance tests
python -m pytest tests/performance/

# Run
 with coverage
python -m pytest tests/ --cov=src/geo_infer_data

# Run
 specific test file
python -m pytest tests/unit/test_ingestion.py
```

## Test
 Coverage

### Uni
t
 Tests
- **test_ingestion.py**: Multi-source ingestion, connectors
- **test_storage.py**: Adaptive storage, backends
- **test_validation.py**: Data validation, quality management
- **test_api.py**: REST API, data service
- **test_error_handling.py**: Error handling across components

### Integratio
n
 Tests
- **test_end_to_end.py**: Complete workflows from ingestion to storage

### Performanc
e
 Tests
- **test_benchmarks.py**: Performance benchmarks for data operations

## Content
s

- **fixtures/**: Test data and fixtures
- **integration/**: Integration test suite
- **performance/**: Performance benchmarks
- **unit/**: Unit test suite

--- 