# Plan: GEO-INFER-INTRA Comprehensive Documentation Update

## Context

GEO-INFER-INTRA is the central documentation hub for the 44-module GEO-INFER framework.
The codebase is at v0.2.0 (released 2026-02-25) but many documentation files still contain
v0.1.0 era content, wrong metadata (framework_version: "1.0.0", last_updated: "2026-01-24"),
broken internal links, incorrect license references (MIT instead of CC BY-NC-SA 4.0),
wrong GitHub URLs, missing module entries (EXAMPLES), incomplete module catalog, and
16 files referenced in docs/index.md that don't yet exist.

This plan covers all 5 update categories: metadata corrections, broken link fixes, new file
creation, module status matrix updates, and module catalog expansion.

---

## Scope: 21 Files Total (16 creates + 5 major updates)

---

## Part A — Update Existing Files (5 files)

### A1. `GEO-INFER-INTRA/README.md`
**Changes:**
- `last_updated: "2026-02-24"` → `"2026-02-25"`
- Add framework stats block: 44 modules | 858 source files | 295,696 source lines | 416 test files | 3,000+ tests
- Fix directory structure: `src/geo_infer_intra/config.py` → `src/geo_infer_intra/utils/config.py`
- Add reference to PAI.md development methodology

### A2. `GEO-INFER-INTRA/AGENTS.md`
**Changes:**
- Add GEO-INFER-SPM (Statistical Parametric Mapping) under new modules
- Add GEO-INFER-EXAMPLES (Cross-module integration demonstrations)
- Update framework stats to match current (44 modules, 20/44 Beta+, 24/44 Alpha)
- Add v0.2.0 capability context (Zero-Mock Policy, H3 v4 complete)

### A3. `GEO-INFER-INTRA/docs/index.md`
**Changes (critical):**
- Fix ALL `../getting_started/` → `getting_started/` (docs/index.md is AT docs/ root, not a subdir)
- License: `MIT` → `CC BY-NC-SA 4.0`
- GitHub URLs: `geo-infer/geo-infer-intra` → `ActiveInferenceInstitute/GEO-INFER`
- Remove/mark-TBD fictitious community links (`forum.geo-infer.org`, `discord.gg/geo-infer`)
- Fix geospatial concept paths:
  - `geospatial/coordinate_systems.md` → `geospatial/concepts/coordinate_systems.md`
  - `geospatial/spatial_relationships.md` → `geospatial/concepts/spatial_relationships.md`
- Fix H3 link: `h3_guide.md` → `geospatial/data_formats/h3/index.md`
- Add EXAMPLES module to module quick-reference links

### A4. `GEO-INFER-INTRA/docs/modules/index.md`
**Changes:**
- `last_updated: "2026-01-24"` → `"2026-02-25"`
- `framework_version: "1.0.0"` → `"0.2.0"`
- Fix SPM description: "Spatial Process Modeling" → "Statistical Parametric Mapping"
- Fix LOG description: "Logging & Monitoring" → "Logistics & Supply Chain"
- Add EXAMPLES module row to Operations section (currently absent)
- Update module status matrix to match TODO.md (2026-02-25) — full status for all 44:

| Module | Old Status | Correct Status (from TODO.md) |
|--------|-----------|-------------------------------|
| BAYES | "In Progress" in status table | ✅ Beta |
| AI | ✅ | 🔄 Alpha (no known blockers) |
| AGENT | 🔄 In Development | 🔄 Alpha |
| SPM | 🔄 In Development | 🔄 Alpha (GLM incomplete) |
| IOT | 🔄 In Development | ✅ Beta |
| HEALTH | 🔄 In Development | ✅ Beta |
| BIO | 🔄 In Development | ✅ Beta |
| CLIMATE | 🔄 In Development | ✅ Beta |
| FOREST | 🔄 In Development | ✅ Beta |
| MARINE | 🔄 In Development | 🔄 Alpha |
| COMMS | 🔄 In Development | ✅ Beta |
| APP | 🔄 In Development | ✅ Beta |
| ART | 🔄 In Development | ✅ Beta |
| PLACE | 🔄 In Development | ✅ Beta (H3 v4) |
| GIT | 🔄 In Development | ✅ Beta |
| TEST | 🔄 In Development | ✅ Stable |
| LOG | 🔄 In Development | ✅ Beta |
| EXAMPLES | Missing | ✅ Beta |

