# Module Structure Standards

Every module follows this canonical structure:

```
GEO-INFER-MODULE/
├── .cursorrules            # Module-specific cursor rules (optional)
├── config/                 # Configuration files (YAML/JSON)
│   ├── default.yaml        # Default configuration
│   └── schema.json         # Configuration validation schema
├── docs/                   # Documentation (markdown, API specs)
│   ├── api_schema.yaml     # OpenAPI documentation
│   ├── architecture.md     # Module architecture
│   └── tutorials/          # Step-by-step tutorials
├── examples/               # Working examples and demonstrations
│   ├── basic_example.py    # Basic usage
│   └── advanced_example.py # Advanced workflows
├── src/                    # Source code
│   └── geo_infer_module/   # Main package (lowercase, underscored)
│       ├── __init__.py     # Package init with version and exports
│       ├── api/            # API definitions and routes
│       │   ├── __init__.py
│       │   ├── rest_api.py
│       │   └── schemas.py
│       ├── core/           # Core functionality and algorithms
│       │   ├── __init__.py
│       │   ├── main_engine.py
│       │   └── algorithms.py
│       ├── models/         # Data models and schemas
│       │   ├── __init__.py
│       │   └── data_models.py
│       └── utils/          # Utility functions and helpers
│           ├── __init__.py
│           ├── helpers.py
│           └── validation.py
├── tests/                  # Comprehensive test suite
│   ├── conftest.py         # Shared fixtures
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── performance/        # Performance benchmarks
├── pyproject.toml          # Package metadata, deps, tool config
├── AGENTS.md               # AI agent guidance for this module
├── CHANGELOG.md            # Version history (Keep a Changelog format)
└── README.md               # Module documentation with YAML front matter
```

## Required Files

| File | Purpose |
|------|---------|
| `README.md` | Module overview, API reference, getting started |
| `AGENTS.md` | AI agent guidance: key files, patterns, gotchas |
| `pyproject.toml` | Package metadata, dependencies, tool config |
| `src/geo_infer_*/` | Source package (PEP 8 lowercase) |
| `tests/` | Test suite with unit + integration subdirs |

## README Structure

All module READMEs must include:

1. **YAML Front Matter** — metadata (title, description, purpose, module_type, status, dependencies, tags)
2. **Overview** — module purpose and scope
3. **Core Features** — (not "Key Features") capabilities list
4. **API Reference** — core classes with signatures and examples
5. **Integration** — how it works with other modules
6. **Getting Started** — installation and basic usage
7. **Examples** — working code
8. **Troubleshooting** — common issues and solutions

## Module Categories (44 modules)

| Category | Modules |
|----------|---------|
| 🧠 **Analytical Core** | ACT, BAYES, AI, MATH, COG, AGENT, SPM |
| 🗺️ **Spatial-Temporal** | SPACE, TIME, IOT |
| 💾 **Data Management** | DATA, API |
| 🔒 **Security & Governance** | SEC, NORMS, REQ, METAGOV |
| 🧪 **Simulation & Modeling** | SIM, ANT |
| 👥 **People & Community** | CIV, PEP, ORG, COMMS |
| 🖥️ **Applications** | APP, ART |
| 🏢 **Domain-Specific** | AG, ECON, RISK, LOG, BIO, HEALTH, CLIMATE, ENERGY, WATER, TRANSPORT, FOREST, MARINE, EMERGENCY, EDU |
| 📍 **Place-Based** | PLACE |
| ⚙️ **Operations** | OPS, INTRA, GIT, TEST, EXAMPLES |

## Module-Specific Cursor Rules

Modules extend root rules with a `.cursorrules` file at `GEO-INFER-{MODULE}/.cursorrules`.

### File Structure

Module-specific `.cursorrules` files include:

1. **Module Overview** — purpose and context
2. **Module-Specific Context** — status, dependencies, key integrations
3. **Core Development Principles** — extensions to root principles
4. **Implementation Requirements** — domain-specific guidelines
5. **NO MOCK Requirements** — domain-specific prohibitions
6. **Dependencies and Integration** — module-specific patterns
7. **Data Sources and APIs** — module-specific data requirements

### Relationship to Root Rules

- Root rules (this directory) apply to **all modules**
- Module rules **extend** root rules for that specific module
- Conflicts are resolved in favour of module-specific rules
- Module rules should reference root rules: "Extends `/.cursorrules`"
