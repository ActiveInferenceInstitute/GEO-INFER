#!/usr/bin/env python
"""
Script to discover and run all GEO-INFER-ART tests.
"""

import os
import sys
import unittest


def run_all_tests():
    """Discover and run all tests in the tests directory."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add the src directory to the path so modules can be imported
    project_dir = os.path.dirname(tests_dir)
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    # Discover all tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_all_tests()) 