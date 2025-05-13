# Contributing to GEO-INFER

Thank you for your interest in contributing to the GEO-INFER framework! This guide provides detailed instructions on how to contribute effectively to the project while maintaining our high standards for code quality, documentation, and testing.

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](../code_of_conduct.md). By participating, you are expected to uphold this code.

## Getting Started

### Set Up Your Development Environment

1. **Fork the Repository**: 
   - Visit the GEO-INFER repository on GitHub and click "Fork" in the upper right corner.

2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/geo-infer.git
   cd geo-infer
   ```

3. **Add the Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/geo-infer/geo-infer.git
   ```

4. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install Development Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

6. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

## Workflow

### Branch Naming Convention

All branches should follow the pattern `{type}/{description}` where:

- `{type}` is one of:
  - `feat`: New feature
  - `fix`: Bug fix
  - `docs`: Documentation only changes
  - `style`: Changes that do not affect the meaning of the code
  - `refactor`: Code change that neither fixes a bug nor adds a feature
  - `perf`: Code change that improves performance
  - `test`: Adding missing tests or correcting existing tests
  - `build`: Changes that affect the build system or external dependencies
  - `ci`: Changes to CI configuration files and scripts
  - `chore`: Other changes that don't modify src or test files

- `{description}` is a brief, hyphenated description of the change:
  - Use lowercase letters
  - Use hyphens as separators
  - Be concise but descriptive

Examples:
- `feat/h3-spatial-index`
- `fix/coordinate-bounds-validation`
- `docs/improve-installation-guide`

### Development Workflow

1. **Sync with Upstream**:
   ```bash
   git checkout main
   git pull upstream main
   git push origin main
   ```

2. **Create a Feature Branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make Your Changes**:
   - Follow the coding standards
   - Write tests for your changes
   - Update documentation as needed

4. **Commit Your Changes**:
   - Use the conventional commits format:
   ```
   type(scope): short description
   
   Longer explanation if necessary
   
   Refs #123
   ```
   - Example: `feat(space): add H3 spatial indexing`

5. **Push to Your Fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

6. **Create a Pull Request**:
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Select the appropriate branches
   - Fill out the PR template

## Coding Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting with line length 88
- Use Google-style docstrings
- Sort imports according to the standard:
  - Standard library imports
  - Third-party imports
  - First-party imports
  - Local imports

Example:
```python
"""Module docstring with a brief description.

More detailed description if needed.
"""

import os
import sys
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import geopandas as gpd

from geo_infer.core import utils
from geo_infer.space import indexing

from .local_module import local_function


def function_name(param1: type, param2: Optional[type] = None) -> return_type:
    """Short description of function.
    
    More detailed description if needed.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter. Default is None.
        
    Returns:
        Description of the return value
        
    Raises:
        ExceptionType: When and why this exception might be raised
        
    Examples:
        >>> function_name(1, "test")
        Expected output
    """
    # Implementation
    return result
```

### Type Hints

- Use type hints for all function parameters and return values
- Use the typing module for complex types
- For geospatial types, use clearly defined types that document the coordinate system expectations

Example:
```python
from typing import List, Tuple, Union
from shapely.geometry import Point, Polygon

def buffer_points(
    points: List[Tuple[float, float]], 
    distance: float, 
    crs: str = "EPSG:4326"
) -> List[Polygon]:
    """Buffer points to create polygons."""
    # Implementation
```

### Geospatial Conventions

- Always specify coordinate reference systems in function signatures
- Prefer the order (latitude, longitude) in documentation and variable names
- Use consistent units and document them (meters, degrees, etc.)
- Handle edge cases like the antimeridian and polar regions

## Testing

### Test Requirements

- Maintain at least 95% code coverage
- Write tests for all new features and bug fixes
- Test edge cases and error conditions

### Test Organization

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Place performance tests in `tests/performance/`
- Geospatial test data should be stored in `tests/data/geospatial/`

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=geo_infer

# Run specific test category
pytest tests/unit/

# Run tests matching a pattern
pytest -k "spatial"
```

### Geospatial Testing

- Mock coordinate systems where appropriate
- Use small, representative datasets for testing
- Test with real-world geospatial data for edge cases
- Verify results with known geospatial libraries

## Documentation

### Requirements

All contributions should include appropriate documentation:

- **Code Documentation**: Docstrings for all public classes, methods, and functions
- **Module Documentation**: Module-level docstrings explaining purpose and usage
- **Examples**: Code examples for non-trivial functionality
- **API Documentation**: Updates to API reference if public interfaces change
- **Tutorials**: Consider adding or updating tutorials for significant features

### Standards

- Follow the [GEO-INFER Documentation Guide](../documentation_guide.md)
- Use Markdown for all documentation files
- Use Mermaid for diagrams
- Include links to related documentation

## Pull Request Process

1. **Create a Pull Request**:
   - Ensure your PR has a descriptive title following the conventional commits format
   - Fill out the PR template completely
   - Link to any related issues

2. **CI Checks**:
   - Ensure all CI checks pass
   - Address any linting, formatting, or test failures

3. **Code Review**:
   - Address reviewer comments and suggestions
   - Keep the PR focused on a single change or feature

4. **Approval and Merge**:
   - Once approved, a maintainer will merge your PR
   - In some cases, you may be asked to rebase before merging

## Release Process

Our release process follows semantic versioning:

- **Major Releases (X.0.0)**: Breaking changes
- **Minor Releases (0.X.0)**: New features, non-breaking
- **Patch Releases (0.0.X)**: Bug fixes, non-breaking

Contributors don't need to manage releases, but should be aware of how changes impact versioning.

## Common Tasks

### Adding a New Module

1. Use the module template:
   ```bash
   python -m geo_infer.tools.create_module --name new_module_name
   ```

2. Follow the structure in the template
3. Update cross-module references

### Adding Geospatial Algorithms

1. Place implementation in the appropriate module
2. Include detailed docstrings with:
   - Mathematical basis
   - Coordinate system handling
   - Performance characteristics
   - Edge case behavior

3. Provide visualization examples where appropriate

### Updating Dependencies

1. Update `setup.py` and `requirements.txt`
2. Document the change and rationale
3. Test with the new dependency versions

## Getting Help

- **Developer Chat**: Join our [Slack channel](https://geo-infer-community.slack.com)
- **Mailing List**: Subscribe to our [development mailing list](https://lists.geo-infer.org/dev)
- **Office Hours**: Join our biweekly developer office hours

## Special Cases

### Large Data Contributions

For contributions that include large datasets:

1. Contact the maintainers first
2. Provide samples rather than full datasets in the PR
3. Include data processing scripts if applicable

### Experimental Features

For experimental or research-oriented features:

1. Use the `experimental/` namespace
2. Clearly document the experimental status
3. Provide research references and validation

## Acknowledgments

By contributing to GEO-INFER, you agree that your contributions will be licensed under the project's license. All contributors will be acknowledged in our documentation.

Thank you for your contributions to making GEO-INFER better! 