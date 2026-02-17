"""
Unit and property-based tests for the GeoInferTestRunner and helpers.
"""

import pytest
from hypothesis import given, settings, strategies as st
from unittest.mock import patch

# Alias imports to prevent pytest collection warnings
from geo_infer_test.core.test_runner import (
    TestConfiguration as _TestConfiguration,
    TestResult as _TestResult,
    GeoInferTestRunner as _GeoInferTestRunner,
)


# ============================================================================
# TestConfiguration dataclass tests
# ============================================================================

class TestTestConfiguration:
    """Tests for the TestConfiguration dataclass."""

    def test_defaults(self):
        cfg = _TestConfiguration(modules_to_test=["A"], test_types=["unit"])
        assert cfg.parallel_execution is True
        assert cfg.max_workers == 4
        assert cfg.timeout_seconds == 300
        assert cfg.fail_fast is False
        assert cfg.coverage_enabled is True

    @pytest.mark.parametrize("modules", [
        ["A"], ["A", "B"], ["A", "B", "C", "D", "E"],
        [f"MOD_{i}" for i in range(20)],
    ])
    def test_modules_list(self, modules):
        cfg = _TestConfiguration(modules_to_test=modules, test_types=["unit"])
        assert cfg.modules_to_test == modules

    @pytest.mark.parametrize("types", [
        ["unit"], ["integration"], ["unit", "integration"],
        ["unit", "integration", "performance"],
    ])
    def test_test_types(self, types):
        cfg = _TestConfiguration(modules_to_test=["A"], test_types=types)
        assert cfg.test_types == types

    @pytest.mark.parametrize("workers", [1, 2, 4, 8, 16])
    def test_max_workers(self, workers):
        cfg = _TestConfiguration(
            modules_to_test=["A"], test_types=["unit"], max_workers=workers
        )
        assert cfg.max_workers == workers

    @pytest.mark.parametrize("timeout", [10, 60, 300, 600, 3600])
    def test_timeout(self, timeout):
        cfg = _TestConfiguration(
            modules_to_test=["A"], test_types=["unit"], timeout_seconds=timeout
        )
        assert cfg.timeout_seconds == timeout

    @pytest.mark.parametrize("parallel, fail_fast, coverage, perf", [
        (True, False, True, True),
        (False, True, False, False),
        (True, True, True, False),
        (False, False, False, True),
    ])
    def test_boolean_flags(self, parallel, fail_fast, coverage, perf):
        cfg = _TestConfiguration(
            modules_to_test=["A"],
            test_types=["unit"],
            parallel_execution=parallel,
            fail_fast=fail_fast,
            coverage_enabled=coverage,
            performance_benchmarks=perf,
        )
        assert cfg.parallel_execution == parallel
        assert cfg.fail_fast == fail_fast
        assert cfg.coverage_enabled == coverage
        assert cfg.performance_benchmarks == perf


# ============================================================================
# TestResult dataclass tests
# ============================================================================

class TestTestResultDataclass:
    """Tests for the TestResult dataclass."""

    def test_basic_creation(self):
        r = _TestResult(
            test_id="t1", module="mod", test_name="test_foo",
            status="passed", duration=0.5, message="ok", details={}
        )
        assert r.test_id == "t1"
        assert r.status == "passed"
        assert r.performance_metrics is None

    @pytest.mark.parametrize("status", ["passed", "failed", "error", "skipped"])
    def test_status_values(self, status):
        r = _TestResult(
            test_id="t1", module="mod", test_name="test_x",
            status=status, duration=1.0, message="", details={}
        )
        assert r.status == status

    @pytest.mark.parametrize("duration", [0.0, 0.001, 1.0, 10.0, 100.0, 300.0])
    def test_duration_values(self, duration):
        r = _TestResult(
            test_id="t1", module="mod", test_name="test_x",
            status="passed", duration=duration, message="", details={}
        )
        assert r.duration == duration

    def test_with_performance_metrics(self):
        r = _TestResult(
            test_id="t1", module="mod", test_name="test_x",
            status="passed", duration=1.0, message="",
            details={}, performance_metrics={"memory": 1024, "cpu": 0.5}
        )
        assert r.performance_metrics["memory"] == 1024


# ============================================================================
# GeoInferTestRunner tests
# ============================================================================

