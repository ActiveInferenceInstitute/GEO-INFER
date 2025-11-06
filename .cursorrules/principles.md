# Core Development Principles

## 1. NO MOCK METHODS - EVER

- Never create placeholder, stub, or mock methods
- Every function must be fully implemented with real logic
- Use proper error handling instead of `pass` or `NotImplementedError`
- If functionality is complex, break it into smaller, implementable pieces
- Implement real data analysis and processing pipelines

## 2. Maximum Intelligence & Documentation

- Write intelligent, thoughtful code that demonstrates deep understanding
- Include comprehensive docstrings for all functions, classes, and modules
- Use type hints for all function parameters and return values
- Document the mathematical/theoretical basis for algorithms
- Include example usage in docstrings
- Provide mathematical foundations and citations where applicable

## 3. Leverage Existing Module Structure

- Understand and work within the established module hierarchy
- Use the standardized directory structure: `src/`, `docs/`, `examples/`, `tests/`, `config/`
- Follow existing patterns for API design, data models, and utilities
- Import and extend existing functionality rather than reimplementing
- Respect module dependencies and data flow patterns

## 4. Active Inference First

- Ground all implementations in Active Inference mathematical principles
- Implement free energy minimization where applicable
- Use Bayesian inference for uncertainty quantification
- Design perception-action loops for autonomous systems
- Apply probabilistic reasoning to spatial-temporal problems

## 5. Concise Professional Communication

- Avoid unnecessary adjectives and descriptive hyperbole
- Use precise, understated language that shows rather than tells
- Prefer "comprehensive" over "comprehensive and sophisticated"
- Choose "robust" over "extremely robust and highly sophisticated"
- Eliminate redundant descriptors like "advanced", "sophisticated", "comprehensive" when not adding value
- Focus on functionality and capabilities rather than marketing language
- Use technical accuracy over promotional language

## 6. Documentation Standards Compliance

- Follow established documentation templates and standards
- Use YAML front matter for machine-readable metadata
- Maintain cross-linking between modules and documentation
- Include working code examples and integration patterns
- Update documentation simultaneously with code changes
- Use consistent terminology and formatting across all docs

