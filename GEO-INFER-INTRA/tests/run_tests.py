#!/usr/bin/env python
"""
Test runner for the GEO-INFER framework.

This script provides a command-line interface for running tests across all modules.
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the GEO-INFER framework")
    
    # Test selection
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--system", action="store_true", help="Run system tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    
    # Module selection
    parser.add_argument("--modules", nargs="*", help="Specific modules to test (e.g., space time data)")
    
    # Test filtering
    parser.add_argument("--keyword", "-k", help="Only run tests which match the given substring expression")
    parser.add_argument("--marker", "-m", help="Only run tests matching the given marker expression")
    
    # Test output
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Increase verbosity")
    parser.add_argument("--quiet", "-q", action="store_true", help="Decrease verbosity")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML coverage report")
    
    # Other options
    parser.add_argument("--skip-slow", action="store_true", help="Skip slow tests")
    parser.add_argument("--jobs", "-j", type=int, default=1, help="Number of parallel test processes")
    
    return parser.parse_args()

def build_pytest_command(args: argparse.Namespace) -> List[str]:
    """Build pytest command from arguments."""
    cmd = ["python3", "-m", "pytest"]
    
    # Test selection
    test_types = []
    if args.unit:
        test_types.append("unit")
    if args.integration:
        test_types.append("integration")
    if args.system:
        test_types.append("system")
    if args.performance:
        test_types.append("performance")
    
    # Set test directories
    if test_types:
        cmd.extend([f"tests/{test_type}" for test_type in test_types])
    else:
        cmd.append("tests")
    
    # Verbosity
    if args.verbose > 0:
        cmd.extend(["-" + "v" * args.verbose])
    if args.quiet:
        cmd.append("-q")
    
    # Filtering
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    marker_expr = []
    if args.marker:
        marker_expr.append(args.marker)
    if args.skip_slow:
        marker_expr.append("not slow")
    
    if marker_expr:
        cmd.extend(["-m", " and ".join(marker_expr)])
    
    # Coverage
    if not args.no_coverage:
        cmd.append("--cov=.")
        
        if args.modules:
            # Limit coverage to specific modules
            module_paths = [f"GEO-INFER-{module.upper()}" for module in args.modules]
            cmd.extend([f"--cov={path}" for path in module_paths])
        
        cmd.append("--cov-report=term")
        
        if args.html_report:
            cmd.append("--cov-report=html:.test-results/coverage")
    
    # Parallel
    if args.jobs > 1:
        cmd.extend(["-n", str(args.jobs)])
    
    return cmd

def run_tests(cmd: List[str]) -> int:
    """Run tests with the given command."""
    print(f"Running: {' '.join(cmd)}")
    
    # Set environment variables for testing
    env = os.environ.copy()
    env["GEO_INFER_ENV"] = "test"
    env["GEO_INFER_DEBUG"] = "true"
    
    # Run the tests
    start_time = time.time()
    result = subprocess.run(cmd, env=env)
    end_time = time.time()
    
    # Print summary
    duration = end_time - start_time
    print(f"\nTest run completed in {duration:.2f} seconds")
    print(f"Return code: {result.returncode}")
    
    return result.returncode

def main() -> int:
    """Main entry point."""
    # Add the parent directory to Python path for module imports
    parent_dir = str(Path(__file__).parent.parent)
    sys.path.insert(0, parent_dir)
    
    args = parse_args()
    cmd = build_pytest_command(args)
    return run_tests(cmd)

if __name__ == "__main__":
    sys.exit(main()) 