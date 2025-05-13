# Developer Guide

This guide is intended for developers who want to contribute to or extend GEO-INFER-INTRA.

## Contents

- [Architecture Overview](architecture_overview.md)
- [Code Structure](code_structure.md)
- [Development Environment Setup](environment_setup.md)
- [Contributing Guidelines](contributing.md)
- [API Development](api_development.md)
- [Testing Guidelines](testing.md)
- [Documentation Guidelines](documentation_guidelines.md)
- [Release Process](release_process.md)

## Development Workflow

GEO-INFER-INTRA follows a standard git-based development workflow:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write or update tests
5. Update documentation
6. Submit a pull request

See [Contributing Guidelines](contributing.md) for more detailed information.

## Code Standards

GEO-INFER-INTRA follows the coding standards defined in the `.cursorrules` file at the root of the project. Key points include:

- Python code follows PEP 8 style guide with Black formatting
- Documentation uses Google-style docstrings
- Testing follows pytest-based testing patterns
- Line length is limited to 88 characters

See [Code Structure](code_structure.md) for more details on how the codebase is organized. 