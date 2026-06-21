# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this GEO-INFER repository.

## Project Overview

GEO-INFER is a 44-module geospatial inference framework implementing Active Inference principles for ecological, civic, and commercial applications. It is a Python monorepo using `uv` as the package manager, with Python 3.11+ required.

### Current Stats (2026-06-15)

- **44 modules** | **884 Python source files** | **441 Python test files**
- All package directories follow PEP 8 lowercase naming: `geo_infer_<module>` (including `geo_infer_forest`, `geo_infer_marine`, `geo_infer_energy`, `geo_infer_water`). Mixed-case directory normalization is complete.
- Repo contract checks live in `GEO-INFER-TEST/validate_repo_contracts.py`; source-language debt is reported by default and can be made fatal with `--strict-source-language`.
- The same contract validator also enforces root uv workspace hygiene, per-module test inventory, source/test task-marker hygiene, and library logging configuration.
- Every module has a minimum of 4 test files.

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

# Run by category (unit, integration, performance, coverage, all)
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# Run tests directly with pytest for a single module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# Run a single test file
uv run python -m pytest GEO-INFER-MATH/tests/unit/test_spatial_statistics.py -v

# Run with coverage
uv run python -m pytest GEO-INFER-MATH/tests/ --cov=GEO-INFER-MATH/src --cov-report=html

# Validate repo-wide contracts and Active Inference API contracts
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_repo_contracts.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
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

# Lint changed files or a module
uv run ruff check GEO-INFER-MODULE/src/

# Format check
uv run black --check GEO-INFER-MODULE/src/
```

Configuration: Black line-length 88, isort profile "black", mypy strict mode. All configured in root `pyproject.toml`.

## Architecture

### Module Layout

Every module follows this package structure:

```text
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
├── examples/            # Working, runnable examples
├── pyproject.toml
├── requirements.txt
├── README.md            # Module overview and usage
├── AGENTS.md            # Agent capabilities and integration
├── SKILL.md             # Claude Code skill (auto-discovered)
└── .cursorrules         # Module-specific dev rules (extends root)
```

### Module Categories

- **Analytical Core**: MATH, ACT, BAYES, AI, COG, AGENT, SPM
- **Spatial-Temporal**: SPACE, TIME, IOT
- **Infrastructure**: DATA, API, SEC, OPS, METAGOV
- **Domain-Specific**: AG, HEALTH, ECON, RISK, LOG, BIO, CLIMATE, ENERGY, FOREST, MARINE, EMERGENCY, EDU, TRANSPORT, WATER
- **Agent & Simulation**: AGENT, ANT, SIM
- **Community & Applications**: CIV, PEP, ORG, COMMS, APP, ART
- **Governance**: NORMS, REQ
- **Operations**: OPS, INTRA, GIT, TEST, EXAMPLES, PLACE

### Data Flow

```text
Data Sources → DATA → SPACE/TIME → MATH/BAYES/ACT → AI/AGENT → Domain Modules → API/APP
```

Foundation modules (MATH) have no dependencies. Core modules (BAYES, ACT) depend on MATH. Infrastructure (DATA, SPACE, TIME) is consumed by analytics (AI) and domain modules (AG, HEALTH, etc.). API and APP are the top-level consumers.

### Key Technical Decisions

- **H3 v4**: SPACE and PLACE modules are fully migrated to `h3>=4.5.0,<5` (use `latlng_to_cell`, `cell_to_latlng`, not legacy API).
- **Backend-agnostic pattern**: SPACE module uses a dispatcher/interface pattern for H3 vs SRAI backends.
- **Graceful degradation**: `__init__.py` files use `try/except` for optional dependency imports, with module-level `HAS_<DEP>` flags consumed by call sites.
- **Package directory casing**: All 44 modules use `geo_infer_<module>` (lowercase) naming.
- **Real implementations only**: BAYES GaussianProcess uses Cholesky decomposition. Model comparison uses real LOO/WAIC/DIC/BIC/AIC. ACT free energy exposes typed breakdowns and uses `complexity - accuracy` for categorical variational free energy.
- **Active Inference contract**: `GEO-INFER-ACT` exports `FreeEnergyBreakdown`, `PolicyEvaluation`, and `ActiveInferenceStepResult`. `PolicySelector(selection_mode="deterministic")` selects the lowest expected free energy; stochastic selection is seedable.

## Critical Development Rules

These rules are from `.cursorrules/` and apply to all modules:

1. **NO MOCK METHODS**: Never create placeholder, stub, or mock implementations. Every function must have real logic. Use proper error handling instead of `pass` or `NotImplementedError`.

2. **Active Inference First**: Ground implementations in Active Inference mathematical principles (free energy minimization, Bayesian inference, perception-action loops).

3. **Concise Professional Language**: Avoid unnecessary adjectives and marketing hyperbole ("advanced", "sophisticated", "comprehensive" when not adding value). Use precise, technical language.

4. **Type Hints Everywhere**: Full type annotations on all function parameters and return values.

5. **Module-specific `.cursorrules`**: Individual modules may have their own `.cursorrules` file that extends the root rules. Check `GEO-INFER-MODULE/.cursorrules` before working on a module.

6. **Docs track code**: Every code change must keep `README.md` (user-facing) and `AGENTS.md` (agent/integration-facing) in sync with the implementation.

7. **Modular hygiene is centralized**: Root `pyproject.toml`, `uv.lock`, and `.python-version` define the uv environment; planned work belongs in root `TODO.md` or an issue; module source and tests must not carry local task markers.

8. **Library logging is passive**: Importable modules should create loggers with `logging.getLogger(__name__)`. Configure process-wide handlers only in CLI entrypoints.

## Key Files & Resources

- `GEO-INFER-TEST/run_unified_tests.py` - Cross-module unified test runner
- `GEO-INFER-TEST/validate_repo_contracts.py` - Module inventory, signposting, casing, setup syntax, and source-language debt report
- `GEO-INFER-TEST/validate_active_inference_contract.py` - Executable ACT API contract check
- `GEO-INFER-INTRA/docs/` - Central documentation hub (guides, tutorials, integration docs)
- `GEO-INFER-EXAMPLES/examples/` - Working examples including module orchestrators
- `SKILL.md` - Root Claude Code skill (ecosystem overview)
- `GEO-INFER-*/SKILL.md` - Module-level Claude Code skills (44 files)
- `.cursorrules/` - Framework-wide development rules
- `AGENTS.md` - Multi-agent systems architecture documentation
- `PAI.md` - PAI Algorithm integration and development methodology
- `ISA.md` - Current ideal-state criteria and verification targets
- `CLAUDE.md` - This file (Claude Code guidance)
