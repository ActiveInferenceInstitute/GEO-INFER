"""Monitoring configuration module."""
import logging
import socket
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, Union

import prometheus_client as prom
from prometheus_client import Counter, Gauge, Histogram, REGISTRY
from prometheus_fastapi_instrumentator import Instrumentator

from .config import get_config

# Export REGISTRY as METRICS_REGISTRY for consistency
METRICS_REGISTRY = REGISTRY

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of HTTP errors",
    ["method", "endpoint", "error_type"]
)

CACHE_SIZE = Gauge(
    "cache_size_bytes",
    "Current size of the cache in bytes",
    ["cache_name"]
)

QUEUE_SIZE = Gauge(
    "queue_size",
    "Current number of items in the queue",
    ["queue_name"]
)

def reset_metrics() -> None:
    """Reset all metrics."""
    prom.REGISTRY._collector_to_names.clear()
    prom.REGISTRY._name_to_collector.clear()

def record_request(method: str, endpoint: str, status: int, duration: float) -> None:
    """Record a request metric.

    Args:
        method: HTTP method
        endpoint: Request endpoint
        status: HTTP status code
        duration: Request duration in seconds
    """
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

def record_error(method: str, endpoint: str, error_type: str) -> None:
    """Record an error metric.

    Args:
        method: HTTP method
        endpoint: Request endpoint
        error_type: Type of error
    """
    ERROR_COUNT.labels(method=method, endpoint=endpoint, error_type=error_type).inc()

def record_metric(
    name: str,
    value: float,
    metric_type: str = "counter",
    labels: Optional[Dict[str, str]] = None
) -> None:
    """Record a metric value.

    Args:
        name: Metric name
        value: Metric value
        metric_type: Type of metric (counter, gauge, histogram)
        labels: Optional metric labels
    """
    labels = labels or {}
    
    if metric_type == "counter":
        metric = Counter(name, f"Counter metric {name}", list(labels.keys()))
    elif metric_type == "gauge":
        metric = Gauge(name, f"Gauge metric {name}", list(labels.keys()))
    elif metric_type == "histogram":
        metric = Histogram(name, f"Histogram metric {name}", list(labels.keys()))
    else:
        raise ValueError(f"Invalid metric type: {metric_type}")
    
    metric.labels(**labels).inc(value)

def get_metric_value(
    name: str,
    labels: Optional[Dict[str, str]] = None
) -> float:
    """Get the value of a metric.

    Args:
        name: Metric name
        labels: Optional metric labels

    Returns:
        Metric value

    Raises:
        ValueError: If metric not found
    """
    labels = labels or {}
    
    for collector in METRICS_REGISTRY._collector_to_names:
        if collector._name == name:
            return collector.labels(**labels)._value.get()
    
    raise ValueError(f"Metric {name} not found")

def is_port_in_use(port: int) -> bool:
    """Check if a port is in use.
    
    Args:
        port: Port number
        
    Returns:
        bool: True if port is in use
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", port))
            return False
        except socket.error:
            return True

@contextmanager
def start_metrics_server(port: int = 9090) -> None:
    """Start metrics server.
    
    Args:
        port: Port to start server on
    """
    # Find available port if specified port is in use
    while is_port_in_use(port):
        port += 1
    
    try:
        prom.start_http_server(port, registry=METRICS_REGISTRY)
        yield
    finally:
        # Clean up
        pass

def instrument_app(app: Any) -> None:
    """Instrument a FastAPI application.

    Args:
        app: FastAPI application instance
    """
    instrumentator = Instrumentator(
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS"
    )
    
    instrumentator.instrument(app)
    app.instrumentator = instrumentator

def setup_monitoring(
    app: Optional[Any] = None,
    port: Optional[int] = None,
    metrics_path: str = "/metrics"
) -> None:
    """Set up monitoring.

    Args:
        app: Optional FastAPI application to instrument
        port: Optional port for metrics server
        metrics_path: Path for metrics endpoint
    """
    config = get_config()
    if not config.monitoring.enabled:
        return
    
    # Reset metrics
    reset_metrics()
    
    # Instrument app if provided
    if app:
        instrument_app(app)
    
    # Start metrics server if port specified
    if port:
        prom.start_http_server(port, registry=METRICS_REGISTRY)
    
    logging.info("Monitoring setup complete")

# Export functions and registry
__all__ = [
    "METRICS_REGISTRY",
    "reset_metrics",
    "record_request",
    "record_error",
    "record_metric",
    "get_metric_value",
    "is_port_in_use",
    "start_metrics_server",
    "instrument_app",
    "setup_monitoring"
] 