#!/usr/bin/env python3
"""
Comprehensive Test Runner for GEO-INFER-ANT

This script runs the complete test suite for the GEO-INFER-ANT framework,
including unit tests, integration tests, performance tests, and examples.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --performance      # Run only performance tests
    python run_tests.py --examples         # Run examples
    python run_tests.py --coverage         # Run with coverage analysis
    python run_tests.py --quick            # Run quick subset of tests
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_command(command, description=""):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.path.dirname(__file__))

        execution_time = time.time() - start_time

        print(f"Execution time: {execution_time".2f"} seconds")
        print(f"Return code: {result.returncode}")

        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")

        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")

        success = result.returncode == 0

        if success:
            print(f"\n✅ {description} completed successfully")
        else:
            print(f"\n❌ {description} failed")

        return success, execution_time, result.stdout, result.stderr

    except Exception as e:
        print(f"\n❌ {description} failed with exception: {e}")
        return False, time.time() - start_time, "", str(e)


def run_unit_tests():
    """Run unit tests."""
    print("\n🧪 Running Unit Tests")
    print("-" * 40)

    success, exec_time, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        "Unit Tests"
    )

    return {
        'test_type': 'unit',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr
    }


def run_integration_tests():
    """Run integration tests."""
    print("\n🔗 Running Integration Tests")
    print("-" * 40)

    success, exec_time, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
        "Integration Tests"
    )

    return {
        'test_type': 'integration',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr
    }


def run_performance_tests():
    """Run performance tests."""
    print("\n⚡ Running Performance Tests")
    print("-" * 40)

    success, exec_time, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "tests/performance/", "-v", "--tb=short"],
        "Performance Tests"
    )

    return {
        'test_type': 'performance',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr
    }


def run_examples():
    """Run example demonstrations."""
    print("\n📚 Running Examples")
    print("-" * 40)

    success, exec_time, stdout, stderr = run_command(
        [sys.executable, "examples/swarm_intelligence_demo.py"],
        "Complete Demonstration"
    )

    return {
        'test_type': 'examples',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr
    }


def run_coverage_analysis():
    """Run tests with coverage analysis."""
    print("\n📊 Running Coverage Analysis")
    print("-" * 40)

    try:
        # Check if pytest-cov is available
        import pytest_cov
        coverage_available = True
    except ImportError:
        coverage_available = False

    if coverage_available:
        success, exec_time, stdout, stderr = run_command(
            [sys.executable, "-m", "pytest", "tests/", "--cov=geo_infer_ant", "--cov-report=html", "--cov-report=term"],
            "Coverage Analysis"
        )
    else:
        print("Coverage analysis not available (install pytest-cov)")
        success, exec_time, stdout, stderr = run_command(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            "Tests without Coverage"
        )

    return {
        'test_type': 'coverage',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr,
        'coverage_available': coverage_available
    }


def run_quick_tests():
    """Run quick subset of tests for fast feedback."""
    print("\n🚀 Running Quick Tests")
    print("-" * 40)

    success, exec_time, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "tests/unit/test_core.py", "-v"],
        "Quick Core Tests"
    )

    return {
        'test_type': 'quick',
        'success': success,
        'execution_time': exec_time,
        'output': stdout,
        'errors': stderr
    }


def generate_test_report(results):
    """Generate comprehensive test report."""
    print("\n📋 Generating Test Report")
    print("-" * 40)

    report = {
        'test_session': {
            'start_time': datetime.now().isoformat(),
            'total_tests': len(results),
            'successful_tests': sum(1 for r in results if r['success']),
            'failed_tests': sum(1 for r in results if not r['success']),
            'total_execution_time': sum(r['execution_time'] for r in results)
        },
        'results': results,
        'summary': {}
    }

    # Generate summary
    if results:
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]

        report['summary'] = {
            'success_rate': len(successful_tests) / len(results) if results else 0,
            'avg_execution_time': sum(r['execution_time'] for r in results) / len(results) if results else 0,
            'fastest_test': min(results, key=lambda r: r['execution_time']) if results else None,
            'slowest_test': max(results, key=lambda r: r['execution_time']) if results else None
        }

        # Detailed breakdown
        report['summary']['by_type'] = {}
        for result in results:
            test_type = result['test_type']
            if test_type not in report['summary']['by_type']:
                report['summary']['by_type'][test_type] = {
                    'count': 0,
                    'successful': 0,
                    'total_time': 0.0
                }

            report['summary']['by_type'][test_type]['count'] += 1
            report['summary']['by_type'][test_type]['total_time'] += result['execution_time']
            if result['success']:
                report['summary']['by_type'][test_type]['successful'] += 1

    # Save report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Test report saved to: {report_file}")

    return report


def print_final_summary(report):
    """Print final test summary."""
    print("\n" + "="*60)
    print("🧪 GEO-INFER-ANT TEST SUMMARY")
    print("="*60)

    session = report['test_session']
    summary = report['summary']

    print(f"Total Tests: {session['total_tests']}")
    print(f"Successful: {session['successful_tests']}")
    print(f"Failed: {session['failed_tests']}")
    print(f"Success Rate: {summary['success_rate']".1%"}")
    print(f"Total Time: {session['total_execution_time']".2f"} seconds")
    print(f"Average Time: {summary['avg_execution_time']".2f"} seconds")

    if summary['by_type']:
        print("\n📊 By Test Type:")
        for test_type, stats in summary['by_type'].items():
            success_rate = stats['successful'] / stats['count'] if stats['count'] > 0 else 0
            print(f"  {test_type}: {stats['successful']}/{stats['count']} ({success_rate:.1%}, {stats['total_time']:.1f}s)")

    print("\n🎯 Overall Status:")
    if session['failed_tests'] == 0:
        print("✅ ALL TESTS PASSED!")
        print("🎉 GEO-INFER-ANT is ready for use!")
    else:
        print(f"❌ {session['failed_tests']} TESTS FAILED")
        print("🔧 Check test outputs for details")

    print("="*60)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description='GEO-INFER-ANT Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--performance', action='store_true', help='Run only performance tests')
    parser.add_argument('--examples', action='store_true', help='Run examples')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage analysis')
    parser.add_argument('--quick', action='store_true', help='Run quick subset of tests')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')

    args = parser.parse_args()

    print("🚀 GEO-INFER-ANT Comprehensive Test Runner")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")

    results = []

    # Determine which tests to run
    run_all = not (args.unit or args.integration or args.performance or args.examples or args.quick)

    if args.quick or run_all:
        print("\n⚡ Running Quick Tests (Core Components)")
        quick_result = run_quick_tests()
        results.append(quick_result)

    if args.unit or run_all:
        print("\n🧪 Running Unit Tests")
        unit_result = run_unit_tests()
        results.append(unit_result)

    if args.integration or run_all:
        print("\n🔗 Running Integration Tests")
        integration_result = run_integration_tests()
        results.append(integration_result)

    if args.performance or run_all:
        print("\n⚡ Running Performance Tests")
        performance_result = run_performance_tests()
        results.append(performance_result)

    if args.examples or run_all:
        print("\n📚 Running Examples")
        examples_result = run_examples()
        results.append(examples_result)

    if args.coverage:
        print("\n📊 Running Coverage Analysis")
        coverage_result = run_coverage_analysis()
        results.append(coverage_result)

    # Generate and display report
    report = generate_test_report(results)
    print_final_summary(report)

    # Exit with appropriate code
    if report['test_session']['failed_tests'] > 0:
        print(f"\n❌ {report['test_session']['failed_tests']} tests failed")
        return 1
    else:
        print("\n✅ All tests completed successfully!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
