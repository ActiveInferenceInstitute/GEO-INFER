"""
Integration tests for GEO-INFER-DATA.

This module contains integration tests that verify how different components
of the GEO-INFER-DATA module work together in realistic scenarios.

Test Categories:
    end_to_end: Complete workflows from data ingestion to storage
    cross_component: Tests of component interactions
    data_flow: Tests of data flow between components
    performance_integration: Performance tests across components

Examples:
    >>> # Run integration tests
    >>> python -m pytest tests/integration/ -v
    >>>
    >>> # Run specific integration test
    >>> python -m pytest tests/integration/test_end_to_end.py::test_complete_workflow
"""

import pytest
import asyncio
from pathlib import Path

# Integration test configuration
pytest_plugins = ["pytest_asyncio"]

# Test data paths
INTEGRATION_TEST_DATA = Path(__file__).parent.parent / "fixtures" / "integration_data"
MOCK_API_RESPONSES = INTEGRATION_TEST_DATA / "mock_responses"

# Ensure test directories exist
INTEGRATION_TEST_DATA.mkdir(exist_ok=True)
MOCK_API_RESPONSES.mkdir(exist_ok=True)
