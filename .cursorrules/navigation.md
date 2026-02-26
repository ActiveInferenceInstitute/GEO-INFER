# Navigation Guide

## Quick-Start Decision Tree

```
What do you need?
├── Understand a module → Read its README.md
├── AI guidance for a module → Read its AGENTS.md
├── See working code → Check examples/ directory
├── Understand expected behaviour → Read tests/ directory
├── Configuration patterns → Check config/ directory
├── Cross-module integration → See integration.md
├── What's left to do → Read /TODO.md
└── Module architecture → Read docs/architecture.md
```

## Common Tasks

| Task | Where to Look |
|------|--------------|
| Find a module's main engine | `GEO-INFER-MODULE/src/geo_infer_module/core/` |
| Find API endpoints | `GEO-INFER-MODULE/src/geo_infer_module/api/rest_api.py` |
| Find data models | `GEO-INFER-MODULE/src/geo_infer_module/models/` |
| Find utilities | `GEO-INFER-MODULE/src/geo_infer_module/utils/` |
| Find test fixtures | `GEO-INFER-MODULE/tests/conftest.py` |
| Find config schema | `GEO-INFER-MODULE/config/schema.json` |
| Check dependencies | `GEO-INFER-MODULE/pyproject.toml` |
| Find all modules list | `/TODO.md` → Module Status Registry |

## File Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Python modules | `snake_case.py` | `risk_engine.py` |
| Test files | `test_<module>.py` | `test_risk_engine.py` |
| Config files | `<name>.yaml` | `default.yaml` |
| Documentation | `<TOPIC>.md` (uppercase) | `AGENTS.md` |
| Package dirs | `geo_infer_<module>` | `geo_infer_risk` |

## Key Resources

| Resource | Path |
|----------|------|
| Project README | `/README.md` |
| TODO & Roadmap | `/TODO.md` |
| Module Index | `GEO-INFER-INTRA/docs/modules/index.md` |
| Integration Guide | `GEO-INFER-INTRA/docs/guides/MODULE_INTEGRATION_GUIDE.md` |
| Doc Standards | `GEO-INFER-INTRA/docs/DOCUMENTATION_STANDARDS.md` |
| CI Config | `.github/workflows/ci.yml` |
| Root Cursorrules | `.cursorrules/` (this directory) |

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

## Understanding Dependencies

- Check `pyproject.toml` for declared dependencies
- Review the dependency matrix in `integration.md`
- Understand the layered architecture: Foundation → Data → Domain → Application
- Consider both direct and transitive dependencies
- Use `uv pip install -e .` to install a module with its deps

## Contributing

1. Read the module's README.md and AGENTS.md
2. Understand the module's role in the architecture (see `integration.md`)
3. Follow coding patterns established in `implementation.md`
4. Write tests following `testing.md` standards
5. Format and lint before committing (see `workflow.md`)
6. Consider impacts on dependent modules
