# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GEO-INFER is a 44-module geospatial inference framework implementing Active Inference principles for ecological, civic, and commercial applications. It is a Python monorepo using `uv` as the package manager, with Python 3.9+ required.

## Build & Development Commands

```bash
# Install a specific module (editable)
uv pip install -e ./GEO-INFER-MATH

# Install multiple modules
uv pip install -e ./GEO-INFER-MATH ./GEO-INFER-SPACE ./GEO-INFER-ACT

# Install with optional extras
uv pip install -e "./GEO-INFER-AI[dev,docs]"
```

## Testing

```bash
# Run unified test suite (all modules)
uv run python GEO-INFER-TEST/run_unified_tests.py

# Run tests for a specific module
uv run python GEO-INFER-TEST/run_unified_tests.py --module MATH

# Run by category (unit, integration, system, performance)
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# Run tests directly with pytest for a single module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Run a single test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# Run with coverage
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src --cov-report=html
```

Pytest markers: `unit`, `integration`, `system`, `performance`, `geospatial`, `api`, `slow`, `fast`.

## Code Quality

```bash
# Format
black GEO-INFER-MODULE/src/

# Sort imports
isort GEO-INFER-MODULE/src/

# Type check
mypy GEO-INFER-MODULE/src/

# Lint
flake8 GEO-INFER-MODULE/src/
```

Configuration: Black line-length 88, isort profile "black", mypy strict mode. All configured in root `pyproject.toml`.

## Architecture

### Module Layout

Every module follows this package structure:
```
GEO-INFER-MODULE/
├── src/geo_infer_module/
│   ├── __init__.py      # Exports with graceful try/except imports
│   ├── core/            # Core algorithms and logic
│   ├── models/          # Data models
│   ├── api/             # API endpoints/interfaces
│   └── utils/           # Helpers
├── tests/
│   ├── unit/
│   └── integration/
├── pyproject.toml
├── requirements.txt
├── .cursorrules         # Module-specific dev rules (extends root)
└── AGENTS.md            # Agent capabilities for this module
```

### Module Categories

- **Analytical Core**: MATH, ACT, BAYES, AI, COG, AGENT, SPM
- **Spatial-Temporal**: SPACE, TIME, IOT
- **Infrastructure**: DATA, API, SEC, OPS, METAGOV
- **Domain-Specific**: AG, HEALTH, ECON, RISK, LOG, BIO, CLIMATE, ENERGY, FOREST, MARINE, EMERGENCY, EDU
- **Agent & Simulation**: AGENT, ANT, SIM
- **Community & Applications**: CIV, PEP, ORG, COMMS, APP, ART
- **Governance**: NORMS, REQ
- **Operations**: OPS, INTRA, GIT, TEST, EXAMPLES, PLACE

### Data Flow

```
Data Sources → DATA → SPACE/TIME → MATH/BAYES/ACT → AI/AGENT → Domain Modules → API/APP
```

Foundation modules (MATH) have no dependencies. Core modules (BAYES, ACT) depend on MATH. Infrastructure (DATA, SPACE, TIME) is consumed by analytics (AI) and domain modules (AG, HEALTH, etc.). API and APP are the top-level consumers.

### Key Technical Decisions

- **H3 v4**: SPACE and PLACE modules are fully migrated to `h3>=4.0.0` (use `latlng_to_cell`, `cell_to_latlng`, not legacy API)
- **Backend-agnostic pattern**: SPACE module uses a dispatcher/interface pattern for H3 vs SRAI backends
- **Graceful degradation**: `__init__.py` files use `try/except` for optional dependency imports

## Critical Development Rules

These rules are from `.cursorrules/` and apply to all modules:

1. **NO MOCK METHODS**: Never create placeholder, stub, or mock implementations. Every function must have real logic. Use proper error handling instead of `pass` or `NotImplementedError`.

2. **Active Inference First**: Ground implementations in Active Inference mathematical principles (free energy minimization, Bayesian inference, perception-action loops).

3. **Concise Professional Language**: Avoid unnecessary adjectives and marketing hyperbole ("advanced", "sophisticated", "comprehensive" when not adding value). Use precise, technical language.

4. **Type Hints Everywhere**: Full type annotations on all function parameters and return values.

5. **Module-specific `.cursorrules`**: Individual modules may have their own `.cursorrules` file that extends the root rules. Check `GEO-INFER-MODULE/.cursorrules` before working on a module.

## Key Files & Resources

- `GEO-INFER-TEST/run_unified_tests.py` - Cross-module unified test runner
- `GEO-INFER-INTRA/docs/` - Central documentation hub (guides, tutorials, integration docs)
- `GEO-INFER-EXAMPLES/examples/` - Working examples including module orchestrators
- `.cursorrules/` - Framework-wide development rules
- `AGENTS.md` - Multi-agent systems architecture documentation
