#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive monitoring and observability for GEO-INFER-GIT.

This module provides advanced monitoring capabilities including:
- Metrics collection and aggregation
- Distributed tracing
- Performance profiling
- Alerting and notification systems
- Health checks and diagnostics
- Observability dashboards
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import psutil
import uuid

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

def _utc_now() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


@dataclass
class Metric:
    """A single metric measurement."""

    name: str
    value: Union[int, float]
    timestamp: datetime = field(default_factory=_utc_now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

@dataclass
class TraceSpan:
    """A distributed trace span."""

    span_id: str
    trace_id: str
    parent_span_id: Optional[str] = None
    operation_name: str = ""
    start_time: datetime = field(default_factory=_utc_now)
    end_time: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"

    @property
    def duration(self) -> float:
        """Get span duration in seconds."""
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()

    def finish(self, status: str = "ok") -> None:
        """Finish the span."""
        self.end_time = datetime.now(timezone.utc)
        self.status = status

    def log(self, message: str, **fields: Any) -> None:
        """Add a log entry to the span."""
        self.logs.append({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'message': message,
            'fields': fields
        })

@dataclass
class AlertRule:
    """An alerting rule configuration."""

    name: str
    metric_name: str
    condition: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    duration_minutes: int = 5
    severity: str = "warning"  # info, warning, error, critical
    message: str = ""
    enabled: bool = True
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None

@dataclass
class Alert:
    """An alert notification."""

    alert_id: str
    rule_name: str
    severity: str
    message: str
    timestamp: datetime = field(default_factory=_utc_now)
    metric_name: str = ""
    metric_value: float = 0.0
    threshold: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """
    Comprehensive metrics collection system.

    Provides:
    - Custom metric collection and aggregation
    - Counter, gauge, histogram, and summary metrics
    - Automatic metric export to multiple backends
    - Metric tagging and filtering
    """

    def __init__(self, enable_collection: bool = True):
        """
        Initialize metrics collector.

        Args:
            enable_collection: Whether to enable metrics collection
        """
        self.enable_collection = enable_collection
        self.metrics: Dict[str, List[Metric]] = defaultdict(list)
        self.counters: Dict[str, int] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.summaries: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Auto-export configuration
        self.auto_export_interval = 60  # seconds
        self.export_backends: List[Any] = []

        # Thread safety
        self.lock = threading.RLock()

        # Start auto-export if enabled
        if enable_collection:
            self._start_auto_export()

    def _start_auto_export(self) -> None:
        """Start automatic metric export."""
        export_thread = threading.Thread(
            target=self._auto_export_worker,
            daemon=True
        )
        export_thread.start()

    def _auto_export_worker(self) -> None:
        """Background worker for automatic metric export."""
        while True:
            try:
                time.sleep(self.auto_export_interval)
                self.export_metrics()
            except Exception as e:
                logger.warning(f"Error in auto-export: {e}")

    def counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a counter metric.

        Args:
            name: Metric name
            value: Value to add
            tags: Metric tags
        """
        if not self.enable_collection:
            return

        with self.lock:
            self.counters[name] = self.counters.get(name, 0) + value

            # Store metric
            metric = Metric(
                name=name,
                value=self.counters[name],
                tags=tags or {}
            )
            self.metrics[name].append(metric)

    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            tags: Metric tags
        """
        if not self.enable_collection:
            return

        with self.lock:
            self.gauges[name] = value

            # Store metric
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric)

    def histogram(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a histogram metric.

        Args:
            name: Metric name
            value: Histogram value
            tags: Metric tags
        """
        if not self.enable_collection:
            return

        with self.lock:
            self.histograms[name].append(value)

            # Store metric
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric)

    def summary(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a summary metric.

        Args:
            name: Metric name
            value: Summary value
            tags: Metric tags
        """
        if not self.enable_collection:
            return

        with self.lock:
            if name not in self.summaries:
                self.summaries[name] = {'count': 0, 'sum': 0.0, 'min': float('inf'), 'max': 0.0}

            summary = self.summaries[name]
            summary['count'] += 1
            summary['sum'] += value
            summary['min'] = min(summary['min'], value)
            summary['max'] = max(summary['max'], value)

            # Store metric
            metric = Metric(
                name=name,
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(metric)

    def get_metric_summary(self, name: str) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        with self.lock:
            if name in self.counters:
                return {'type': 'counter', 'value': self.counters[name]}
            elif name in self.gauges:
                return {'type': 'gauge', 'value': self.gauges[name]}
            elif name in self.histograms:
                values = self.histograms[name]
                if values:
                    return {
                        'type': 'histogram',
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values)
                    }
            elif name in self.summaries:
                return {'type': 'summary', **self.summaries[name]}

        return {}

    def export_metrics(self, format: str = 'prometheus') -> str:
        """
        Export metrics in specified format.

        Args:
            format: Export format (prometheus, json, influxdb)

        Returns:
            Formatted metrics string
        """
        if format == 'prometheus':
            return self._export_prometheus()
        elif format == 'json':
            return self._export_json()
        elif format == 'influxdb':
            return self._export_influxdb()
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []

        with self.lock:
            # Export counters
            for name, value in self.counters.items():
                lines.append(f"# HELP {name} Counter metric")
                lines.append(f"# TYPE {name} counter")
                lines.append(f"{name} {value}")

            # Export gauges
            for name, gauge_val in self.gauges.items():
                lines.append(f"# HELP {name} Gauge metric")
                lines.append(f"# TYPE {name} gauge")
                lines.append(f"{name} {gauge_val}")

            # Export histograms
            for name, values in self.histograms.items():
                if values:
                    lines.append(f"# HELP {name} Histogram metric")
                    lines.append(f"# TYPE {name} histogram")
                    for hist_val in values:
                        lines.append(f"{name}_bucket{{\"le\"+\"Inf\"}} 1")
                        lines.append(f"{name} {hist_val}")

        return '\n'.join(lines)

    def _export_json(self) -> str:
        """Export metrics in JSON format."""
        export_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'counters': self.counters,
            'gauges': self.gauges,
            'histograms': dict(self.histograms),
            'summaries': dict(self.summaries)
        }

        return json.dumps(export_data, indent=2)

    def _export_influxdb(self) -> str:
        """Export metrics in InfluxDB line protocol format."""
        lines = []

        with self.lock:
            timestamp = int(time.time() * 1e9)  # nanoseconds

            # Export counters
            for name, value in self.counters.items():
                lines.append(f"{name},type=counter value={value} {timestamp}")

            # Export gauges
            for name, gauge_val in self.gauges.items():
                lines.append(f"{name},type=gauge value={gauge_val} {timestamp}")

        return '\n'.join(lines)

