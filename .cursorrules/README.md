# GEO
-INFER Cursor Rules

This directory contains modular cursor rules for the GEO-INFER framework development. Rules are organized by topic for maintainability and clarity.

## Structur
e

- **`README.md`** (this file) - Overview and navigation
- **`principles.md`** - Core development principles and philosophy
- **`structure.md`** - Module structure standards and organization
- **`implementation.md`** - Code implementation guidelines
- **`workflow.md`** - Development workflow and environment management
- **`testing.md`** - Testing requirements and standards
- **`integration.md`** - Module integration patterns and guidelines
- **`documentation.md`** - Documentation standards and requirements
- **`requirements.md`** - Critical requirements (NEVER/ALWAYS rules)
- **`standards.md`** - Excellence standards and code review checklist
- **`navigation.md`** - Navigation guide and key resources

## Quick
 Reference

### Mos
t
 Important Rules
1. **NO MOCK METHODS** - See `principles.md`
2. **Use `uv` for all package management** - See `workflow.md`
3. **Follow module structure standards** - See `structure.md`
4. **documentation required** - See `documentation.md`
5. **Active Inference first** - See `principles.md`

## Framework
 Overview

GEO-INFER is a geospatial inference framework implementing Active Inference principles for ecological, civic, and commercial applications. The framework consists of 30+ specialized modules organized into distinct categories.

### Cor
e
 Module Categories:
- **🧠 Analytical Core**: ACT, BAYES, AI, MATH, COG, AGENT, SPM
- **🗺️ Spatial-Temporal**: SPACE, TIME, IOT
- **💾 Data Management**: DATA, API
- **🔒 Security & Governance**: SEC, NORMS, REQ, METAGOV
- **🧪 Simulation & Modeling**: SIM, ANT
- **👥 People & Community**: CIV, PEP, ORG, COMMS
- **🖥️ Applications**: APP, ART
- **🏢 Domain-Specific**: AG, ECON, RISK, LOG, BIO, HEALTH, CLIMATE, ENERGY, WATER, TRANSPORT, FOREST, MARINE, EMERGENCY, EDU
- **📍 Place-Based**: PLACE
- **⚙️ Operations**: OPS, INTRA, GIT, TEST, EXAMPLES

## Usag
e

Cursor will automatically load rules from this directory. For specific guidance, refer to the relevant module file.

## Module
-Specific Rules

Modules can extend these root framework rules with module-specific development guidelines by creating a `.cursorrules` file in their module directory.

### Patte
r
n

Each module can have its own `.cursorrules` file at:
```
GEO-INFER-{MODULE}/.cursorrules
```

### Ho
w
 It Works

- **Root Rules** (`.cursorrules/` directory): Apply to all modules universally
- **Module Rules** (`GEO-INFER-{MODULE}/.cursorrules`): Extend root rules with module-specific requirements
- **Relationship**: Module rules reference and extend root rules, not replace them

### Exampl
e
s

Many modules already have module-specific `.cursorrules` files:
- `GEO-INFER-ACT/.cursorrules` - Active Inference implementation requirements
- `GEO-INFER-SPACE/.cursorrules` - H3 v4 API requirements and spatial standards
- `GEO-INFER-AGENT/.cursorrules` - Agent architecture and coordination patterns

For details on the module-specific rules pattern, see `structure.md` in this directory.

## Key
 Resources

- **Main README**: `/README.md` - project overview
- **Module Index**: `GEO-INFER-INTRA/docs/modules/index.md` - All modules overview
- **Integration Guide**: `GEO-INFER-INTRA/docs/guides/MODULE_INTEGRATION_GUIDE.md` - Cross-module patterns
- **Standards**: `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md` - Documentation guidelines

