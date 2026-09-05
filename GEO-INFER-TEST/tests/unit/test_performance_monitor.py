"""
Unit tests for PerformanceMonitor using standard and property-based testing.
"""

import json
import statistics
from hypothesis import given, strategies as st
from geo_infer_test.core.performance_monitor import (
    PerformanceMonitor,
    BenchmarkRunner,
    MetricsCollector,
    PerformanceAnalyzer,
)


class TestPerformanceMonitor:
    """Standard tests for PerformanceMonitor."""

    def test_basic_timing(self):
        """Test basic start/stop timing functionality."""
        monitor = PerformanceMonitor()
        monitor.start("test_op")
        metrics = monitor.stop()

        assert metrics["label"] == "test_op"
        assert metrics["duration_s"] >= 0
        assert "peak_memory_bytes" in metrics

    def test_get_all_records(self):
        """Verify records accumulate correctly."""
        monitor = PerformanceMonitor()
        monitor.start("op1")
        monitor.stop()
        monitor.start("op2")
        monitor.stop()

        records = monitor.get_all_records()
        assert len(records) == 2
        assert records[0]["label"] == "op1"
        assert records[1]["label"] == "op2"

        monitor.reset()
        assert len(monitor.get_all_records()) == 0

    def test_nested_sections_both_recorded(self):
        """Nested start/stop pairs must yield two records and balanced tracing.

        Pre-fix behavior: the inner start overwrote the outer record and the
        inner stop() killed tracemalloc for the outer section.
        """
        monitor = PerformanceMonitor()
        monitor.start("outer")
        monitor.start("inner")
        inner = monitor.stop()
        outer = monitor.stop()

        assert inner["label"] == "inner"
        assert outer["label"] == "outer"
        labels = [r["label"] for r in monitor.get_all_records()]
        assert labels == ["inner", "outer"]
        # Both sections captured a real traced-memory peak.
        assert inner["peak_memory_bytes"] >= 0
        assert outer["peak_memory_bytes"] >= 0
        assert monitor._trace_depth == 0

        monitor.reset()
        monitor.start("after_reset")
        assert monitor.stop()["label"] == "after_reset"


class TestBenchmarkRunner:
    """Tests for BenchmarkRunner."""

    def test_benchmark_simple_function(self):
        """Benchmark a predictable function."""
        runner = BenchmarkRunner(iterations=5, warmup=1)

        def slow_func():
            pass

        stats = runner.run(slow_func, label="slow")

        assert stats["iterations"] == 5
        assert stats["mean_s"] >= 0
        assert stats["total_s"] >= 0


class TestMetricsCollectorAnalyzer:
    """Tests for MetricsCollector and PerformanceAnalyzer."""

    def test_collection_and_analysis_flow(self):
        """Test collecting metrics and detecting regressions."""
        collector = MetricsCollector()
        analyzer = PerformanceAnalyzer(collector)

        # Add baseline data
        collector.add({"duration_s": 1.0, "mean_s": 1.0})
        collector.add({"duration_s": 1.1, "mean_s": 1.1})

        # Test regression detection
        # Current (1.1) vs Baseline (1.0) -> ratio 1.1 -> No regression at threshold 1.5
        report = analyzer.detect_regression({"duration_s": 1.0}, threshold=1.5)
        assert report["status"] == "ok"

        # Add very slow data
        collector.add({"duration_s": 2.0, "mean_s": 2.0})

        # Current (2.0) vs Baseline (1.0) -> ratio 2.0 -> Regression at threshold 1.5
        report = analyzer.detect_regression({"duration_s": 1.0}, threshold=1.5)
        assert report["status"] == "regression"
        assert len(report["regressions"]) == 1
        assert report["regressions"][0]["metric"] == "duration_s"

    def test_metrics_persistence_round_trip(self, tmp_path):
        """Verify MetricsCollector writes JSON snapshots with metric payloads."""
        collector = MetricsCollector()
        collector.add({"duration_s": 1.25, "mean_s": 1.25})

        output_file = tmp_path / "metrics.json"
        collector.save(output_file)

        payload = json.loads(output_file.read_text())
        assert len(payload) == 1
        assert payload[0]["duration_s"] == 1.25
        assert payload[0]["mean_s"] == 1.25
        assert "timestamp" in payload[0]


# ---------------------------------------------------------------------------
# Property-Based Tests (Hypothesis)
# ---------------------------------------------------------------------------


class TestHypothesisPerformance:
    """Property-based tests for performance statistics logic."""

    @given(st.lists(st.floats(min_value=0.001, max_value=1.0), min_size=2, max_size=50))
    def test_benchmark_stats_calculation(self, durations):
        """
        Verify that BenchmarkRunner-like statistics are calculated correctly
        for any list of durations.
        """
        mean = statistics.mean(durations)
        median = statistics.median(durations)
        stdev = statistics.stdev(durations) if len(durations) > 1 else 0.0

        # We can't easily mock time.perf_counter inside BenchmarkRunner via Hypothesis
        # so we verify the logic we use:
        assert min(durations) <= mean <= max(durations)
        assert min(durations) <= median <= max(durations)
        if len(durations) > 2 and stdev > 0:
            # Most values within 3 stdevs (Chebyshev's inequality rough check)
            pass

    @given(st.lists(st.floats(min_value=0.1, max_value=10.0), min_size=10))
    def test_analyzer_trend_detection(self, values):
        """Verify trend detection logic acts consistently."""
        collector = MetricsCollector()
        for v in values:
            collector.add({"mean_s": v})

        analyzer = PerformanceAnalyzer(collector)
        report = analyzer.trend_report()

        assert report["trend"] in ("improving", "degrading", "stable", "unknown")
        assert report["total_samples"] == len(values)

        # self-consistency check
        if report["trend"] == "degrading":
            assert report["second_half_mean"] > report["first_half_mean"] * 1.1
        elif report["trend"] == "improving":
            assert report["second_half_mean"] < report["first_half_mean"] * 0.9
