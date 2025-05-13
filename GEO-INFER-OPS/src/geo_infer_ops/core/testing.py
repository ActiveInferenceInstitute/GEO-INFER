"""Testing configuration module."""
import contextlib
import logging
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Generator, Union, List

import pytest
from fastapi.testclient import TestClient
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

from .config import Config, update_config, get_config
from .logging import setup_logging, get_logger
from .monitoring import reset_metrics, METRICS_REGISTRY

logger = get_logger(__name__)

@contextlib.contextmanager
def mock_config(config_dict: Dict[str, Any]) -> Generator[Config, None, None]:
    """Mock configuration for testing.
    
    Args:
        config_dict: Configuration dictionary
        
    Yields:
        Config: Mocked configuration
    """
    # Store original config
    original_config = get_config()
    original_dict = original_config.model_dump()
    
    try:
        # Update config
        config = update_config(config_dict)
        yield config
    finally:
        # Restore original config
        update_config(original_dict)

def create_test_data_dir(prefix: str = "geo_infer_test_") -> str:
    """Create a temporary directory for test data.
    
    Args:
        prefix: Directory name prefix
        
    Returns:
        str: Path to created directory
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    return temp_dir

def create_test_client(app: Any) -> TestClient:
    """Create a test client for a FastAPI application.
    
    Args:
        app: FastAPI application
        
    Returns:
        TestClient: Test client
    """
    return TestClient(app)

def setup_testing(
    test_dir: str = "tests",
    coverage_report: bool = True,
    parallel: bool = False,
    timeout: Optional[int] = None,
    log_level: str = "INFO",
    json_format: bool = True
) -> int:
    """Set up and run tests.

    Args:
        test_dir: Directory containing tests
        coverage_report: Whether to generate coverage report
        parallel: Whether to run tests in parallel
        timeout: Test timeout in seconds
        log_level: Logging level
        json_format: Whether to use JSON log format

    Returns:
        Exit code from pytest
    """
    config = get_config()
    
    # Build pytest arguments
    args = [test_dir, "-v"]
    
    if parallel:
        args.extend(["-n", "auto"])
    
    if timeout:
        args.extend(["--timeout", str(timeout)])
    
    if coverage_report:
        args.extend([
            "--cov=geo_infer_ops",
            "--cov-report=term-missing",
            f"--cov-fail-under={config.testing.coverage_threshold}"
        ])
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    env["LOG_LEVEL"] = log_level
    env["LOG_FORMAT"] = "json" if json_format else "console"
    
    try:
        return subprocess.run(
            ["pytest"] + args,
            env=env,
            check=True
        ).returncode
    except subprocess.CalledProcessError as e:
        logger.error("test_execution_failed", error=str(e))
        return e.returncode

def assert_response_status(response: Any, expected_status: int) -> None:
    """Assert response status code.
    
    Args:
        response: FastAPI response
        expected_status: Expected status code
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"

def assert_response_json(response: Any, expected_json: Dict[str, Any]) -> None:
    """Assert response JSON content.
    
    Args:
        response: FastAPI response
        expected_json: Expected JSON content
    """
    assert response.json() == expected_json, \
        f"Expected JSON {expected_json}, got {response.json()}"

def assert_metric_value(
    metric_name: str,
    expected_value: Union[int, float],
    labels: Optional[Dict[str, str]] = None
) -> None:
    """Assert Prometheus metric value.

    Args:
        metric_name: Name of the metric
        expected_value: Expected metric value
        labels: Optional metric labels
    """
    labels = labels or {}
    
    # Find metric in registry
    for collector in pytest.REGISTRY._collector_to_names:
        if hasattr(collector, "_name") and collector._name == metric_name:
            actual_value = collector.labels(**labels)._value.get()
            assert actual_value == expected_value, \
                f"Metric {metric_name} value mismatch: expected {expected_value}, got {actual_value}"
            return
    
    raise ValueError(f"Metric {metric_name} not found")

def create_test_app() -> Any:
    """Create a test FastAPI application.
    
    Returns:
        Any: FastAPI application
    """
    from fastapi import FastAPI
    return FastAPI()

def create_test_request() -> Dict[str, Any]:
    """Create a test request.
    
    Returns:
        Dict[str, Any]: Test request
    """
    return {
        "method": "GET",
        "url": "http://test.example.com/test",
        "headers": {"Content-Type": "application/json"},
        "body": b"{}"
    }

def create_test_response() -> Dict[str, Any]:
    """Create a test response.
    
    Returns:
        Dict[str, Any]: Test response
    """
    return {
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": b"{}"
    }

def create_test_metric(
    name: str,
    metric_type: str = "counter",
    labels: Optional[List[str]] = None
) -> Union[Counter, Gauge, Histogram]:
    """Create a test metric.

    Args:
        name: Metric name
        metric_type: Type of metric (counter, gauge, histogram)
        labels: Optional metric labels

    Returns:
        Prometheus metric instance
    """
    labels = labels or []
    
    if metric_type == "counter":
        return Counter(name, f"Test counter {name}", labels)
    elif metric_type == "gauge":
        return Gauge(name, f"Test gauge {name}", labels)
    elif metric_type == "histogram":
        return Histogram(name, f"Test histogram {name}", labels)
    else:
        raise ValueError(f"Invalid metric type: {metric_type}")

# Export functions
__all__ = [
    "mock_config", "create_test_data_dir", "create_test_client",
    "setup_testing", "assert_response_status", "assert_response_json",
    "assert_metric_value", "create_test_app", "create_test_request",
    "create_test_response", "create_test_metric"
]