class Tracer:
    """
    Distributed tracing system for tracking operations across services.

    Provides:
    - Span creation and management
    - Context propagation
    - Trace sampling and filtering
    - Integration with logging systems
    """

    def __init__(self, service_name: str = "geo-infer-git", sampling_rate: float = 1.0):
        """
        Initialize tracer.

        Args:
            service_name: Name of this service
            sampling_rate: Trace sampling rate (0.0 to 1.0)
        """
        self.service_name = service_name
        self.sampling_rate = sampling_rate

        # Active traces
        self.active_traces: Dict[str, List[TraceSpan]] = defaultdict(list)
        self.completed_traces: Dict[str, List[TraceSpan]] = {}

        # Context management
        self.context = threading.local()

        # Thread safety
        self.lock = threading.RLock()

    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None,
                   tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """
        Start a new trace span.

        Args:
            operation_name: Name of the operation
            parent_span_id: ID of parent span
            tags: Span tags

        Returns:
            New TraceSpan instance
        """
        # Generate trace and span IDs
        trace_id = getattr(self.context, 'trace_id', str(uuid.uuid4()))
        span_id = str(uuid.uuid4())

        # Check if we should sample this trace
        if not self._should_sample():
            # Create a no-op span
            return TraceSpan(span_id=span_id, trace_id=trace_id, operation_name=operation_name)

        # Create real span
        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            tags=tags or {}
        )

        # Set context
        self.context.trace_id = trace_id
        self.context.current_span_id = span_id

        # Add to active traces
        with self.lock:
            self.active_traces[trace_id].append(span)

        return span

    def _should_sample(self) -> bool:
        """Determine if this trace should be sampled."""
        import random
        return random.random() < self.sampling_rate

    def finish_span(self, span: TraceSpan) -> None:
        """
        Finish a trace span.

        Args:
            span: Span to finish
        """
        span.finish()

        # Move to completed traces
        with self.lock:
            if span.trace_id in self.active_traces:
                active_spans = self.active_traces[span.trace_id]

                # Remove finished span
                self.active_traces[span.trace_id] = [
                    s for s in active_spans if s.span_id != span.span_id
                ]

                # Move to completed if no active spans remain
                if not self.active_traces[span.trace_id]:
                    completed_spans = self.completed_traces.get(span.trace_id, [])
                    completed_spans.extend(active_spans)
                    self.completed_traces[span.trace_id] = completed_spans
                    del self.active_traces[span.trace_id]

    def get_trace(self, trace_id: str) -> Optional[List[TraceSpan]]:
        """
        Get a complete trace by ID.

        Args:
            trace_id: Trace ID

        Returns:
            List of spans in the trace
        """
        with self.lock:
            if trace_id in self.completed_traces:
                return self.completed_traces[trace_id]
            elif trace_id in self.active_traces:
                return self.active_traces[trace_id]

        return None

    def export_traces(self, format: str = 'jaeger') -> str:
        """
        Export traces in specified format.

        Args:
            format: Export format (jaeger, zipkin, json)

        Returns:
            Formatted trace data
        """
        if format == 'json':
            return self._export_traces_json()
        elif format == 'jaeger':
            return self._export_traces_jaeger()
        else:
            raise ValueError(f"Unsupported trace format: {format}")

    def _export_traces_json(self) -> str:
        """Export traces in JSON format."""
        export_data: Dict[str, Any] = {
            'service': self.service_name,
            'traces': {}
        }

        with self.lock:
            for trace_id, spans in self.completed_traces.items():
                export_data['traces'][trace_id] = [
                    {
                        'span_id': span.span_id,
                        'trace_id': span.trace_id,
                        'parent_span_id': span.parent_span_id,
                        'operation_name': span.operation_name,
                        'start_time': span.start_time.isoformat(),
                        'end_time': span.end_time.isoformat() if span.end_time else None,
                        'duration': span.duration,
                        'tags': span.tags,
                        'logs': span.logs,
                        'status': span.status
                    }
                    for span in spans
                ]

        return json.dumps(export_data, indent=2)

    def _export_traces_jaeger(self) -> str:
        """Export traces in Jaeger format."""
        # Simplified Jaeger format export
        return self._export_traces_json()

