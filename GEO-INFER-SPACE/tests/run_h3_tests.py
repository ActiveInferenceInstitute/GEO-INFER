#!/usr/bin/env python3
"""
H3 Module Test Runner

Comprehensive test runner for all H3 module tests.
Runs unit tests, integration tests, and performance tests.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import pytest
import sys
import os
import time
import subprocess
from pathlib import Path


def run_tests(test_pattern: str = "test_h3_*.py", verbose: bool = True):
    """
    Run H3 module tests.
    
    Args:
        test_pattern: Pattern to match test files
        verbose: Whether to run tests in verbose mode
    """
    # Get the tests directory
    tests_dir = Path(__file__).parent
    
    # Add src directory to Python path
    src_dir = tests_dir.parent / "src"
    sys.path.insert(0, str(src_dir))
    
    # Build pytest arguments
    args = [
        str(tests_dir),
        "-v" if verbose else "",
        "-k", test_pattern.replace("*.py", ""),
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ]
    
    # Remove empty arguments
    args = [arg for arg in args if arg]
    
    print(f"Running H3 tests with pattern: {test_pattern}")
    print(f"Tests directory: {tests_dir}")
    print(f"Source directory: {src_dir}")
    print(f"Python path: {sys.path[0]}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        # Run pytest
        result = pytest.main(args)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("-" * 80)
        print(f"Test execution completed in {duration:.2f} seconds")
        
        if result == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ {result} test(s) failed!")
        
        return result == 0
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False


def run_specific_test(test_file: str, verbose: bool = True):
    """
    Run a specific test file.
    
    Args:
        test_file: Name of the test file to run
        verbose: Whether to run tests in verbose mode
    """
    tests_dir = Path(__file__).parent
    test_path = tests_dir / test_file
    
    if not test_path.exists():
        print(f"❌ Test file not found: {test_path}")
        return False
    
    print(f"Running specific test: {test_file}")
    return run_tests(test_file, verbose)


def run_all_tests(verbose: bool = True):
    """
    Run all H3 module tests.
    
    Args:
        verbose: Whether to run tests in verbose mode
    """
    print("🧪 Running all H3 module tests...")
    print("=" * 80)
    
    # Test categories
    test_categories = [
        "test_h3_core.py",
        "test_h3_indexing.py", 
        "test_h3_traversal.py",
        "test_h3_hierarchy.py",
        "test_h3_unidirectional.py",
        "test_h3_validation.py",
        "test_h3_utilities.py",
        "test_h3_conversion.py",
        "test_h3_analysis.py"
    ]
    
    results = {}
    total_passed = 0
    total_failed = 0
    
    for test_file in test_categories:
        print(f"\n📋 Running {test_file}...")
        print("-" * 60)
        
        success = run_specific_test(test_file, verbose)
        results[test_file] = success
        
        if success:
            total_passed += 1
            print(f"✅ {test_file} passed")
        else:
            total_failed += 1
            print(f"❌ {test_file} failed")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    for test_file, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_file}")
    
    print(f"\nTotal: {len(test_categories)} test files")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {total_failed} test file(s) failed!")
        return False


def run_performance_tests():
    """
    Run performance tests for H3 operations.
    """
    print("⚡ Running H3 performance tests...")
    print("=" * 80)
    
    # Import performance test modules
    try:
        from h3.core import latlng_to_cell, cell_to_latlng
        import numpy as np
        import time
        
        # Performance test parameters
        num_operations = 100000
        resolution = 9
        
        print(f"Testing {num_operations:,} coordinate conversions...")
        
        # Generate test data
        lats = np.random.uniform(-90, 90, num_operations)
        lngs = np.random.uniform(-180, 180, num_operations)
        
        # Test latlng_to_cell performance
        start_time = time.time()
        cells = [latlng_to_cell(lat, lng, resolution) for lat, lng in zip(lats, lngs)]
        latlng_to_cell_time = time.time() - start_time
        
        # Test cell_to_latlng performance
        start_time = time.time()
        coordinates = [cell_to_latlng(cell) for cell in cells[:1000]]  # Test subset
        cell_to_latlng_time = time.time() - start_time
        
        # Calculate metrics
        latlng_to_cell_rate = num_operations / latlng_to_cell_time
        cell_to_latlng_rate = 1000 / cell_to_latlng_time
        
        print(f"✅ latlng_to_cell: {latlng_to_cell_rate:,.0f} ops/sec")
        print(f"✅ cell_to_latlng: {cell_to_latlng_rate:,.0f} ops/sec")
        print(f"✅ Total time: {latlng_to_cell_time + cell_to_latlng_time:.2f} seconds")
        
        # Performance thresholds
        min_latlng_rate = 10000  # 10k ops/sec
        min_cell_rate = 10000    # 10k ops/sec
        
        if latlng_to_cell_rate >= min_latlng_rate and cell_to_latlng_rate >= min_cell_rate:
            print("🎉 Performance tests passed!")
            return True
        else:
            print("⚠️  Performance below threshold!")
            return False
            
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def run_integration_tests():
    """
    Run integration tests for H3 modules.
    """
    print("🔗 Running H3 integration tests...")
    print("=" * 80)
    
    try:
        # Test module imports
        from h3 import (
            latlng_to_cell, cell_to_latlng, cell_to_boundary,
            grid_disk, grid_ring, cell_to_children, cell_to_parent,
            is_valid_cell, cell_area, cell_perimeter
        )
        
        print("✅ All H3 modules imported successfully")
        
        # Test basic workflow
        lat, lng = 37.7749, -122.4194
        resolution = 9
        
        # Create cell
        cell = latlng_to_cell(lat, lng, resolution)
        assert is_valid_cell(cell)
        
        # Get boundary
        boundary = cell_to_boundary(cell)
        assert len(boundary) >= 6
        
        # Get neighbors
        neighbors = grid_disk(cell, 1)
        assert len(neighbors) > 0
        
        # Get children
        children = cell_to_children(cell, resolution + 1)
        assert len(children) > 0
        
        # Get parent
        parent = cell_to_parent(cell, resolution - 1)
        assert is_valid_cell(parent)
        
        # Calculate properties
        area = cell_area(cell, 'km^2')
        perimeter = cell_perimeter(cell, 'km')
        assert area > 0 and perimeter > 0
        
        print("✅ Integration workflow completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """
    Main test runner function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="H3 Module Test Runner")
    parser.add_argument("--test", help="Run specific test file")
    parser.add_argument("--pattern", help="Run tests matching pattern")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--quiet", action="store_true", help="Run tests quietly")
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if args.test:
        success = run_specific_test(args.test, verbose)
    elif args.pattern:
        success = run_tests(args.pattern, verbose)
    elif args.performance:
        success = run_performance_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.all:
        success = run_all_tests(verbose)
    else:
        # Default: run all tests
        success = run_all_tests(verbose)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 