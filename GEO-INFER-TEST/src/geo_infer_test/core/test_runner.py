"""
Main test runner for the GEO-INFER-TEST framework.

This module provides the core test execution engine that can run tests
across all GEO-INFER modules with comprehensive logging and reporting.
"""

import pytest
import asyncio
import importlib
import inspect
from typing import Dict, List, Any, Optional, Union, Type, Callable
from pathlib import Path
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time

from .log_integration import LogIntegration, TestLogEntry


@dataclass
class TestConfiguration:
    """Configuration for test execution."""
    modules_to_test: List[str]
    test_types: List[str]  # ['unit', 'integration', 'performance', 'load']
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    fail_fast: bool = False
    coverage_enabled: bool = True
    performance_benchmarks: bool = True
    log_integration_enabled: bool = True


@dataclass
class TestResult:
    """Result of a test execution."""
    test_id: str
    module: str
    test_name: str
    status: str
    duration: float
    message: str
    details: Dict[str, Any]
    performance_metrics: Optional[Dict[str, float]] = None


class GeoInferTestRunner:
    """
    Main test runner for the GEO-INFER ecosystem.
    
    Provides comprehensive test execution capabilities across all modules
    with integration to GEO-INFER-LOG for detailed monitoring and reporting.
    """
    
    # All available GEO-INFER modules
    AVAILABLE_MODULES = [
        'ACT', 'AG', 'AI', 'AGENT', 'ANT', 'API', 'APP', 'ART', 'BAYES',
        'BIO', 'CIV', 'COG', 'COMMS', 'DATA', 'ECON', 'GIT', 'HEALTH',
        'INTRA', 'LOG', 'MATH', 'NORMS', 'OPS', 'ORG', 'PEP', 'REQ',
        'RISK', 'SEC', 'SIM', 'SPACE', 'SPM', 'TEST', 'TIME'
    ]
    
    def __init__(self, config: TestConfiguration):
        """Initialize the test runner."""
        self.config = config
        self.log_integration = LogIntegration() if config.log_integration_enabled else None
        self.test_results: List[TestResult] = []
        self.discovered_tests: Dict[str, List[str]] = {}
        self._setup_test_environment()
    
    def _setup_test_environment(self):
        """Set up the testing environment."""
        # Ensure test directories exist
        test_dirs = ['unit', 'integration', 'performance', 'load']
        for test_dir in test_dirs:
            Path(f'tests/{test_dir}').mkdir(parents=True, exist_ok=True)
        
        # Setup logging if enabled
        if self.log_integration:
            self.log_integration.logger.info("GeoInferTestRunner initialized")
    
    def discover_tests(self) -> Dict[str, List[str]]:
        """
        Discover all available tests across specified modules.
        
        Returns:
            Dictionary mapping module names to lists of discovered test functions
        """
        discovered = {}
        
        for module in self.config.modules_to_test:
            if module not in self.AVAILABLE_MODULES:
                if self.log_integration:
                    self.log_integration.logger.warning(f"Unknown module: {module}")
                continue
            
            module_tests = self._discover_module_tests(module)
            if module_tests:
                discovered[module] = module_tests
                if self.log_integration:
                    self.log_integration.logger.info(
                        f"Discovered {len(module_tests)} tests for module {module}"
                    )
        
        self.discovered_tests = discovered
        return discovered
    
    def _discover_module_tests(self, module: str) -> List[str]:
        """Discover tests for a specific module."""
        tests = []
        
        # Look for module test directory
        module_test_dir = Path(f'GEO-INFER-{module}/tests')
        if not module_test_dir.exists():
            return tests
        
        # Discover test files
        for test_type in self.config.test_types:
            test_type_dir = module_test_dir / test_type
            if test_type_dir.exists():
                test_files = list(test_type_dir.glob('test_*.py'))
                for test_file in test_files:
                    tests.append(f"{module}::{test_type}::{test_file.stem}")
        
        return tests
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Execute all discovered tests with comprehensive logging and reporting.
        
        Returns:
            Comprehensive test execution report
        """
        if not self.discovered_tests:
            self.discover_tests()
        
        start_time = time.time()
        
        if self.log_integration:
            self.log_integration.logger.info("Starting comprehensive test execution")
        
        if self.config.parallel_execution:
            self._run_tests_parallel()
        else:
            self._run_tests_sequential()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Generate comprehensive report
        report = self._generate_execution_report(total_duration)
        
        if self.log_integration:
            self.log_integration.logger.info(
                f"Test execution completed in {total_duration:.2f}s"
            )
        
        return report
    
    def _run_tests_parallel(self):
        """Execute tests in parallel using thread/process pools."""
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            
            for module, tests in self.discovered_tests.items():
                for test in tests:
                    future = executor.submit(self._execute_single_test, module, test)
                    futures.append(future)
            
            # Wait for all tests to complete
            for future in futures:
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    if result:
                        self.test_results.append(result)
                except Exception as e:
                    if self.log_integration:
                        self.log_integration.logger.error(f"Test execution error: {e}")
    
    def _run_tests_sequential(self):
        """Execute tests sequentially."""
        for module, tests in self.discovered_tests.items():
            for test in tests:
                try:
                    result = self._execute_single_test(module, test)
                    if result:
                        self.test_results.append(result)
                        
                        # Check fail-fast
                        if (self.config.fail_fast and 
                            result.status in ['FAIL', 'ERROR']):
                            if self.log_integration:
                                self.log_integration.logger.warning(
                                    "Stopping execution due to fail-fast mode"
                                )
                            return
                            
                except Exception as e:
                    if self.log_integration:
                        self.log_integration.logger.error(f"Test execution error: {e}")
    
    def _execute_single_test(self, module: str, test: str) -> Optional[TestResult]:
        """Execute a single test with comprehensive logging."""
        test_id = f"{module}_{test}_{int(time.time())}"
        
        # Parse test information
        parts = test.split('::')
        if len(parts) != 3:
            return None
        
        module_name, test_type, test_file = parts
        test_name = f"{test_type}_{test_file}"
        
        start_time = time.time()
        
        try:
            if self.log_integration:
                with self.log_integration.test_context(test_id, module, test_name):
                    # Execute the actual test
                    result = self._run_pytest_test(module, test_type, test_file)
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    return TestResult(
                        test_id=test_id,
                        module=module,
                        test_name=test_name,
                        status='PASS' if result else 'FAIL',
                        duration=duration,
                        message="Test execution completed",
                        details={'test_type': test_type, 'test_file': test_file}
                    )
            else:
                # Execute without log integration
                result = self._run_pytest_test(module, test_type, test_file)
                end_time = time.time()
                duration = end_time - start_time
                
                return TestResult(
                    test_id=test_id,
                    module=module,
                    test_name=test_name,
                    status='PASS' if result else 'FAIL',
                    duration=duration,
                    message="Test execution completed",
                    details={'test_type': test_type, 'test_file': test_file}
                )
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            return TestResult(
                test_id=test_id,
                module=module,
                test_name=test_name,
                status='ERROR',
                duration=duration,
                message=f"Test execution failed: {str(e)}",
                details={'error': str(e), 'test_type': test_type, 'test_file': test_file}
            )
    
    def _run_pytest_test(self, module: str, test_type: str, test_file: str) -> bool:
        """Execute a pytest test file."""
        test_path = Path(f'GEO-INFER-{module}/tests/{test_type}/{test_file}.py')
        
        if not test_path.exists():
            return False
        
        # Run pytest programmatically
        exit_code = pytest.main([
            str(test_path),
            '-v',
            '--tb=short',
            '--disable-warnings'
        ])
        
        return exit_code == 0
    
    def _generate_execution_report(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test execution report."""
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.status == 'PASS')
        failed = sum(1 for r in self.test_results if r.status == 'FAIL')
        errors = sum(1 for r in self.test_results if r.status == 'ERROR')
        
        module_summaries = {}
        for result in self.test_results:
            module = result.module
            if module not in module_summaries:
                module_summaries[module] = {
                    'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'duration': 0.0
                }
            
            summary = module_summaries[module]
            summary['total'] += 1
            summary['duration'] += result.duration
            
            if result.status == 'PASS':
                summary['passed'] += 1
            elif result.status == 'FAIL':
                summary['failed'] += 1
            elif result.status == 'ERROR':
                summary['errors'] += 1
        
        report = {
            'execution_summary': {
                'total_tests': total_tests,
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'success_rate': (passed / total_tests * 100) if total_tests > 0 else 0,
                'total_duration': total_duration
            },
            'module_summaries': module_summaries,
            'test_results': [
                {
                    'test_id': r.test_id,
                    'module': r.module,
                    'test_name': r.test_name,
                    'status': r.status,
                    'duration': r.duration,
                    'message': r.message,
                    'details': r.details
                }
                for r in self.test_results
            ],
            'configuration': {
                'modules_tested': self.config.modules_to_test,
                'test_types': self.config.test_types,
                'parallel_execution': self.config.parallel_execution,
                'max_workers': self.config.max_workers,
                'log_integration_enabled': self.config.log_integration_enabled
            }
        }
        
        return report
    
    def run_module_tests(self, module: str) -> Dict[str, Any]:
        """Run tests for a specific module only."""
        if module not in self.AVAILABLE_MODULES:
            raise ValueError(f"Unknown module: {module}")
        
        # Temporarily modify config to test only this module
        original_modules = self.config.modules_to_test
        self.config.modules_to_test = [module]
        
        try:
            # Discover and run tests for this module
            self.discovered_tests = {module: self._discover_module_tests(module)}
            report = self.run_all_tests()
            return report
        finally:
            # Restore original configuration
            self.config.modules_to_test = original_modules
    
    def run_cross_module_tests(self) -> Dict[str, Any]:
        """Run tests that verify cross-module integration."""
        if self.log_integration:
            self.log_integration.logger.info("Starting cross-module integration tests")
        
        # This would implement comprehensive cross-module testing
        # For now, return a placeholder
        return {
            'cross_module_tests': 'Not yet implemented',
            'integration_status': 'Planned for future release'
        } 