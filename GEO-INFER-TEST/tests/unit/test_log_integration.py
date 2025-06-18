"""
Unit tests for GEO-INFER-TEST log integration functionality.

This test file demonstrates the testing capabilities and validates
the integration with the GEO-INFER-LOG module.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

# Import the modules we're testing
try:
    from geo_infer_test.core.log_integration import (
        LogIntegration, LoggingTestReporter, TestLogger, LogAnalyzer,
        TestLogEntry, ModuleTestSummary
    )
except ImportError:
    pytest.skip("GEO-INFER-TEST modules not available", allow_module_level=True)


class TestLogIntegration:
    """Test suite for the LogIntegration class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_config = {
            'level': 'INFO',
            'log_dir': self.temp_dir,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    
    def test_log_integration_initialization(self):
        """Test that LogIntegration initializes properly."""
        log_integration = LogIntegration(self.log_config)
        
        assert log_integration.log_config == self.log_config
        assert log_integration.test_entries == []
        assert log_integration.module_summaries == {}
        assert log_integration.logger is not None
    
    def test_test_context_manager_success(self):
        """Test the test context manager with a successful test."""
        log_integration = LogIntegration(self.log_config)
        
        with log_integration.test_context("test_001", "SPACE", "test_h3_indexing"):
            # Simulate successful test execution
            time.sleep(0.01)
        
        # Verify the test was logged
        assert len(log_integration.test_entries) == 1
        entry = log_integration.test_entries[0]
        
        assert entry.test_id == "test_001"
        assert entry.module == "SPACE"
        assert entry.test_name == "test_h3_indexing"
        assert entry.status == "PASS"
        assert entry.duration > 0
    
    def test_test_context_manager_failure(self):
        """Test the test context manager with a failing test."""
        log_integration = LogIntegration(self.log_config)
        
        with pytest.raises(ValueError):
            with log_integration.test_context("test_002", "TIME", "test_temporal_analysis"):
                # Simulate test failure
                raise ValueError("Test failed")
        
        # Verify the test failure was logged
        assert len(log_integration.test_entries) == 1
        entry = log_integration.test_entries[0]
        
        assert entry.test_id == "test_002"
        assert entry.module == "TIME"
        assert entry.test_name == "test_temporal_analysis"
        assert entry.status == "FAIL"
        assert entry.error_info is not None
        assert "ValueError" in entry.error_info['exception_type']
    
    def test_module_summary_updates(self):
        """Test that module summaries are updated correctly."""
        log_integration = LogIntegration(self.log_config)
        
        # Add multiple test results for the same module
        with log_integration.test_context("test_003", "AI", "test_prediction"):
            pass
        
        with pytest.raises(RuntimeError):
            with log_integration.test_context("test_004", "AI", "test_training"):
                raise RuntimeError("Training failed")
        
        # Check module summary
        assert "AI" in log_integration.module_summaries
        summary = log_integration.module_summaries["AI"]
        
        assert summary.module_name == "AI"
        assert summary.total_tests == 2
        assert summary.passed == 1
        assert summary.failed == 0
        assert summary.errors == 1  # RuntimeError counts as error
    
    @patch('geo_infer_test.core.log_integration.LOG_MODULE_AVAILABLE', False)
    def test_log_integration_without_log_module(self):
        """Test LogIntegration when GEO-INFER-LOG is not available."""
        log_integration = LogIntegration(self.log_config)
        
        assert log_integration.log_available is False
        
        # Should still work without the LOG module
        with log_integration.test_context("test_005", "BAYES", "test_inference"):
            pass
        
        assert len(log_integration.test_entries) == 1


class TestLoggingTestReporter:
    """Test suite for the LoggingTestReporter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_config = {'log_dir': self.temp_dir}
        self.log_integration = LogIntegration(self.log_config)
    
    def test_report_generation(self):
        """Test comprehensive report generation."""
        # Add some test data
        with self.log_integration.test_context("test_006", "SPACE", "test_coordinates"):
            pass
        
        with pytest.raises(AssertionError):
            with self.log_integration.test_context("test_007", "SPACE", "test_projections"):
                raise AssertionError("Projection test failed")
        
        # Generate report
        reporter = LoggingTestReporter(self.log_integration)
        output_dir = Path(self.temp_dir) / "reports"
        report_data = reporter.generate_test_report(output_dir)
        
        # Verify report structure
        assert 'timestamp' in report_data
        assert 'summary' in report_data
        assert 'module_summaries' in report_data
        assert 'test_entries' in report_data
        
        # Verify summary data
        summary = report_data['summary']
        assert summary['total_tests'] == 2
        assert summary['passed'] == 1
        assert summary['failed'] == 1
        assert summary['success_rate'] == 50.0
    
    def test_report_file_creation(self):
        """Test that report files are actually created."""
        # Add a test entry
        with self.log_integration.test_context("test_008", "DATA", "test_loading"):
            pass
        
        reporter = LoggingTestReporter(self.log_integration)
        output_dir = Path(self.temp_dir) / "reports"
        reporter.generate_test_report(output_dir)
        
        # Check that JSON report was created
        json_reports = list(output_dir.glob("test_report_*.json"))
        assert len(json_reports) >= 1
        
        # Verify JSON content
        import json
        with open(json_reports[0]) as f:
            report_data = json.load(f)
        
        assert report_data['summary']['total_tests'] == 1


class TestLogAnalyzer:
    """Test suite for the LogAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.log_integration = LogIntegration({})
        
        # Add diverse test data for analysis
        test_scenarios = [
            ("test_001", "SPACE", "test_fast", 0.1, "PASS"),
            ("test_002", "SPACE", "test_slow", 1.0, "PASS"),
            ("test_003", "TIME", "test_quick", 0.2, "PASS"),
            ("test_004", "TIME", "test_failure", 0.3, "FAIL"),
            ("test_005", "AI", "test_success", 0.15, "PASS"),
        ]
        
        for test_id, module, test_name, duration, status in test_scenarios:
            # Manually create test entries for analysis
            import datetime
            entry = TestLogEntry(
                timestamp=datetime.datetime.now(),
                test_id=test_id,
                module=module,
                test_name=test_name,
                status=status,
                duration=duration,
                message=f"Test {status.lower()}",
                details={}
            )
            self.log_integration.test_entries.append(entry)
            
            # Update module summaries
            if module not in self.log_integration.module_summaries:
                self.log_integration.module_summaries[module] = ModuleTestSummary(
                    module_name=module,
                    total_tests=0,
                    passed=0,
                    failed=0,
                    skipped=0,
                    errors=0,
                    total_duration=0.0
                )
            
            summary = self.log_integration.module_summaries[module]
            summary.total_tests += 1
            summary.total_duration += duration
            
            if status == "PASS":
                summary.passed += 1
            elif status == "FAIL":
                summary.failed += 1
    
    def test_test_pattern_analysis(self):
        """Test analysis of test execution patterns."""
        analyzer = LogAnalyzer(self.log_integration)
        analysis = analyzer.analyze_test_patterns()
        
        assert 'total_tests_analyzed' in analysis
        assert analysis['total_tests_analyzed'] == 5
        
        assert 'module_reliability' in analysis
        
        # Check SPACE module reliability
        space_reliability = analysis['module_reliability']['SPACE']
        assert space_reliability['success_rate'] == 100.0  # 2/2 passed
        
        # Check TIME module reliability
        time_reliability = analysis['module_reliability']['TIME']
        assert time_reliability['success_rate'] == 50.0  # 1/2 passed
    
    def test_performance_bottleneck_detection(self):
        """Test identification of performance bottlenecks."""
        analyzer = LogAnalyzer(self.log_integration)
        bottlenecks = analyzer.identify_performance_bottlenecks()
        
        # Should identify the slow test (1.0s when average is much lower)
        assert len(bottlenecks) >= 1
        
        slow_test = next((b for b in bottlenecks if b['test_name'] == 'test_slow'), None)
        assert slow_test is not None
        assert slow_test['duration'] == 1.0
        assert slow_test['slowness_factor'] > 2.0  # Much slower than average


class TestTestLogger:
    """Test suite for the TestLogger class."""
    
    def test_performance_metrics_logging(self):
        """Test logging of performance metrics."""
        log_integration = LogIntegration({})
        test_logger = TestLogger(log_integration)
        
        # Create a test entry first
        with log_integration.test_context("test_009", "MATH", "test_calculations"):
            pass
        
        # Log performance metrics
        metrics = {
            'cpu_usage': 45.2,
            'memory_mb': 128.5,
            'operations_per_second': 1500
        }
        
        test_logger.log_performance_metrics("test_009", metrics)
        
        # Verify metrics were added to the test entry
        entry = log_integration.test_entries[0]
        assert entry.performance_metrics == metrics
    
    def test_module_health_logging(self):
        """Test logging of module health information."""
        log_integration = LogIntegration({})
        test_logger = TestLogger(log_integration)
        
        health_data = {
            'status': 'healthy',
            'response_time': 0.05,
            'last_error': None
        }
        
        # This should not raise an exception
        test_logger.log_module_health("SPACE", health_data)
    
    def test_cross_module_interaction_logging(self):
        """Test logging of cross-module interactions."""
        log_integration = LogIntegration({})
        test_logger = TestLogger(log_integration)
        
        # This should not raise an exception
        test_logger.log_cross_module_interaction(
            "SPACE", "TIME", "data_flow", "success"
        )


# Integration test demonstrating the full workflow
def test_full_workflow_integration():
    """Integration test demonstrating the complete testing workflow."""
    log_integration = LogIntegration({})
    
    # Simulate a complete testing session
    test_cases = [
        ("integration_001", "SPACE", "test_h3_integration", True),
        ("integration_002", "TIME", "test_temporal_ops", True),
        ("integration_003", "AI", "test_model_training", False),
        ("integration_004", "SPACE", "test_coordinate_transform", True),
    ]
    
    for test_id, module, test_name, should_pass in test_cases:
        try:
            with log_integration.test_context(test_id, module, test_name):
                if not should_pass:
                    raise RuntimeError("Simulated test failure")
                time.sleep(0.01)  # Simulate work
        except RuntimeError:
            pass  # Expected for failing tests
    
    # Generate comprehensive report
    reporter = LoggingTestReporter(log_integration)
    with tempfile.TemporaryDirectory() as temp_dir:
        report_data = reporter.generate_test_report(Path(temp_dir))
    
    # Analyze patterns
    analyzer = LogAnalyzer(log_integration)
    analysis = analyzer.analyze_test_patterns()
    bottlenecks = analyzer.identify_performance_bottlenecks()
    
    # Verify the workflow completed successfully
    assert len(log_integration.test_entries) == 4
    assert report_data['summary']['total_tests'] == 4
    assert report_data['summary']['success_rate'] == 75.0  # 3/4 passed
    assert len(analysis['module_reliability']) == 3  # 3 different modules
    
    print("✅ Full workflow integration test completed successfully!") 