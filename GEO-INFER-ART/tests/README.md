# GEO-INFER-ART Tests

This directory contains the test suite for the GEO-INFER-ART module.

## Running Tests

### Run All Tests

To run all tests in the test suite:

```bash
cd GEO-INFER-ART
python -m tests.run_all_tests
```

### Run Individual Test Modules

To run a specific test module:

```bash
cd GEO-INFER-ART
python -m tests.unit.test_geo_art
python -m tests.unit.test_color_palette
# etc.
```

### Run Tests with Coverage

To run tests with coverage reporting:

```bash
cd GEO-INFER-ART
pytest --cov=geo_infer_art tests/
```

## Test Structure

- `unit/`: Unit tests for individual components
  - `test_geo_art.py`: Tests for the GeoArt class
  - `test_color_palette.py`: Tests for the ColorPalette class
  - `test_style_transfer.py`: Tests for the StyleTransfer class
  - `test_generative_map.py`: Tests for the GenerativeMap class
  - `test_procedural_art.py`: Tests for the ProceduralArt class
  - `test_place_art.py`: Tests for the PlaceArt class
  - `test_cultural_map.py`: Tests for the CulturalMap class

## Adding New Tests

When adding a new component to the GEO-INFER-ART module, please create a corresponding test file in the appropriate directory.

### Test File Template

```python
#!/usr/bin/env python
"""
Unit tests for the [Component] class in geo_infer_art.[module_path].
"""

import os
import unittest
# Import other required modules

from geo_infer_art.[module_path] import [Component]


class Test[Component](unittest.TestCase):
    """Test suite for the [Component] class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Set up any test fixtures
        
    def tearDown(self):
        """Clean up after tests."""
        # Clean up test fixtures
    
    def test_something(self):
        """Test description."""
        # Test code
        self.assertTrue(True)  # Assertions


if __name__ == "__main__":
    unittest.main()
```

## Test Best Practices

1. **Comprehensive Coverage**: Aim for at least 80% code coverage.
2. **Isolated Tests**: Each test should be independent and not rely on the state from other tests.
3. **Test Edge Cases**: Test boundary conditions and error handling.
4. **Mock External Services**: Use `unittest.mock` to mock external services.
5. **Clear Test Names**: Use descriptive test names that explain what is being tested.
6. **Clean Teardown**: Ensure tests clean up after themselves in `tearDown()`. 