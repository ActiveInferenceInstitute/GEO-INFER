# Module Structure Standards

Every module follows this standardized structure:

```
GEO-INFER-MODULE/
├── config/               # Configuration files (YAML/JSON)
│   ├── example.yaml      # Example configuration
│   └── schema.json       # Configuration schema
├── docs/                 # Documentation (markdown, API specs)
│   ├── api_schema.yaml   # API documentation
│   ├── architecture.md   # Module architecture
│   └── tutorials/        # Step-by-step tutorials
├── examples/             # Working examples and demonstrations
│   ├── basic_example.py  # Basic usage examples
│   └── advanced_example.py # Advanced workflows
├── src/                  # Source code
│   └── geo_infer_module/ # Main package
│       ├── __init__.py   # Package initialization
│       ├── api/          # API definitions and routes
│       │   ├── __init__.py
│       │   ├── rest_api.py
│       │   └── schemas.py
│       ├── core/         # Core functionality and algorithms
│       │   ├── __init__.py
│       │   ├── main_engine.py
│       │   └── algorithms.py
│       ├── models/       # Data models and schemas
│       │   ├── __init__.py
│       │   └── data_models.py
│       └── utils/        # Utility functions and helpers
│           ├── __init__.py
│           ├── helpers.py
│           └── validation.py
├── tests/                # Comprehensive test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── performance/      # Performance tests
├── setup.py              # Package setup
├── requirements.txt      # Dependencies
└── README.md             # Module documentation
```

## README Structure

All module READMEs must include:
- YAML front matter with metadata
- Overview section
- **Core Features** (not "Key Features")
- **API Reference** section with core classes
- Integration with other modules
- Getting started guide
- Examples
- Troubleshooting

## Module Categories

- **🧠 Analytical Core**: ACT, BAYES, AI, MATH, COG, AGENT, SPM
- **🗺️ Spatial-Temporal**: SPACE, TIME, IOT
- **💾 Data Management**: DATA, API
- **🔒 Security & Governance**: SEC, NORMS, REQ, METAGOV
- **🧪 Simulation & Modeling**: SIM, ANT
- **👥 People & Community**: CIV, PEP, ORG, COMMS
- **🖥️ Applications**: APP, ART
- **🏢 Domain-Specific**: AG, ECON, RISK, LOG, BIO, HEALTH
- **📍 Place-Based**: PLACE
- **⚙️ Operations**: OPS, INTRA, GIT, TEST, EXAMPLES

## Module-Specific Cursor Rules

Modules can extend the root framework rules with module-specific development guidelines by creating a `.cursorrules` file in their module directory.

### Pattern

Each module can have its own `.cursorrules` file at:
```
GEO-INFER-{MODULE}/.cursorrules
```

### Purpose

Module-specific `.cursorrules` files:
- Extend root framework rules (`.cursorrules/` directory)
- Provide module-specific implementation requirements
- Document module-specific dependencies and integration patterns
- Specify module-specific "NO MOCK" requirements
- Include module-specific code structure guidelines

### Examples

- **GEO-INFER-ACT/.cursorrules**: Active Inference implementation requirements, free energy minimization, variational inference
- **GEO-INFER-SPACE/.cursorrules**: H3 v4 API requirements, backend-agnostic patterns, spatial operation standards
- **GEO-INFER-AGENT/.cursorrules**: Agent architecture requirements, perception-action loops, multi-agent coordination

### Structure

Module-specific `.cursorrules` files typically include:
1. **Module Overview**: Purpose and context
2. **Module-Specific Context**: Status, dependencies, key integrations
3. **Core Development Principles**: Extensions to root principles
4. **Module-Specific Implementation Requirements**: Domain-specific guidelines
5. **Module-Specific NO MOCK Requirements**: Domain-specific prohibitions
6. **Dependencies and Integration**: Module-specific integration patterns
7. **Data Sources and APIs**: Module-specific data requirements

### Relationship to Root Rules

- Root rules (`.cursorrules/` directory) apply to **all modules**
- Module-specific rules (`.cursorrules` file) **extend** root rules for that module
- Module rules should reference root rules: "This module extends the root framework rules (see `/.cursorrules`)"
- Conflicts are resolved in favor of module-specific rules for that module only

