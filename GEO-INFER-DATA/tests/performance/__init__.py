"""
Performance tests for GEO-INFER-DATA.

This module contains performance tests and benchmarks for all
GEO-INFER-DATA components including throughput, latency, and scalability tests.

Test Categories:
    benchmarks: Performance benchmarks for different operations
    scalability: Scalability tests with varying data sizes
    stress_tests: Stress tests under high load
    memory_tests: Memory usage and optimization tests

Examples:
    >>> # Run performance tests
    >>> python -m pytest tests/performance/ -v
    >>>
    >>> # Run specific benchmark
    >>> python -m pytest tests/performance/test_benchmarks.py::test_ingestion_throughput
"""

import pytest
import asyncio
from pathlib import Path

# Performance test configuration
pytest_plugins = ["pytest_asyncio", "pytest_benchmark"]

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'ingestion_throughput': 1000,  # records/second
    'storage_latency': 5.0,        # seconds
    'query_latency': 1.0,          # seconds
    'validation_latency': 10.0,    # seconds
    'memory_usage': 500,           # MB
}

# Test data sizes for scalability testing
DATA_SIZES = {
    'small': 1000,
    'medium': 10000,
    'large': 100000,
    'xlarge': 1000000
}
