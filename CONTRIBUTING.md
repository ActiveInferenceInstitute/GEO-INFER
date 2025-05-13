# Contributing to GEO-INFER

Thank you for your interest in contributing to the GEO-INFER framework! This document provides guidelines and instructions for contributing.

## Code of Conduct

All contributors are expected to adhere to our Code of Conduct. Please be respectful and considerate in all interactions.

## Development Process

We follow a collaborative development process:

1. **Issues**: Browse existing issues or create a new one to discuss proposed changes before starting work.
2. **Branches**: Create a feature branch for your contribution, branched from `main`.
3. **Commits**: Make focused, logical commits with clear messages following the conventional commit format.
4. **Pull Requests**: Submit a PR with a clear description of the changes and reference to related issues.
5. **Review**: Respond to feedback during code review and make necessary adjustments.
6. **Integration**: Once approved, your changes will be merged into the main branch.

## Branch Naming Convention

Follow this format for branch names:
- `feature/{description}` - For new features
- `fix/{description}` - For bug fixes
- `docs/{description}` - For documentation changes
- `refactor/{description}` - For code refactoring
- `test/{description}` - For testing related changes

For geospatial-specific contributions, consider adding scope details:
- `feature/vector/{description}` - For vector data features
- `feature/raster/{description}` - For raster data features
- `feature/h3/{description}` - For H3 indexing features

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Example:
```
feat(space): add H3 spatial indexing support

Implement H3 hexagonal grid system for multi-resolution spatial indexing.
This enables more efficient proximity searches and spatial aggregations.

Resolves #123
```

Use module prefixes in the scope to indicate which GEO-INFER module is affected:
- `feat(space): ...` - For GEO-INFER-SPACE module changes
- `fix(time): ...` - For GEO-INFER-TIME module fixes
- `docs(api): ...` - For GEO-INFER-API documentation

## Pull Request Process

1. Ensure your code follows the project's coding standards
2. Update documentation as needed
3. Add or update tests to cover your changes
4. Make sure all tests pass
5. Get at least one code review approval
6. For changes to geospatial functionality, include visual examples where appropriate

## Coding Standards

- Follow [PEP 8](https://pep8.org/) for Python code
- Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Add type hints to function signatures
- Keep functions focused and small
- Write unit tests for new features

### Geospatial-Specific Standards

- Use standard coordinate ordering: [latitude, longitude] in variables and documentation
- Follow `dataset_naming: "{source}_{parameter}_{timeframe}_{region}_{resolution}"` convention for dataset names
- Include coordinate system information in all spatial function docstrings
- Add proper validation for coordinate bounds (-90 to 90 latitude, -180 to 180 longitude)
- Handle edge cases like date line crossing and polar regions properly

### Active Inference Principles

For contributions to active inference components:
- Follow established free energy principle terminology
- Document precision weighting and belief updating mechanisms
- Maintain consistency with Markov blanket formalisms
- Include references to relevant active inference literature

## Documentation Requirements

All contributions should include proper documentation:

1. **Code Documentation**
   - Module docstrings explaining purpose and usage
   - Class and function docstrings with parameters, return values, and examples
   - Type hints for all function parameters and return values

2. **User Documentation**
   - Updates to module README files for feature changes
   - Example notebooks demonstrating new features
   - Diagrams illustrating complex workflows (using Mermaid or PlantUML)

3. **Geospatial Visualization**
   - Include map visualizations for spatial algorithms
   - Document coordinate systems and projections used
   - Provide example datasets for testing

## Module-Specific Guidelines

Each module may have additional contribution guidelines. See the module's own CONTRIBUTING.md file for details.

## Setting Up Development Environment

1. Fork and clone the repository
2. Create a virtual environment
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
4. Run tests to ensure everything is working:
   ```bash
   pytest
   ```

## Geospatial Data Handling

When contributing code that processes geospatial data:

1. **Performance Considerations**
   - Use appropriate spatial indexing for large datasets
   - Implement progressive loading for large raster data
   - Consider level-of-detail approaches for visualization

2. **Data Validation**
   - Validate coordinate systems and projections
   - Check topology validity for vector data
   - Ensure resolution consistency across datasets

3. **Interoperability**
   - Follow OGC standards where applicable
   - Support common geospatial file formats
   - Maintain STAC compatibility for Earth observation data

## Getting Help

If you need help or have questions:
- Open an issue on GitHub
- Join our community [Discord/Slack] channel
- Email the maintainers at [contact@geo-infer.org]

Thank you for contributing to GEO-INFER! 