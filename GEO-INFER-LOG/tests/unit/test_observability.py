"""Tests for the observability layer in geo_infer_log."""

from geo_infer_log import PerformanceMetrics


class TestPerformanceMetrics:
    """Test suite for PerformanceMetrics."""

    def test_get_all_metrics_returns_without_deadlock(self) -> None:
        """get_all_metrics must not re-acquire the non-reentrant lock."""
        metrics = PerformanceMetrics()
        metrics.record_duration("load_data", 1.5)
        metrics.increment_counter("requests", 2)
        metrics.set_gauge("queue_depth", 7.0)

        snapshot = metrics.get_all_metrics()

        assert snapshot["counters"] == {"requests": 2}
        assert snapshot["gauges"] == {"queue_depth": 7.0}
        stats = snapshot["performance_stats"]["load_data"]
        assert stats["count"] == 1
        assert stats["mean"] == 1.5

    def test_end_timer_records_full_operation_name(self) -> None:
        """Operations containing underscores keep their full name."""
        metrics = PerformanceMetrics()
        timer_id = metrics.start_timer("load_data")
        duration = metrics.end_timer(timer_id)

        assert duration > 0
        snapshot = metrics.get_all_metrics()
        # The operation must be keyed as "load_data", not truncated to "load".
        assert "load_data" in snapshot["performance_stats"]
        assert "load" not in snapshot["performance_stats"]

    def test_end_timer_unknown_id_returns_zero(self) -> None:
        """Ending a timer that was never started yields 0.0."""
        metrics = PerformanceMetrics()
        assert metrics.end_timer("missing_id") == 0.0

    def test_get_stats_matches_get_all_metrics(self) -> None:
        """get_stats and get_all_metrics agree on the same operation."""
        metrics = PerformanceMetrics()
        metrics.record_duration("route", 2.0)
        metrics.record_duration("route", 4.0)

        stats = metrics.get_stats("route")
        all_stats = metrics.get_all_metrics()["performance_stats"]["route"]

        assert stats == all_stats
        assert stats["count"] == 2
        assert stats["min"] == 2.0
        assert stats["max"] == 4.0
