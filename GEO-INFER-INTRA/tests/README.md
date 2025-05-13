# GEO-INFER Test Infrastructure

This directory contains the comprehensive test infrastructure for the GEO-INFER framework. The test infrastructure is designed to work across all modules and support various types of testing.

## Directory Structure

```
tests/
├── conftest.py           # Shared fixtures and test configuration
├── unit/                 # Unit tests
├── integration/          # Integration tests
├── system/               # System tests
├── performance/          # Performance tests
├── utils/                # Test utilities
│   ├── __init__.py       # Module discovery and import utilities
│   ├── geospatial.py     # Geospatial testing utilities
│   └── time_series.py    # Time series testing utilities
├── run_tests.py          # Test runner script
├── pytest.ini            # Pytest configuration
└── README.md             # This file
```

## Running Tests

You can run tests using the provided test runner script:

```bash
# Run all tests
./tests/run_tests.py

# Run only unit tests
./tests/run_tests.py --unit

# Run only integration tests
./tests/run_tests.py --integration

# Run only performance tests
./tests/run_tests.py --performance

# Run tests for specific modules
./tests/run_tests.py --modules space time data

# Run tests with specific keyword
./tests/run_tests.py --keyword geojson

# Run tests with specific marker
./tests/run_tests.py --marker geospatial

# Skip slow tests
./tests/run_tests.py --skip-slow

# Run tests in parallel
./tests/run_tests.py --jobs 4

# Generate HTML coverage report
./tests/run_tests.py --html-report
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run with coverage
pytest --cov=.
```

## Writing Tests

When writing new tests, follow these guidelines:

- Place unit tests in the `unit/` directory
- Place integration tests in the `integration/` directory
- Place system tests in the `system/` directory
- Place performance tests in the `performance/` directory
- Name test files with the prefix `test_`
- Name test functions with the prefix `test_`
- Use appropriate fixtures from `conftest.py`
- Write docstrings explaining what each test is verifying
- Use appropriate markers to categorize tests

## Test Markers

The following markers are available:

- `unit`: Unit tests that test a specific function or class
- `integration`: Integration tests that test interactions between components
- `system`: System tests that test the entire system
- `performance`: Performance tests that measure performance characteristics
- `geospatial`: Tests related to geospatial functionality
- `api`: Tests related to API functionality
- `slow`: Tests that take a long time to run
- `fast`: Tests that run quickly

Example:

```python
@pytest.mark.unit
@pytest.mark.geospatial
def test_create_point():
    # Test code here
    pass
```

## Test Utilities

The `utils/` directory contains utilities for testing:

- `__init__.py`: Module discovery and import utilities
- `geospatial.py`: Utilities for testing geospatial functionality
- `time_series.py`: Utilities for testing time series functionality

## Test Configuration

Test configuration is defined in `pytest.ini` and `conftest.py`. The `conftest.py` file defines fixtures that can be used across all tests.

## Test Coverage

The minimum test coverage threshold is 95% as specified in the `.cursorrules` file. You can check the current coverage by running:

```bash
./tests/run_tests.py --html-report
```

Then open `.test-results/coverage/index.html` in a browser.

## Continuous Integration

Tests are run automatically in the CI pipeline for every pull request and push to the main branch. The CI configuration is defined in the GitHub Actions workflows.

## Cross-Module Testing

The test infrastructure is designed to work across all GEO-INFER modules. The `integration/` directory contains tests that verify the interactions between different modules.

## Fixtures

Common fixtures are defined in `conftest.py` and are available to all tests. These include:

- Environment fixtures: `test_env`, `temp_dir`, etc.
- Configuration fixtures: `test_config_factory`, etc.
- Data fixtures: `test_geojson_point`, `test_geojson_feature`, `test_time_series_data`, etc.
- Validation fixtures: `assert_valid_geojson`, etc. 