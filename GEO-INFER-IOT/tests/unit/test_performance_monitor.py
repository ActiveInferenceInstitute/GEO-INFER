"""Regression tests for IoT performance monitoring summaries."""

from datetime import datetime

from geo_infer_iot.performance import PerformanceMetrics, PerformanceMonitor


def test_performance_summary_aggregates_metrics() -> None:
    monitor = PerformanceMonitor({"throughput_threshold": 0.0})
    monitor.metrics_history.extend(
        [
            PerformanceMetrics(timestamp=datetime.now(), cpu_percent=20.0),
            PerformanceMetrics(timestamp=datetime.now(), cpu_percent=40.0),
        ]
    )

    summary = monitor.get_performance_summary(minutes=5)

    assert summary["total_samples"] == 2
    assert summary["cpu_usage"]["mean"] == 30.0
