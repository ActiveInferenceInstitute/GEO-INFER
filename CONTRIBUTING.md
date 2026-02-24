# Contributing to GEO-INFER

Thank you for your interest in contributing to the GEO-INFER framework! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Contributions](#making-contributions)
- [Coding Standards](#coding-standards)
- [Documentation Standards](#documentation-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- uv (recommended) or pip for package management

### Repository Structure

```text
GEO-INFER/
├── GEO-INFER-ACT/       # Active Inference module
├── GEO-INFER-AGENT/     # Autonomous agents module
├── GEO-INFER-SPACE/     # Spatial methods module
├── GEO-INFER-TIME/      # Temporal analysis module
├── ... (44 total modules)
├── README.md            # Main documentation
├── AGENTS.md            # Agent architecture documentation
└── CONTRIBUTING.md      # This file
```

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ActiveInferenceInstitute/GEO-INFER.git
cd GEO-INFER
```

### 2. Create Virtual Environment

```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate

# Or using standard Python
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install a specific module in development mode
uv pip install -e ./GEO-INFER-ACT

# Or install multiple modules
uv pip install -e ./GEO-INFER-ACT -e ./GEO-INFER-AGENT -e ./GEO-INFER-SPACE
```

### 4. Run Tests

```bash
# Run tests for a specific module
pytest GEO-INFER-ACT/tests/

# Run all tests
pytest
```

## Making Contributions

### Types of Contributions

1. **Bug Fixes**: Fix issues in existing code
2. **New Features**: Add new functionality to modules
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Examples**: Add usage examples and tutorials

### Contribution Workflow

1. **Fork** the repository
2. **Create a branch** for your feature/fix: `git checkout -b feature/my-feature`
3. **Make changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit** with clear messages: `git commit -m "Add feature X to module Y"`
7. **Push** to your fork: `git push origin feature/my-feature`
8. **Create a Pull Request**

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints for function signatures
- Maximum line length: 88 characters (Black default)
- Use docstrings for all public functions and classes

### Example

```python
from typing import List, Optional
import numpy as np

def process_spatial_data(
    data: np.ndarray,
    resolution: int = 9,
    method: str = "h3"
) -> List[str]:
    """
    Process spatial data and return cell identifiers.

    Args:
        data: Input spatial coordinates as numpy array
        resolution: H3 resolution level (0-15)
        method: Indexing method to use

    Returns:
        List of cell identifiers

    Raises:
        ValueError: If resolution is out of valid range
    """
    if not 0 <= resolution <= 15:
        raise ValueError(f"Resolution must be 0-15, got {resolution}")
    
    # Implementation here
    return []
```

### Naming Conventions

- **Modules**: `geo_infer_<name>` (lowercase with underscores)
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`

## Documentation Standards

### README.md Files

Each module should have a README.md with:

1. **YAML Frontmatter**: Title, description, status, dependencies
2. **Overview**: Brief description of the module
3. **Installation**: How to install the module
4. **Usage**: Basic usage examples
5. **API Reference**: Key classes and functions
6. **Contributing**: Link to this document

### AGENTS.md Files

Each module should have an AGENTS.md describing:

1. **Agent Capabilities**: What agents can do with this module
2. **Implementation Status**: ✅ Implemented vs 🔮 Planned features
3. **Integration Patterns**: How to use with other modules
4. **Code Examples**: Working code snippets

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong

    Example:
        >>> function_name("test", 42)
        True
    """
```

## Testing Requirements

### Test Structure

```text
GEO-INFER-<MODULE>/
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_models.py
│   └── conftest.py  # Shared fixtures
```

### Writing Tests

```python
import pytest
from geo_infer_act import ActiveInferenceModel

class TestActiveInferenceModel:
    """Tests for ActiveInferenceModel class."""

    def test_initialization(self):
        """Test model initialization with default parameters."""
        model = ActiveInferenceModel()
        assert model is not None

    def test_perceive_updates_beliefs(self):
        """Test that perceive() updates internal beliefs."""
        model = ActiveInferenceModel()
        initial_beliefs = model.get_beliefs()
        model.perceive(observation=[0.5, 0.5])
        updated_beliefs = model.get_beliefs()
        assert not np.array_equal(initial_beliefs, updated_beliefs)
```

### Test Coverage

- Aim for 80%+ test coverage
- All public APIs must have tests
- Include both unit and integration tests

## Pull Request Process

### Before Submitting

1. Ensure all tests pass: `uv run python -m pytest`
2. Check code style: `ruff check .` and `black --check .`
3. Check types: `mypy GEO-INFER-MODULE/src/`
4. Update documentation if needed
5. Add yourself to CONTRIBUTORS.md (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test improvement

## Testing
Describe how you tested the changes

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

### Review Process

1. Maintainers will review within 1-2 weeks
2. Address any feedback in additional commits
3. Once approved, a maintainer will merge

## Module-Specific Guidelines

Some modules have additional contribution guidelines:

- **GEO-INFER-ACT**: See `GEO-INFER-ACT/docs/CONTRIBUTING_ACT.md`
- **GEO-INFER-SPACE**: See `GEO-INFER-SPACE/docs/CONTRIBUTING_SPACE.md`
- **GEO-INFER-PEP**: See `GEO-INFER-PEP/docs/CONTRIBUTING_PEP.md`

### Environmental Modules (Feb 2026 Renames)

The following modules were renamed from uppercase to lowercase package naming in Feb 2026:

- **GEO-INFER-FOREST** → `geo_infer_forest`
- **GEO-INFER-MARINE** → `geo_infer_marine`
- **GEO-INFER-ENERGY** → `geo_infer_energy`
- **GEO-INFER-WATER** → `geo_infer_water`

Ensure all imports use the new lowercase package names.

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Community**: Join the [Active Inference Institute](https://www.activeinference.institute/) community

## License

By contributing, you agree that your contributions will be licensed under the CC BY-NC-SA 4.0 license.

---

**Thank you for contributing to GEO-INFER!**

*Last Updated: 2026-02-24*
