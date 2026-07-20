"""
Tests for PerformanceMonitor, OperationTracker, and DataProcessingProfiler
in geo_infer_data.utils.performance.
"""

from geo_infer_data.utils.performance import (
    DataProcessingProfiler,
    PerformanceMonitor,
)


# ---------------------------------------------------------------------------
# PerformanceMonitor
# ---------------------------------------------------------------------------


class TestPerformanceMonitor:
    def test_init_defaults(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        assert monitor.metrics["operations"] == {}
        assert monitor.active_operations == {}

    def test_record_metric(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        monitor.record_metric("ingest", "execution_time", 1.5)
        monitor.record_metric("ingest", "execution_time", 2.0)
        assert len(monitor.metrics["operations"]["ingest"]["execution_time"]) == 2

    def test_get_metrics_summary(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        monitor.record_metric("load", "execution_time", 3.0)
        monitor.record_metric("load", "execution_time", 5.0)
        summary = monitor.get_metrics()
        op = summary["operations"]["load"]["execution_time"]
        assert op["count"] == 2
        assert op["average"] == 4.0
        assert op["min"] == 3.0
        assert op["max"] == 5.0

    def test_track_operation_context_manager(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        with monitor.track_operation("test_op"):
            pass

        summary = monitor.get_metrics()
        assert "test_op" in summary["operations"]
        exec_times = summary["operations"]["test_op"]["execution_time"]
        assert exec_times["count"] == 1
        assert exec_times["total"] >= 0

    def test_identify_bottlenecks_none(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        monitor.record_metric("fast_op", "execution_time", 0.5)
        bottlenecks = monitor.identify_bottlenecks()
        slow = [b for b in bottlenecks if b["type"] == "slow_operation"]
        assert len(slow) == 0

    def test_identify_bottlenecks_slow(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        monitor.record_metric("slow_op", "execution_time", 120.0)
        bottlenecks = monitor.identify_bottlenecks()
        slow = [b for b in bottlenecks if b["type"] == "slow_operation"]
        assert len(slow) >= 1
        assert slow[0]["severity"] == "high"

    def test_reset_metrics(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        monitor.record_metric("op", "time", 1.0)
        assert len(monitor.metrics["operations"]) > 0
        monitor.reset_metrics()
        assert monitor.metrics["operations"] == {}

    def test_multiple_operations_tracked(self):
        monitor = PerformanceMonitor(
            enable_memory_monitoring=False, enable_cpu_monitoring=False
        )
        with monitor.track_operation("op_a"):
            pass
        with monitor.track_operation("op_b"):
            pass
        summary = monitor.get_metrics()
        assert "op_a" in summary["operations"]
        assert "op_b" in summary["operations"]
        assert summary["total_operations"] == 2


# ---------------------------------------------------------------------------
# DataProcessingProfiler
# ---------------------------------------------------------------------------


class TestDataProcessingProfiler:
    def test_profile_step(self):
        profiler = DataProcessingProfiler()
        profiler.start_profiling()

        with profiler.profile_step("load"):
            pass

        with profiler.profile_step("transform"):
            pass

        profile = profiler.get_profile()
        assert "load" in profile["steps"]
        assert "transform" in profile["steps"]
        assert profile["steps"]["load"]["calls"] == 1
        assert profile["steps"]["transform"]["calls"] == 1

    def test_get_profile_without_start(self):
        profiler = DataProcessingProfiler()
        result = profiler.get_profile()
        assert "error" in result

    def test_step_percentages(self):
        profiler = DataProcessingProfiler()
        profiler.start_profiling()
        with profiler.profile_step("step_a"):
            pass
        profiler.end_profiling()

        profile = profiler.get_profile()
        assert profile["steps"]["step_a"]["percentage"] >= 0

    def test_repeated_step_accumulates(self):
        profiler = DataProcessingProfiler()
        profiler.start_profiling()
        for _ in range(3):
            with profiler.profile_step("repeated"):
                pass
        profiler.end_profiling()

        profile = profiler.get_profile()
        assert profile["steps"]["repeated"]["calls"] == 3
        assert profile["steps"]["repeated"]["duration"] >= 0
