#!/usr/bin/env python3
"""
GEO-INFER Unified Test Suite Runner

Enhanced to support:
- Dynamic discovery of all GEO-INFER modules
- Module-specific test execution
- Cross-module integration testing
- Comprehensive reporting across all modules
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess
import tempfile
import shutil
import glob

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Constants
MODULE_PREFIX = "GEO-INFER-"
TEST_DIR_NAME = "tests"

def discover_geo_infer_modules():
    """Discover all GEO-INFER modules in the project."""
    modules = []
    for item in project_root.iterdir():
        if item.is_dir() and item.name.startswith(MODULE_PREFIX):
            module_name = item.name[len(MODULE_PREFIX):]
            test_path = item / TEST_DIR_NAME
            if test_path.exists() and any(test_path.iterdir()):
                modules.append({
                    'name': module_name,
                    'path': str(item),
                    'test_path': str(test_path),
                    'has_tests': True
                })
            else:
                modules.append({
                    'name': module_name,
                    'path': str(item),
                    'test_path': str(test_path),
                    'has_tests': False
                })
    return modules

def run_command(cmd, description, timeout=300, cwd=None):
    """Run a command and return results."""
    print(f"\n🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    if cwd:
        print(f"   Working directory: {cwd}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
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

def run_module_tests(module, timeout=300):
    """Run tests for a specific GEO-INFER module."""
    if not module['has_tests']:
        print(f"   ⚠️  No tests found for module {module['name']}")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': f"No tests found in {module['test_path']}"
        }
    
    print(f"\n{'='*60}")
    print(f"🧪 Running tests for module: {module['name']}")
    print(f"{'='*60}")
    
    cmd = [
        "python", "-m", "pytest",
        module['test_path'],
        "-v",
        "--tb=short",
        "--durations=10",
        f"--junitxml=test-results/{module['name']}_results.xml",
        f"--html=test-results/{module['name']}_report.html",
        "--self-contained-html"
    ]
    
    return run_command(cmd, f"Testing {module['name']} module", timeout, cwd=project_root)

def run_cross_module_tests():
    """Run cross-module integration tests."""
    print(f"\n{'='*60}")
    print(f"🔗 Running Cross-Module Integration Tests")
    print(f"{'='*60}")
    
    # Look for integration tests in the GEO-INFER-TEST module
    integration_test_path = project_root / "GEO-INFER-TEST" / "tests" / "integration"
    if not integration_test_path.exists():
        print("   ⚠️  No cross-module integration tests found")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': f'Integration test path not found: {integration_test_path}'
        }
    
    cmd = [
        "python", "-m", "pytest",
        str(integration_test_path),
        "-v",
        "--tb=short",
        f"--junitxml=test-results/integration_results.xml",
        f"--html=test-results/integration_report.html",
        "--self-contained-html"
    ]
    
    return run_command(cmd, "Cross-module integration testing", cwd=project_root)

def run_performance_tests():
    """Run performance tests across all modules."""
    print(f"\n{'='*60}")
    print(f"⚡ Performance Testing")
    print(f"{'='*60}")
    
    # Find all performance tests across modules
    perf_tests = []
    for module in discover_geo_infer_modules():
        if module['has_tests']:
            perf_path = Path(module['test_path']) / "test_performance.py"
            if perf_path.exists():
                perf_tests.append(str(perf_path))
    
    if not perf_tests:
        print("   ⚠️  No performance tests found")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': 'No performance tests found'
        }
    
    cmd = [
        "python", "-m", "pytest",
        *perf_tests,
        "-v",
        "--benchmark-only",
        "--benchmark-sort=mean",
        "--benchmark-min-rounds=3"
    ]
    
    return run_command(cmd, "Performance benchmarks", cwd=project_root)

def run_coverage_analysis():
    """Run coverage analysis across all modules."""
    print(f"\n{'='*60}")
    print(f"📊 Coverage Analysis")
    print(f"{'='*60}")
    
    # Find all source directories
    source_dirs = []
    for module in discover_geo_infer_modules():
        src_path = Path(module['path']) / "src"
        if src_path.exists():
            source_dirs.append(str(src_path))
    
    if not source_dirs:
        print("   ⚠️  No source directories found for coverage")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': 'No source directories found'
        }
    
    # Find all test files
    test_files = []
    for module in discover_geo_infer_modules():
        if module['has_tests']:
            test_files.extend(glob.glob(f"{module['test_path']}/test_*.py"))
    
    if not test_files:
        print("   ⚠️  No test files found for coverage")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': 'No test files found'
        }
    
    cmd = [
        "python", "-m", "pytest",
        *test_files,
        f"--cov={','.join(source_dirs)}",
        "--cov-report=html:test-results/coverage",
        "--cov-report=term-missing",
        "--cov-fail-under=80"
    ]
    
    return run_command(cmd, "Coverage analysis", cwd=project_root)

def run_all_tests():
    """Run all test categories across all modules."""
    print("🚀 GEO-INFER Unified Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create test results directory
    results_dir = project_root / "test-results"
    results_dir.mkdir(exist_ok=True)
    
    # Clean previous results
    for file in results_dir.glob("*"):
        if file.is_file():
            file.unlink()
    
    test_results = {}
    modules = discover_geo_infer_modules()
    
    # Run tests for each module
    for module in modules:
        result = run_module_tests(module)
        test_results[module['name']] = result
    
    # Run cross-module integration tests
    integration_result = run_cross_module_tests()
    test_results['integration'] = integration_result
    
    # Run performance tests
    perf_result = run_performance_tests()
    test_results['performance'] = perf_result
    
    # Run coverage analysis
    coverage_result = run_coverage_analysis()
    test_results['coverage'] = coverage_result
    
    # Generate summary report
    generate_summary_report(test_results, modules)
    
    return test_results

def generate_summary_report(results, modules):
    """Generate a comprehensive summary report."""
    print(f"\n{'='*60}")
    print(f"📋 Test Summary Report")
    print(f"{'='*60}")
    
    total_tests = 0
    passed_tests = 0
    total_duration = 0
    
    # Module results
    print("\nModule Test Results:")
    for module in modules:
        if module['name'] in results:
            result = results[module['name']]
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            total_duration += duration
            has_tests = "YES" if module['has_tests'] else "NO"
            
            print(f"{module['name']:15} {status:10} {duration:8.2f}s  Tests: {has_tests}")
            
            if result['success']:
                passed_tests += 1
            total_tests += 1
    
    # Additional test categories
    categories = ['integration', 'performance', 'coverage']
    print("\nAdditional Test Categories:")
    for category in categories:
        if category in results:
            result = results[category]
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            total_duration += duration
            
            print(f"{category.capitalize():15} {status:10} {duration:8.2f}s")
            
            if result['success']:
                passed_tests += 1
            total_tests += 1
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\nOverall Results:")
    print(f"  Total Test Categories: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {total_tests - passed_tests}")
    print(f"  Success Rate: {success_rate:.1f}%")
    print(f"  Total Duration: {total_duration:.2f}s")