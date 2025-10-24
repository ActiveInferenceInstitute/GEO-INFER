"""
Test suite for GEO-INFER-DATA.

This module contains comprehensive tests for all GEO-INFER-DATA functionality
including unit tests, integration tests, and performance tests.

Test Structure:
    unit/ - Unit tests for individual components
    integration/ - Integration tests for component interactions
    performance/ - Performance tests and benchmarks
    fixtures/ - Test data and fixtures

Examples:
    >>> # Run all tests
    >>> python -m pytest tests/
    >>>
    >>> # Run unit tests only
    >>> python -m pytest tests/unit/
    >>>
    >>> # Run with coverage
    >>> python -m pytest tests/ --cov=src/geo_infer_data
"""

import pytest
from pathlib import Path

# Test configuration
pytest_plugins = ["pytest_asyncio"]

# Test data paths
TEST_DATA_PATH = Path(__file__).parent / "fixtures"
MOCK_DATA_PATH = TEST_DATA_PATH / "mock_data"

# Ensure test directories exist
TEST_DATA_PATH.mkdir(exist_ok=True)
MOCK_DATA_PATH.mkdir(exist_ok=True)