### A5. `GEO-INFER-INTRA/docs/architecture/module_catalog.md`
**Changes:**
- Currently only catalogs ~15 of 44 modules; add all 29 missing entries
- Missing modules to add: MATH, BAYES, AI, COG, SPM, ANT, TIME, IOT, NORMS, REQ, METAGOV,
  CIV, PEP, ORG, COMMS, ART, APP, AG, RISK, HEALTH, CLIMATE, ENERGY, FOREST, MARINE,
  WATER, TRANSPORT, EMERGENCY, EDU, PLACE, TEST, EXAMPLES
- Expand Mermaid dependency graph to show all 44 nodes
- Add EXAMPLES to the "Development Support" or "Operations" section

---

## Part B — Create New Files (16 files)

All files follow the project's YAML front-matter standard. Each is purpose-built to satisfy
the broken link referenced in docs/index.md.

### B1. `docs/getting_started/spatial_analysis_basics.md`
**Purpose:** Spatial analysis concepts for beginners — coordinate systems, H3 indexing,
spatial operations (buffer, intersection, union). Links to SPACE module.
**Key sections:** Coordinate Systems, H3 Indexing, Basic Operations, Quick Examples.

### B2. `docs/getting_started/first_map.md`
**Purpose:** Step-by-step "create your first geospatial visualization" tutorial.
Uses `geo_infer_space` + matplotlib/folium. Working code example.
**Key sections:** Prerequisites, Create Point Data, Add to Map, Visualize, Next Steps.

### B3. `docs/integration/external_systems.md`
**Purpose:** How to connect GEO-INFER to external data sources (PostGIS, STAC catalogs,
OGC WMS/WFS, REST APIs, streaming sources).
**Key sections:** Database Integration, OGC Service Integration, REST API Integration,
Streaming Data, Authentication Patterns.

### B4. `docs/integration/geo_infer_modules.md`
**Purpose:** Detailed inter-module integration patterns with code examples — how modules
communicate, data contracts, common pipelines.
**Key sections:** Linear Pipeline, Hub-Spoke, Event-Driven, Feedback Loop patterns.
Code examples for SPACE↔TIME, ACT↔BAYES, DATA↔API integrations.

### B5. `docs/deployment/environment.md`
**Purpose:** Environment configuration guide — environment variables, configuration files,
secrets management, development vs. production profiles.
**Key sections:** Environment Variables, config.yaml structure, Secrets Management,
Profile Management (dev/staging/prod).

### B6. `docs/deployment/scaling.md`
**Purpose:** Horizontal and vertical scaling strategies for GEO-INFER in production.
**Key sections:** Single-Node Setup, Multi-Node Deployment, Load Balancing, H3-Based
Spatial Sharding, Celery Worker Scaling, Memory Management.

### B7. `docs/advanced/performance_optimization.md`
**Purpose:** Performance tuning guide — H3 spatial indexing optimization, NumPy vectorization,
caching strategies, profiling tools.
**Key sections:** Profiling, Spatial Query Optimization, Memory Reduction, Parallel
Processing, Caching, Benchmarks.

### B8. `docs/advanced/custom_models.md`
**Purpose:** How to build specialized Active Inference models extending base classes.
**Key sections:** Generative Model Architecture, Custom Free Energy Functions, Policy
Selection, Spatial Prior Construction, Testing Custom Models.

### B9. `docs/advanced/scaling_guide.md`
**Purpose:** Large-scale data processing guide for big geospatial datasets.
**Key sections:** Data Partitioning, H3-Based Parallelism, Distributed Processing with
Celery/Dask, Memory-Efficient Patterns, Benchmarks.

### B10. `docs/advanced/production_architecture.md`
**Purpose:** Reference architecture for production GEO-INFER deployments — microservices
design, containerization, Kubernetes deployment template.
**Key sections:** Architecture Diagram, Container Setup, Kubernetes Manifests, Monitoring
with Prometheus/Grafana, CI/CD Pipeline.

### B11. `docs/support/troubleshooting.md`
**Purpose:** Common problems and solutions across all 44 modules.
**Key sections:** Import Errors, H3 API Version Issues, NumPy Shape Mismatches, Config
Loading Failures, MCMC Convergence, Memory Errors, Test Failures.

### B12. `docs/support/installation_issues.md`
**Purpose:** Installation troubleshooting — uv install failures, dependency conflicts,
Python version issues, platform-specific problems.
**Key sections:** uv Setup, Dependency Resolution, Platform Issues (macOS/Linux/Windows),
Optional Dependency Errors, Virtual Environment Problems.

