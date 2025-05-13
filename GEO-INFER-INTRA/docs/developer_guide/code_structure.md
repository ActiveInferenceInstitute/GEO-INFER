# Code Structure

This document describes the organization and structure of the GEO-INFER-INTRA codebase to help developers understand and contribute to the project.

## Repository Structure

The GEO-INFER-INTRA repository is organized as follows:

```
GEO-INFER-INTRA/
├── config/                  # Configuration files
│   ├── example.yaml         # Example configuration
│   └── schema.json          # Configuration schema
├── docs/                    # Documentation
├── examples/                # Example code and usage
├── src/                     # Source code
│   └── geo_infer_intra/     # Main package
│       ├── __init__.py      # Package initialization
│       ├── api/             # API definitions
│       ├── core/            # Core functionality
│       ├── models/          # Data models
│       └── utils/           # Utility functions
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── performance/         # Performance tests
├── setup.py                 # Package setup
├── requirements.txt         # Dependencies
└── README.md                # Project README
```

## Main Package Structure

The `geo_infer_intra` package is organized into several modules:

### API Module (`geo_infer_intra.api`)

The API module provides interfaces for programmatic access to GEO-INFER-INTRA functionality:

```
api/
├── __init__.py                # API package initialization
├── auth.py                    # Authentication and authorization
├── documentation.py           # Documentation API
├── knowledge_base.py          # Knowledge Base API
├── ontology.py                # Ontology management API
├── routes.py                  # API route definitions
├── schemas.py                 # API request/response schemas
└── workflow.py                # Workflow management API
```

### Core Module (`geo_infer_intra.core`)

The Core module contains the essential functionality of GEO-INFER-INTRA:

```
core/
├── __init__.py                # Core package initialization
├── documentation/             # Documentation system
│   ├── __init__.py            # Documentation package initialization
│   ├── generators.py          # Documentation generators
│   ├── parsers.py             # Document parsers
│   └── server.py              # Documentation server
├── knowledge_base/            # Knowledge Base system
│   ├── __init__.py            # Knowledge Base package initialization
│   ├── indexing.py            # Content indexing
│   ├── search.py              # Search functionality
│   └── storage.py             # Content storage
├── ontology/                  # Ontology management
│   ├── __init__.py            # Ontology package initialization
│   ├── converters.py          # Format converters
│   ├── manager.py             # Ontology manager
│   └── validators.py          # Ontology validators
└── workflow/                  # Workflow system
    ├── __init__.py            # Workflow package initialization
    ├── engine.py              # Workflow execution engine
    ├── nodes.py               # Workflow node definitions
    └── validators.py          # Workflow validators
```

### Models Module (`geo_infer_intra.models`)

The Models module defines data models used throughout the system:

```
models/
├── __init__.py                # Models package initialization
├── document.py                # Document models
├── knowledge_item.py          # Knowledge item models
├── ontology.py                # Ontology models
└── workflow.py                # Workflow models
```

### Utils Module (`geo_infer_intra.utils`)

The Utils module provides utility functions used by other modules:

```
utils/
├── __init__.py                # Utils package initialization
├── config.py                  # Configuration utilities
├── logging.py                 # Logging utilities
├── serialization.py           # Serialization utilities
└── validation.py              # Validation utilities
```

## Code Style and Conventions

GEO-INFER-INTRA follows these coding conventions:

1. **Python Style Guide**: PEP 8 with Black formatting
2. **Docstrings**: Google-style docstrings
3. **Type Hints**: All functions include type hints
4. **Error Handling**: Exceptions are properly documented and handled
5. **Logging**: Consistent logging using the logging module
6. **Configuration**: Configuration via YAML files with JSON Schema validation
7. **Testing**: All code is tested with pytest

## Dependencies

GEO-INFER-INTRA has the following key dependencies:

- **FastAPI**: Web framework for building APIs
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: SQL toolkit and ORM
- **Elasticsearch**: Full-text search engine
- **RDFLib**: RDF parsing and serialization
- **MkDocs**: Documentation generation
- **Celery**: Distributed task queue for workflow execution

## Development Workflow

When developing for GEO-INFER-INTRA:

1. Create or branch from the appropriate feature branch
2. Make changes following the code style guidelines
3. Add tests for new functionality
4. Update documentation as needed
5. Run the test suite
6. Submit a pull request for review

## Resources

- [Architecture Overview](../architecture/overview.md) - Overall system architecture
- [API Development Guide](api_development.md) - Guide for developing APIs
- [Testing Guidelines](testing.md) - Guide for writing tests
- [Documentation Guidelines](documentation_guidelines.md) - Guide for documenting code 