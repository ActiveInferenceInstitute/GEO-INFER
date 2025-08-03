#!/usr/bin/env python3
"""
H3 Comprehensive Test Suite

Provides 100% coverage testing for all H3 geospatial operations.
Includes unit tests, integration tests, performance tests, and visual outputs.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .test_runner import H3TestRunner
from .coverage_analyzer import H3CoverageAnalyzer
from .visual_test_generator import H3VisualTestGenerator
from .interactive_test_generator import H3InteractiveTestGenerator

__version__ = "4.3.0"
__author__ = "GEO-INFER Framework"
__license__ = "Apache-2.0"

# Export main test classes
__all__ = [
    'H3TestRunner',
    'H3CoverageAnalyzer', 
    'H3VisualTestGenerator',
    'H3InteractiveTestGenerator'
] 