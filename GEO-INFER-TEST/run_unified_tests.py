#!/usr/bin/env python3
"""
GEO-INFER Unified Test Suite Runner

This script demonstrates the comprehensive testing capabilities of the GEO-INFER framework,
running tests across all modules with detailed reporting and performance monitoring.
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import shutil

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description, timeout=300):
    """Run a command and return results."""
    print(f"\n🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   ✅ Completed in {duration:.2f}s")
            return {
                'success': True,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"   ❌ Failed after {duration:.2f}s")
            print(f"   Error: {result.stderr}")
            return {
                'success': False,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after {timeout}s")
        return {
            'success': False,
            'duration': timeout,
            'stdout': '',
            'stderr': f'Command timed out after {timeout} seconds'
        }
    except Exception as e:
        print(f"   💥 Exception: {e}")
        return {
            'success': False,
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': str(e)
        }

def run_test_category(category, description, test_path=None):
    """Run tests for a specific category."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    if test_path is None:
        test_path = f"GEO-INFER-TEST/tests/{category}"
    
    cmd = [
        "python", "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--durations=10",
        f"--junitxml=test-results/{category}_results.xml",
        f"--html=test-results/{category}_report.html",
        "--self-contained-html"
    ]
    
    return run_command(cmd, f"Running {category} tests")

def run_performance_tests():
    """Run performance tests."""
    print(f"\n{'='*60}")
    print(f"⚡ Performance Testing")
    print(f"{'='*60}")
    
    cmd = [
        "python", "-m", "pytest",
        "GEO-INFER-TEST/tests/",
        "-m", "performance",
        "-v",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-min-rounds=3"
    ]
    
    return run_command(cmd, "Running performance benchmarks")

def run_coverage_analysis():
    """Run coverage analysis."""
    print(f"\n{'='*60}")
    print(f"📊 Coverage Analysis")
    print(f"{'='*60}")
    
    cmd = [
        "python", "-m", "pytest",
        "GEO-INFER-TEST/tests/",
        "--cov=GEO-INFER-TEST",
        "--cov-report=html:test-results/coverage",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    return run_command(cmd, "Running coverage analysis")

def run_all_tests():
    """Run all test categories."""
    print("🚀 GEO-INFER Unified Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create test results directory
    results_dir = Path("test-results")
    results_dir.mkdir(exist_ok=True)
    
    # Clean previous results
    for file in results_dir.glob("*"):
        if file.is_file():
            file.unlink()
    
    test_results = {}
    
    # Run different test categories
    test_categories = [
        ("unit", "Unit Tests", "Testing individual functions and classes"),
        ("integration", "Integration Tests", "Testing cross-module interactions"),
    ]
    
    for category, title, description in test_categories:
        result = run_test_category(category, description)
        test_results[category] = result
    
    # Run performance tests
    perf_result = run_performance_tests()
    test_results['performance'] = perf_result
    
    # Run coverage analysis
    coverage_result = run_coverage_analysis()
    test_results['coverage'] = coverage_result
    
    # Generate summary report
    generate_summary_report(test_results)
    
    return test_results

def generate_summary_report(results):
    """Generate a comprehensive summary report."""
    print(f"\n{'='*60}")
    print(f"📋 Test Summary Report")
    print(f"{'='*60}")
    
    total_tests = 0
    passed_tests = 0
    total_duration = 0
    
    for category, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = result['duration']
        total_duration += duration
        
        print(f"{category.upper():15} {status:10} {duration:8.2f}s")
        
        if result['success']:
            passed_tests += 1
        total_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nOverall Results:")
    print(f"  Total Categories: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Total Duration: {total_duration:.2f}s")
    
    # Save detailed results
    results_file = Path("test-results/detailed_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    print(f"Coverage report: test-results/coverage/index.html")
    print(f"HTML reports: test-results/*_report.html")

def run_specific_module_tests(module_name):
    """Run tests for a specific GEO-INFER module."""
    print(f"\n🔍 Running tests for module: {module_name}")
    
    # Check if module has tests
    module_test_path = f"GEO-INFER-{module_name}/tests"
    if Path(module_test_path).exists():
        cmd = [
            "python", "-m", "pytest",
            module_test_path,
            "-v",
            "--tb=short"
        ]
        
        return run_command(cmd, f"Running {module_name} module tests")
    else:
        print(f"   ⚠️  No tests found for module {module_name}")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': f'No tests found in {module_test_path}'
        }

def run_h3_migration_tests():
    """Run H3 v4 migration tests."""
    print(f"\n{'='*60}")
    print(f"🔧 H3 v4 Migration Tests")
    print(f"{'='*60}")
    
    # Test H3 v4 functionality
    try:
        import h3
        print("   ✅ H3 v4 library imported successfully")
        
        # Test basic H3 v4 functionality
        lat, lng = 37.7749, -122.4194
        resolution = 10
        
        h3_cell = h3.latlng_to_cell(lat, lng, resolution)
        print(f"   ✅ H3 cell creation: {h3_cell}")
        
        # Test cell to latlng conversion
        cell_lat, cell_lng = h3.cell_to_latlng(h3_cell)
        print(f"   ✅ H3 cell to latlng: ({cell_lat:.6f}, {cell_lng:.6f})")
        
        # Test grid disk
        neighbors = h3.grid_disk(h3_cell, 2)
        print(f"   ✅ H3 grid disk: {len(neighbors)} neighbors")
        
        return {
            'success': True,
            'duration': 0.1,
            'stdout': 'H3 v4 migration tests passed',
            'stderr': ''
        }
        
    except ImportError as e:
        print(f"   ❌ H3 v4 library not available: {e}")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': f'H3 v4 library not available: {e}'
        }
    except Exception as e:
        print(f"   ❌ H3 v4 test failed: {e}")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': f'H3 v4 test failed: {e}'
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="GEO-INFER Unified Test Suite Runner")
    parser.add_argument("--category", choices=["unit", "integration", "performance", "coverage", "all"],
                       default="all", help="Test category to run")
    parser.add_argument("--module", help="Specific module to test")
    parser.add_argument("--h3-migration", action="store_true", help="Run H3 v4 migration tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Verbose mode enabled")
    
    if args.h3_migration:
        run_h3_migration_tests()
        return
    
    if args.module:
        run_specific_module_tests(args.module)
        return
    
    if args.category == "all":
        run_all_tests()
    elif args.category == "unit":
        run_test_category("unit", "Unit Tests")
    elif args.category == "integration":
        run_test_category("integration", "Integration Tests")
    elif args.category == "performance":
        run_performance_tests()
    elif args.category == "coverage":
        run_coverage_analysis()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\nTest execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 