# GEO-INFER Cursor Rules

> **Version**: 0.2.0 · **Last Updated**: 2026-02-25 · **Modules**: 44

This directory contains modular cursor rules for the GEO-INFER framework. Rules are organised by topic for maintainability and clarity.

## File Index

| File | Purpose |
|------|---------|
| `README.md` | Overview and navigation (this file) |
| `principles.md` | Core development principles and philosophy |
| `structure.md` | Module structure standards and organisation |
| `implementation.md` | Code implementation guidelines and patterns |
| `workflow.md` | Development workflow, CI/CD, and environment management |
| `testing.md` | Testing requirements, coverage, and CI |
| `integration.md` | Module integration patterns and dependency matrix |
| `documentation.md` | Documentation standards and templates |
| `requirements.md` | Critical NEVER/ALWAYS rules |
| `standards.md` | Excellence standards and code review checklist |
| `navigation.md` | Navigation guide and key resources |

## Quick Reference — Most Important Rules

1. **NO MOCK METHODS** — Every function must be fully implemented (`principles.md`)
2. **Use `uv` for all package management** — Never use bare `pip` (`workflow.md`)
3. **Follow module structure standards** — 44 modules, one canonical layout (`structure.md`)
4. **Documentation required** — YAML front matter, docstrings, AGENTS.md (`documentation.md`)
5. **Active Inference first** — Ground implementations in free energy principles (`principles.md`)
6. **Structured logging** — `logging.getLogger(__name__)` everywhere (`implementation.md`)

## Framework Overview

GEO-INFER is a geospatial inference framework implementing Active Inference principles for ecological, civic, and commercial applications. The framework consists of **44 specialised modules** organised into distinct categories.

### Module Categories (44 modules)

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

## Module-Specific Rules

Modules extend these root rules with module-specific `.cursorrules` files:

```
GEO-INFER-{MODULE}/.cursorrules
```

- **Root rules** (this directory): Apply to all modules universally
- **Module rules** (`GEO-INFER-{MODULE}/.cursorrules`): Extend root rules for that module
- **Conflict resolution**: Module-specific rules take precedence for that module only

### Examples

- `GEO-INFER-ACT/.cursorrules` — Active Inference implementation requirements
- `GEO-INFER-SPACE/.cursorrules` — H3 v4 API requirements and spatial standards
- `GEO-INFER-AGENT/.cursorrules` — Agent architecture and coordination patterns

## Key Resources

- **Main README**: `/README.md`
- **TODO & Roadmap**: `/TODO.md`
- **Module Index**: `GEO-INFER-INTRA/docs/modules/index.md`
- **Integration Guide**: `GEO-INFER-INTRA/docs/guides/MODULE_INTEGRATION_GUIDE.md`
- **Documentation Standards**: `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md`