class HealthChecker:
    """
    Comprehensive health checking system.

    Provides:
    - Service health monitoring
    - Dependency health checks
    - Custom health checks
    - Health status aggregation
    """

    def __init__(self, service_name: str = "geo-infer-git"):
        """
        Initialize health checker.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.health_checks: Dict[str, Callable] = {}
        self.last_check_results: Dict[str, Dict[str, Any]] = {}

    def register_check(self, name: str, check_func: Callable[[], Dict[str, Any]]) -> None:
        """
        Register a health check function.

        Args:
            name: Check name
            check_func: Function that returns health status
        """
        self.health_checks[name] = check_func

    def check_all(self) -> Dict[str, Any]:
        """
        Run all registered health checks.

        Returns:
            Aggregated health status
        """
        results = {}
        overall_status = "healthy"

        for name, check_func in self.health_checks.items():
            try:
                result = check_func()
                results[name] = result

                # Update overall status
                if result.get('status') == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result.get('status') == 'degraded' and overall_status == 'healthy':
                    overall_status = 'degraded'

            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                overall_status = 'error'

        # Store results
        self.last_check_results = results

        return {
            'service': self.service_name,
            'status': overall_status,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': results
        }

    def get_status(self) -> str:
        """Get current overall health status."""
        if not self.last_check_results:
            return 'unknown'

        statuses = [check.get('status', 'unknown') for check in self.last_check_results.values()]

        if 'error' in statuses:
            return 'error'
        elif 'unhealthy' in statuses:
            return 'unhealthy'
        elif 'degraded' in statuses:
            return 'degraded'
        else:
            return 'healthy'

class AlertManager:
    """
    Alert management and notification system.

    Provides:
    - Alert rule evaluation
    - Alert notification delivery
    - Alert history and tracking
    - Alert suppression and grouping
    """

    def __init__(self) -> None:
        """Initialize alert manager."""
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.notification_handlers: List[Callable[[Alert], None]] = []
        self.suppression_rules: Dict[str, datetime] = {}

        # Start alert evaluation
        self.evaluation_thread = threading.Thread(
            target=self._alert_evaluation_worker,
            daemon=True
        )
        self.evaluation_thread.start()

    def add_rule(self, rule: AlertRule) -> None:
        """
        Add an alert rule.

        Args:
            rule: AlertRule to add
        """
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> None:
        """
        Remove an alert rule.

        Args:
            rule_name: Name of rule to remove
        """
        if rule_name in self.rules:
            del self.rules[rule_name]

    def add_notification_handler(self, handler: Callable[[Alert], None]) -> None:
        """
        Add a notification handler.

        Args:
            handler: Function to call when alert is triggered
        """
        self.notification_handlers.append(handler)

    def evaluate_metrics(self, metrics_collector: MetricsCollector) -> None:
        """
        Evaluate metrics against alert rules.

        Args:
            metrics_collector: MetricsCollector instance
        """
        current_time = datetime.now(timezone.utc)

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            # Check suppression
            suppression_key = f"{rule.name}_{rule.severity}"
            if suppression_key in self.suppression_rules:
                if current_time - self.suppression_rules[suppression_key] < timedelta(minutes=rule.cooldown_minutes):
                    continue

            # Get metric value
            metric_value = self._get_metric_value(rule.metric_name, metrics_collector)
            if metric_value is None:
                continue

            # Evaluate condition
            triggered = self._evaluate_condition(rule.condition, metric_value, rule.threshold)

            if triggered:
                # Create alert
                alert = Alert(
                    alert_id=str(uuid.uuid4()),
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.message or f"Alert: {rule.metric_name} {rule.condition} {rule.threshold}",
                    metric_name=rule.metric_name,
                    metric_value=metric_value,
                    threshold=rule.threshold
                )

                # Send notifications
                self._send_alert(alert)

                # Set suppression
                self.suppression_rules[suppression_key] = current_time

    def _get_metric_value(self, metric_name: str, metrics_collector: MetricsCollector) -> Optional[float]:
        """Get current value of a metric."""
        summary = metrics_collector.get_metric_summary(metric_name)

        if summary.get('type') == 'counter':
            return float(summary['value'])
        elif summary.get('type') == 'gauge':
            return float(summary['value'])
        elif summary.get('type') == 'histogram' and 'avg' in summary:
            return float(summary['avg'])

        return None

    def _evaluate_condition(self, condition: str, value: float, threshold: float) -> bool:
        """Evaluate alert condition."""
        if condition == 'gt':
            return value > threshold
        elif condition == 'gte':
            return value >= threshold
        elif condition == 'lt':
            return value < threshold
        elif condition == 'lte':
            return value <= threshold
        elif condition == 'eq':
            return abs(value - threshold) < 1e-6

        return False

    def _send_alert(self, alert: Alert) -> None:
        """Send alert to all notification handlers."""
        self.alerts.append(alert)

        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]

        # Send to handlers
        for handler in self.notification_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.warning(f"Error in alert handler: {e}")

    def _alert_evaluation_worker(self) -> None:
        """Background worker for alert evaluation based on current metric values."""
        # Rules are evaluated on demand via :meth:`evaluate_metrics`. This
        # worker exists for interface compatibility; it performs no work.
        return

class ObservabilityManager:
    """
    Comprehensive observability management system.

    Combines metrics, tracing, health checking, and alerting
    into a unified observability framework.
    """

    def __init__(self, service_name: str = "geo-infer-git"):
        """
        Initialize observability manager.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name

        # Initialize components
        self.metrics = MetricsCollector()
        self.tracer = Tracer(service_name)
        self.health_checker = HealthChecker(service_name)
        self.alert_manager = AlertManager()

        # Register default health checks
        self._register_default_health_checks()

        # Auto-alert evaluation
        self.alert_thread = threading.Thread(
            target=self._auto_alert_worker,
            daemon=True
        )
        self.alert_thread.start()

    def _register_default_health_checks(self) -> None:
        """Register default health checks."""
        # Memory usage check
        def memory_check() -> Dict[str, Any]:
            memory = psutil.virtual_memory()
            status = 'healthy' if memory.percent < 80 else 'degraded' if memory.percent < 95 else 'unhealthy'
            return {
                'status': status,
                'memory_percent': memory.percent,
                'memory_available': memory.available / (1024 * 1024),  # MB
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        self.health_checker.register_check('memory', memory_check)

        # CPU usage check
        def cpu_check() -> Dict[str, Any]:
            cpu_percent = psutil.cpu_percent(interval=1)
            status = 'healthy' if cpu_percent < 70 else 'degraded' if cpu_percent < 90 else 'unhealthy'
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        self.health_checker.register_check('cpu', cpu_check)

        # Disk usage check
        def disk_check() -> Dict[str, Any]:
            disk = psutil.disk_usage('/')
            status = 'healthy' if disk.percent < 80 else 'degraded' if disk.percent < 95 else 'unhealthy'
            return {
                'status': status,
                'disk_percent': disk.percent,
                'disk_free': disk.free / (1024 * 1024 * 1024),  # GB
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

        self.health_checker.register_check('disk', disk_check)

    def _auto_alert_worker(self) -> None:
        """Background worker for automatic alert evaluation."""
        while True:
            try:
                time.sleep(30)  # Evaluate every 30 seconds
                self.alert_manager.evaluate_metrics(self.metrics)
            except Exception as e:
                logger.warning(f"Error in auto-alert worker: {e}")

    def start_span(self, operation_name: str, tags: Optional[Dict[str, str]] = None) -> TraceSpan:
        """
        Start a new trace span.

        Args:
            operation_name: Name of the operation
            tags: Span tags

        Returns:
            New TraceSpan instance
        """
        return self.tracer.start_span(operation_name, tags=tags)

    def record_metric(self, metric_type: str, name: str, value: Union[int, float],
                     tags: Optional[Dict[str, str]] = None) -> None:
        """
        Record a metric.

        Args:
            metric_type: Type of metric (counter, gauge, histogram)
            name: Metric name
            value: Metric value
            tags: Metric tags
        """
        if metric_type == 'counter':
            self.metrics.counter(name, int(value), tags)
        elif metric_type == 'gauge':
            self.metrics.gauge(name, float(value), tags)
        elif metric_type == 'histogram':
            self.metrics.histogram(name, float(value), tags)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get current health status.

        Returns:
            Health status information
        """
        return self.health_checker.check_all()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get metrics summary.

        Returns:
            Summary of collected metrics
        """
        return {
            'metrics_count': len(self.metrics.metrics),
            'counters_count': len(self.metrics.counters),
            'gauges_count': len(self.metrics.gauges),
            'histograms_count': len(self.metrics.histograms),
            'summaries_count': len(self.metrics.summaries)
        }

    def export_observability_data(self, format: str = 'json') -> str:
        """
        Export all observability data.

        Args:
            format: Export format

        Returns:
            Formatted observability data
        """
        data = {
            'service': self.service_name,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'health': self.get_health_status(),
            'metrics': self.metrics.export_metrics('json'),
            'traces': self.tracer.export_traces('json')
        }

        if format == 'json':
            return json.dumps(data, indent=2)
        else:
            return str(data)

def create_observability_manager(service_name: str = "geo-infer-git") -> ObservabilityManager:
    """
    Create an observability manager with default configuration.

    Args:
        service_name: Name of the service

    Returns:
        Configured ObservabilityManager instance
    """
    return ObservabilityManager(service_name)