### B13. `docs/support/performance_issues.md`
**Purpose:** Diagnosing and resolving performance problems.
**Key sections:** Identifying Bottlenecks, Profiling with cProfile/Scalene, Common Slow
Paths, H3 Performance Anti-patterns, Memory Leak Detection.

### B14. `docs/bayesian_inference_guide.md`
**Purpose:** Comprehensive guide to Bayesian inference in GEO-INFER — covers BAYES module,
MCMC sampling, Gaussian Processes, model comparison (LOO/WAIC/DIC/BIC/AIC).
**Key sections:** Bayesian Foundations, MCMC Sampling, Gaussian Processes (Cholesky),
Model Comparison, Spatial Priors, Integration with ACT.

### B15. `docs/temporal_analysis_guide.md`
**Purpose:** Temporal analysis deep-dive — time series decomposition, forecasting, temporal
pattern detection, spatiotemporal analysis.
**Key sections:** Time Series Basics, Decomposition, Forecasting Models, Seasonal Patterns,
Spatiotemporal Integration, Real-Time Streaming.

### B16. `SKILL.md` (at `GEO-INFER-INTRA/SKILL.md`)
**Purpose:** PAI skill descriptor for GEO-INFER-INTRA — enables PAI to know when/how to
invoke INTRA capabilities (documentation generation, configuration management,
repository assessment, testing utilities).
**Content:** Frontmatter (name, description, triggers), capabilities overview, tool invocation
patterns, integration with other INTRA docs, last_updated.

---

## Verification Plan

After execution, verify:

```bash
# 1. No broken internal links in key files
grep -n "\.\.\/" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/index.md | grep "getting_started"
# Expected: 0 results (all fixed to relative without ../)

# 2. License is correct in docs/index.md
grep "License" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/index.md
# Expected: "CC BY-NC-SA 4.0"

# 3. Correct GitHub URLs
grep "geo-infer/geo-infer-intra" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/index.md
# Expected: 0 results (all replaced)

# 4. All 16 new files exist
ls /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/getting_started/spatial_analysis_basics.md
ls /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/getting_started/first_map.md
ls /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/advanced/performance_optimization.md
ls /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/support/troubleshooting.md
ls /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/SKILL.md

# 5. Module catalog covers all 44 modules
grep -c "GEO-INFER-" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/architecture/module_catalog.md
# Expected: ≥44

# 6. modules/index.md has updated metadata
grep "last_updated\|framework_version" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/modules/index.md
# Expected: 2026-02-25, 0.2.0

# 7. EXAMPLES module appears in modules index
grep -i "examples" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/modules/index.md
# Expected: at least 1 row with EXAMPLES

# 8. SPM description is correct
grep "SPM" /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/modules/index.md
# Expected: "Statistical Parametric Mapping"
```

---

## Critical Files Modified

| File | Type | Key Changes |
|------|------|-------------|
| `GEO-INFER-INTRA/README.md` | Update | Stats, date, paths |
| `GEO-INFER-INTRA/AGENTS.md` | Update | SPM, EXAMPLES, stats |
| `GEO-INFER-INTRA/SKILL.md` | **Create** | New PAI skill descriptor |
| `docs/index.md` | Update | Links, license, GitHub URLs |
| `docs/modules/index.md` | Update | Metadata, 44-module status matrix |
| `docs/architecture/module_catalog.md` | Update | Expand from 15→44 modules |
| `docs/getting_started/spatial_analysis_basics.md` | **Create** | Spatial concepts intro |
| `docs/getting_started/first_map.md` | **Create** | First visualization tutorial |
| `docs/integration/external_systems.md` | **Create** | External system integration |
| `docs/integration/geo_infer_modules.md` | **Create** | Inter-module integration |
| `docs/deployment/environment.md` | **Create** | Environment config guide |
| `docs/deployment/scaling.md` | **Create** | Scaling strategies |
| `docs/advanced/performance_optimization.md` | **Create** | Performance tuning |
| `docs/advanced/custom_models.md` | **Create** | Custom AI model development |
| `docs/advanced/scaling_guide.md` | **Create** | Large-scale data guide |
| `docs/advanced/production_architecture.md` | **Create** | Production deployment |
| `docs/support/troubleshooting.md` | **Create** | Common problems & solutions |
| `docs/support/installation_issues.md` | **Create** | Install troubleshooting |
| `docs/support/performance_issues.md` | **Create** | Performance troubleshooting |
| `docs/bayesian_inference_guide.md` | **Create** | Bayesian methods guide |
| `docs/temporal_analysis_guide.md` | **Create** | Temporal analysis guide |
