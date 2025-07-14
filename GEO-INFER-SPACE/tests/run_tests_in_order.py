#!/usr/bin/env python3
"""
Test runner script for GEO-INFER-SPACE with logical execution order.

This script runs tests in the following logical order:
1. Setup tests (repository setup and configuration)
2. Core tests (base modules and backend functionality)  
3. Spatial tests (data processing and spatial operations)
4. Reporting tests (visualization and reporting)

Usage:
    python run_tests_in_order.py [--category setup|core|spatial|reporting|all]
"""

import sys
import subprocess
import argparse
from pathlib import Path

def run_test_category(category, verbose=False):
    """Run tests for a specific category."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {category.upper()} Tests")
    print(f"{'='*60}")
    
    cmd = [
        "python", "-m", "pytest", 
        f"-m", category,
        "--tb=short",
        "--durations=10"
    ]
    
    if verbose:
        cmd.append("-v")
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {category} tests: {e}")
        return False

def run_all_tests(verbose=False):
    """Run all tests (no marker filter)."""
    print("🚀 GEO-INFER-SPACE Test Suite (ALL TESTS)")
    print("="*60)
    cmd = [
        "python", "-m", "pytest", "-v" if verbose else None, "--tb=short", "--durations=10"
    ]
    cmd = [c for c in cmd if c]
    print(f"Command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, check=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running all tests: {e}")
        return False

def run_all_tests_in_order(verbose=False):
    """Run all tests in logical order by category (deprecated, use run_all_tests)."""
    categories = ["setup", "core", "spatial", "reporting"]
    print("🚀 GEO-INFER-SPACE Test Suite")
    print("="*60)
    print("📋 Test Execution Order:")
    for i, category in enumerate(categories, 1):
        print(f"  {i}. {category.upper()} - {get_category_description(category)}")
    print()
    results = {}
    for category in categories:
        success = run_test_category(category, verbose)
        results[category] = success
        if not success:
            print(f"❌ {category.upper()} tests failed - stopping execution")
            break
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print(f"{'='*60}")
    all_passed = True
    for category, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {category.upper()}: {status}")
        if not success:
            all_passed = False
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    return all_passed

def get_category_description(category):
    """Get description for test category."""
    descriptions = {
        "setup": "Repository setup, OSC integration, and H3 utilities",
        "core": "Base modules, unified backend, and core functionality", 
        "spatial": "Data integration, spatial processing, and place analysis",
        "reporting": "Enhanced reporting, visualization, and dashboard generation"
    }
    return descriptions.get(category, "Unknown category")

def main():
    parser = argparse.ArgumentParser(description="Run GEO-INFER-SPACE tests in logical order")
    parser.add_argument("--category", choices=["setup", "core", "spatial", "reporting", "all"], 
                       default="all", help="Test category to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    if args.category == "all":
        success = run_all_tests(args.verbose)
    else:
        success = run_test_category(args.category, args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 