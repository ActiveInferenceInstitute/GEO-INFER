#!/bin/bash
# Run tests for GEO-INFER-AG module

# Set up environment
echo "Setting up test environment..."
pip install -r requirements-test.txt

# Run unit tests by default
if [ "$1" == "all" ]; then
    # Run all tests including integration and performance tests
    echo "Running all tests (unit, integration, performance)..."
    python -m pytest tests -m "unit or integration or performance" $2
elif [ "$1" == "integration" ]; then
    # Run unit and integration tests
    echo "Running unit and integration tests..."
    python -m pytest tests -m "unit or integration" $2
elif [ "$1" == "performance" ]; then
    # Run only performance tests
    echo "Running performance tests..."
    python -m pytest tests -m "performance" $2
else
    # Run only unit tests (default)
    echo "Running unit tests only..."
    echo "Use './run_tests.sh integration' to run integration tests as well"
    echo "Use './run_tests.sh all' to run all tests including performance tests"
    python -m pytest tests/unit $2
fi

# Report coverage
echo "Test coverage report:"
python -m pytest --cov-report term-missing --cov=geo_infer_ag tests/unit 