class TestGeoInferTestRunner:
    """Tests for GeoInferTestRunner core logic."""

    def test_runner_initialization(self):
        cfg = _TestConfiguration(modules_to_test=["SPACE"], test_types=["unit"])
        runner = _GeoInferTestRunner(cfg)
        assert runner.config == cfg

    def test_runner_setup_environment(self):
        cfg = _TestConfiguration(modules_to_test=["SPACE"], test_types=["unit"])
        runner = _GeoInferTestRunner(cfg)
        # Should not raise
        runner._setup_test_environment()

    @pytest.mark.parametrize("module", [
        "SPACE", "TIME", "AI", "BAYES", "ACT", "AGENT", "SEC",
        "APP", "API", "LOG", "DATA", "OPS", "RISK",
    ])
    def test_runner_discover_module(self, module):
        cfg = _TestConfiguration(modules_to_test=[module], test_types=["unit"])
        runner = _GeoInferTestRunner(cfg)
        # Discovery should return a structure even for non-existent modules
        tests = runner._discover_module_tests(module)
        assert isinstance(tests, (list, dict, type(None)))

    def test_runner_discover_tests_structure(self):
        cfg = _TestConfiguration(
            modules_to_test=["SPACE", "TIME"], test_types=["unit"]
        )
        runner = _GeoInferTestRunner(cfg)
        discovered = runner.discover_tests()
        assert isinstance(discovered, dict)

    def test_report_generation(self):
        cfg = _TestConfiguration(
            modules_to_test=["SPACE"], test_types=["unit"]
        )
        runner = _GeoInferTestRunner(cfg)
        # Add test results using the actual attribute name and status values
        runner.test_results = [
            _TestResult(
                test_id=f"t{i}", module="SPACE", test_name=f"test_{i}",
                status="PASS" if i % 2 == 0 else "FAIL",
                duration=float(i) * 0.1, message="", details={}
            )
            for i in range(10)
        ]
        report = runner._generate_execution_report(1.5)
        summary = report["execution_summary"]
        assert summary["total_tests"] == 10
        assert summary["passed"] == 5
        assert summary["failed"] == 5


# ============================================================================
# Property-Based Tests (Hypothesis)
# ============================================================================

class TestHypothesisTestRunner:
    """Property-based tests for test runner components."""

    @settings(max_examples=200)
    @given(st.lists(
        st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=('Lu',))),
        min_size=1, max_size=15, unique=True
    ))
    def test_config_modules_preserved(self, modules):
        """All module names should survive config round-trip."""
        cfg = _TestConfiguration(modules_to_test=modules, test_types=["unit"])
        assert cfg.modules_to_test == modules

    @settings(max_examples=200)
    @given(
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=20),
        st.text(min_size=1, max_size=30),
        st.sampled_from(["passed", "failed", "error", "skipped"]),
        st.floats(min_value=0.0, max_value=300.0),
    )
    def test_result_creation_never_crashes(self, test_id, module, name, status, duration):
        """TestResult should handle any valid inputs."""
        r = _TestResult(
            test_id=test_id, module=module, test_name=name,
            status=status, duration=duration, message="", details={}
        )
        assert r.test_id == test_id
        assert r.status == status

    @settings(max_examples=200)
    @given(st.integers(min_value=1, max_value=16))
    def test_runner_worker_configs(self, workers):
        """Runner should accept any valid worker count."""
        cfg = _TestConfiguration(
            modules_to_test=["SPACE"], test_types=["unit"], max_workers=workers
        )
        runner = _GeoInferTestRunner(cfg)
        assert runner.config.max_workers == workers

    @settings(max_examples=200)
    @given(st.lists(
        st.tuples(
            st.text(min_size=1, max_size=10),
            st.sampled_from(["passed", "failed", "error", "skipped"]),
            st.floats(min_value=0.0, max_value=10.0),
        ),
        min_size=1, max_size=50,
    ))
    def test_report_counts_correct(self, test_tuples):
        """Report passed/failed counts should match input."""
        cfg = _TestConfiguration(modules_to_test=["X"], test_types=["unit"])
        runner = _GeoInferTestRunner(cfg)

        # Map pytest-style statuses to runner's internal statuses
        status_map = {"passed": "PASS", "failed": "FAIL", "error": "ERROR", "skipped": "SKIP"}
        results = []
        for i, (name, status, dur) in enumerate(test_tuples):
            results.append(_TestResult(
                test_id=f"t{i}", module="X", test_name=name,
                status=status_map.get(status, status), duration=dur,
                message="", details={}
            ))
        runner.test_results = results

        report = runner._generate_execution_report(1.0)
        summary = report["execution_summary"]
        assert summary["total_tests"] == len(test_tuples)
        expected_passed = sum(1 for _, s, _ in test_tuples if s == "passed")
        assert summary["passed"] == expected_passed
