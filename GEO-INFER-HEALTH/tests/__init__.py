# Tests for GEO-INFER-HEALTH module

import pytest
import sys
from pathlib import Path

# Add the src directory to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import test utilities
# Note: conftest.py contains pytest fixtures, not regular imports
# Fixtures are automatically available to test files via pytest
# No explicit imports needed here

__all__ = [
    "pytest",
    "test_utils",
    "sample_data",
]