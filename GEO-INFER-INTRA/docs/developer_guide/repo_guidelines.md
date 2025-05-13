# GEO-INFER Repository Guidelines

## Overview

This document provides comprehensive guidelines for working with the GEO-INFER repository structure, ensuring consistency across modules and enabling autonomous agent coders to work effectively both individually and collaboratively.

## Repository Organization

The GEO-INFER project follows a multi-module, domain-driven design approach where each domain-specific capability is encapsulated in a dedicated module. The repository is organized as follows:

```
INFER-GEO/                      # Root repository
├── .github/                    # GitHub workflows and templates
├── docs/                       # Project-wide documentation
├── tools/                      # Development and utility tools
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # Project license
├── GEO-INFER-[MODULE1]/        # Domain-specific module
├── GEO-INFER-[MODULE2]/        # Domain-specific module
└── ...                         # Additional modules
```

### Module Independence

Each module is designed to be independently versioned, tested, and deployed. Modules should minimize dependencies on other modules, communicating through well-defined interfaces. This allows for:

1. Parallel development across modules
2. Independent release cycles
3. Selective deployment of capabilities
4. Improved maintainability and testing

## Cross-Module Development Guidelines

When working across multiple modules, adhere to these guidelines:

### 1. No Root-Level Source Code

Source code must never be placed at the repository root level. All code must be contained within the appropriate module structure:

```python
# INCORRECT - Code at root level
/INFER-GEO/my_script.py

# CORRECT - Code within module
/INFER-GEO/GEO-INFER-MODULE/src/geo_infer_module/utils/my_script.py
```

### 2. Module Interaction Patterns

When modules need to interact, use these approaches in order of preference:

1. **API-based interaction**: Use public, stable API endpoints
   ```python
   from geo_infer_space import calculate_spatial_index
   result = calculate_spatial_index(coordinates)
   ```

2. **Event-based communication**: Use message passing for loose coupling
   ```python
   from geo_infer_ops.core.events import publish_event
   publish_event("spatial_data_updated", {"region_id": "R123"})
   ```

3. **Shared data formats**: Use common data schemas
   ```python
   from geo_infer_data.models import GeoDataFrame
   data = GeoDataFrame.from_file("example.geojson")
   ```

### 3. Cross-Module Dependencies

When one module depends on another:

- Declare explicit dependencies in `requirements.txt` with version constraints
- Minimize dependency depth (avoid chains of dependencies)
- Consider using interfaces for stronger decoupling

```
# Example requirements.txt with module dependencies
geo-infer-space>=1.0.0,<2.0.0
geo-infer-time>=0.5.0,<1.0.0
```

## Version Control Practices

### Branching Strategy

GEO-INFER uses a trunk-based development approach with feature branches:

1. `main` - Primary development branch, always in a deployable state
2. `feature/*` - Feature development (e.g., `feature/spatial-indexing`)
3. `fix/*` - Bug fixes (e.g., `fix/coordinate-transformation`)
4. `release/*` - Release preparation (e.g., `release/1.2.0`)

### Commit Conventions

Use conventional commits for clear history and automated tooling:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code changes that neither fix bugs nor add features
- perf: Performance improvements
- test: Adding or correcting tests
- build: Changes to build process or tools
- ci: Changes to CI configuration
- chore: Other changes that don't modify src or test files

Example:
```
feat(spatial-index): add hexagonal grid indexing system

This adds H3 spatial indexing capabilities to improve performance
for large-scale spatial queries.

Closes #123
```

## Continuous Integration and Delivery

All modules should include:

1. **Unit tests**: Test individual components
2. **Integration tests**: Test interactions between components
3. **Style checks**: Enforce code style standards
4. **Type checks**: Verify type annotations
5. **Documentation generation**: Auto-generate API docs

CI/CD workflows are defined in `.github/workflows/`:
- Build and test on pull requests
- Version and release on merges to main
- Documentation updates
- Container image builds

## Documentation Standards

Documentation should be comprehensive and follow these guidelines:

### Module-Level Documentation

Each module must include:
1. **README.md**: Overview, features, getting started
2. **API Reference**: Complete API documentation
3. **Examples**: Practical use cases
4. **Architecture**: Module design and patterns

### Repository-Level Documentation

Repository-level documentation includes:
1. **Project Overview**: Purpose and vision
2. **Module Catalog**: List of all modules with descriptions
3. **Integration Guide**: How modules work together
4. **Contribution Guidelines**: How to contribute
5. **Development Setup**: Environment setup instructions

## Working with Autonomous Agent Coders

### Agent Coordination

Autonomous agents should follow these practices:

1. **Task Segregation**: Work on separate modules or components when possible
2. **Clear Interfaces**: Define interfaces before implementation
3. **Documentation First**: Update docs to reflect intended changes before code
4. **Incremental Changes**: Make smaller, focused changes rather than large rewrites
5. **Review Handoffs**: Document the state when handing off between agents

### Standardized Comments

Use standardized comments to communicate intent and state:

```python
# TODO(agent): Description of what needs to be done
# FIXME(agent): Something that needs fixing
# REVIEW(agent): Request another agent to review this section
# OPTIMIZE(agent): Performance could be improved here
# HANDOFF(agent): Work continued by another agent from this point
```

### Error Handling Standards

Follow consistent error handling patterns:

```python
try:
    # Operation that might fail
    result = perform_operation()
except SpecificError as e:
    # Log with context
    logger.error("Operation failed: %s", str(e), extra={"context": context})
    # Raise with additional context if needed
    raise EnhancedError("Failed to process data") from e
```

## Cross-Domain Knowledge Integration

To maintain consistency across domains:

1. **Ontology Alignment**: Use defined terms from GEO-INFER-INTRA's ontology
2. **Consistent Terminology**: Follow naming conventions for domain concepts
3. **Shared Models**: Leverage common models for cross-domain concepts
4. **Knowledge Transfer**: Document domain insights in the knowledge base

## Performance Considerations

All modules should consider:

1. **Resource Efficiency**: Optimize for memory and CPU usage
2. **Scalability**: Design for horizontal scaling
3. **Asynchronous Patterns**: Use async/await for I/O-bound operations
4. **Caching Strategies**: Implement appropriate caching
5. **Profiling**: Include performance measurement in tests

## Security Standards

Follow these security practices:

1. **Input Validation**: Validate all inputs, especially from external sources
2. **Output Encoding**: Properly encode outputs to prevent injection attacks
3. **Authentication**: Use GEO-INFER-OPS authentication mechanisms
4. **Authorization**: Implement proper permission checks
5. **Secrets Management**: Never hardcode secrets; use GEO-INFER-OPS for secret management
6. **Dependency Security**: Regularly update and scan dependencies

## Monitoring and Observability

Ensure code includes:

1. **Structured Logging**: Use the GEO-INFER-OPS logging framework
   ```python
   from geo_infer_ops.core.logging import get_logger
   logger = get_logger(__name__)
   logger.info("Processing data", extra={"data_size": len(data)})
   ```

2. **Metrics Collection**: Track performance and usage metrics
   ```python
   from geo_infer_ops.core.monitoring import metrics
   metrics.increment("data_processing_count")
   metrics.timing("processing_time", processing_time)
   ```

3. **Tracing**: Implement distributed tracing for operations spanning multiple modules
   ```python
   from geo_infer_ops.core.tracing import trace
   
   @trace("process_spatial_data")
   def process_spatial_data(data):
       # Function implementation
   ```

## Conclusion

By following these repository guidelines, autonomous agent coders can effectively work within the GEO-INFER framework, maintaining consistency and quality across the project. These guidelines ensure that modules remain interoperable while allowing for independent development and innovation within each domain. 