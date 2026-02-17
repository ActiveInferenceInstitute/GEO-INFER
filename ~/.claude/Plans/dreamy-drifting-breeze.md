# GEO-INFER 44-Module Comprehensive Improvement Plan

## Context

Daniel requested a comprehensive review and improvement of all 44 GEO-INFER modules. After deep exploration via 3 parallel agents covering foundation (7 modules), infrastructure (10 modules), and domain (27 modules), plus a Plan agent synthesizing findings, the codebase state is fully mapped.

**Problem**: While structural scaffolding is consistent (all 44 modules have README.md, AGENTS.md, pyproject.toml, src/, tests/), implementation quality varies wildly — from production-ready (SPACE: 33k lines, 30 tests) to completely empty (CIV, ORG, REQ: 0 source lines). Many modules have severe test gaps (BAYES: 27 src files but only 1 test). Several domain modules are thin stubs. Four modules have PEP 8-violating uppercase package directories.

**Intended Outcome**: Every module has real implementations (no pass stubs except abstract methods), adequate tests (minimum 3 test files per module, 1 test file per significant source file), accurate documentation, and consistent structure.

---

## Approach: 10 Parallel Agent Groups Across 4 Phases

Given interdependencies (domain modules depend on MATH/SPACE/ACT), work is phased. Within each phase, groups run in parallel.

### Phase 1: Foundation (Groups 1-2 in parallel)

**Group 1 — MATH + SPACE** (Foundation math/spatial)
- MATH: Fix 3 convenience API stubs, add 11+ test files for untested core modules (geometry, graph_theory, interpolation, optimization, transforms, information_theory, theorem_proving)
- SPACE: Verify H3 v4 API consistency, add backend integration tests, performance benchmarks
- Files: `GEO-INFER-MATH/src/geo_infer_math/api/convenience/{bayes,ai,integration}_convenience.py`

**Group 2 — TIME + DATA** (Foundation temporal/data)
- TIME: Expand thin implementations (3266 lines for 9 files), add decomposition/trend/seasonality algorithms
- DATA: Add tests for 11 untested source files, add pipeline integration tests
- Both: Audit for stubs, verify `__init__.py` exports

### Phase 2: Core Analytics (Groups 3-5 in parallel)

**Group 3 — BAYES** (CRITICAL — worst test ratio in project)
- Fix 8 pass stubs: `__init__.py` GaussianProcess.fit/predict, `models/base.py` 5 methods, `core/model_comparison.py`, `utils/data_processing.py`
- Implement 3 NotImplementedError methods in inference/hierarchical/pymc_interface
- Write 15+ test files covering: inference, posterior, mcmc, hmc, variational, smc, abc, model_comparison, hierarchical, base_model, multilevel, dirichlet_process, spatiotemporal_gp, pymc_interface, priors, diagnostics

**Group 4 — ACT + SPM** (Active Inference + Statistical Parametric Mapping)
- ACT: Add tests for ecological/urban/climate models, dynamic_causal_model, verify SPACE integration
- SPM: Review edge cases, add performance tests (already best test ratio)

**Group 5 — AI + COG** (Machine Learning + Cognitive)
- AI: Expand from 1551 lines — implement real training pipeline, model evaluation, explainability, spatial predictor, feature engineering
- COG: Add 8+ test files for cognitive engine, spatial perception/reasoning/memory

### Phase 3: Integration & Domain (Groups 6-9 in parallel)

**Group 6 — AGENT + ANT + SIM** (Agent architectures)
- AGENT: Fix telemetry/messaging pass stubs, write 10+ test files
- ANT: Verify swarm algorithms, add integration tests
- SIM: Expand thin engine (3857 lines), implement ABM/system dynamics/CA simulation types

**Group 7 — FOREST + MARINE + ENERGY + WATER + CLIMATE** (Environmental domain)
- **FIRST**: Fix uppercase package naming (geo_infer_FOREST → geo_infer_forest) for FOREST, MARINE, ENERGY, WATER
- All 5: Expand thin implementations with real domain algorithms, write tests for every core file
- Target: Each module at minimum 2000+ lines with domain-specific algorithms

**Group 8 — HEALTH + ECON + RISK + AG + BIO + EMERGENCY + TRANSPORT + EDU + LOG** (Applied domains)
- ECON (25 src, 2 tests): Write 15+ test files
- RISK (25 src, 2 tests): Write 15+ test files
- AG: Add tests for soil_health, carbon_sequestration, water_usage models
- HEALTH: Expand implementations (good test ratio already)
- BIO: Write 6+ test files, audit implementations
- EMERGENCY/TRANSPORT/EDU: Expand thin implementations, add tests
- LOG: Add 8+ test files for logistics optimization

**Group 9 — NORMS + METAGOV + SEC + COMMS + GIT + IOT + PEP** (Governance & infrastructure)
- Each: Add 6-10 test files to address test gaps
- SEC: Verify auth/authz implementations are real
- IOT: Expand MQTT/sensor integration tests

### Phase 4: Application Layer & Empty Modules (Group 10)

**Group 10 — CIV + ORG + REQ + API + APP + OPS + TEST + EXAMPLES + INTRA + ART + PLACE**
- CIV/ORG/REQ: Implement from scratch based on README specs (participation_platform, organization_model, requirements_analyzer, etc.)
- API/APP: Verify FastAPI endpoints, expand test coverage
- TEST: Verify `run_unified_tests.py` works with all 44 modules
- EXAMPLES: Add working examples for 10+ modules
- INTRA: Verify documentation cross-references

---

## Critical Files

| File | Issue | Priority |
|------|-------|----------|
| `GEO-INFER-BAYES/src/geo_infer_bayes/__init__.py` | GaussianProcess.fit/predict are `pass` | P0 |
| `GEO-INFER-BAYES/src/geo_infer_bayes/models/base.py` | 5 `pass` stubs in base model | P0 |
| `GEO-INFER-CIV/src/geo_infer_civ/__init__.py` | Imports empty submodules w/o try/except | P1 |
| `GEO-INFER-ORG/src/geo_infer_org/__init__.py` | Empty package | P1 |
| `GEO-INFER-REQ/src/geo_infer_req/__init__.py` | Empty package | P1 |
| `GEO-INFER-FOREST/src/geo_infer_FOREST/` | Uppercase package name (PEP 8 violation) | P1 |
| `GEO-INFER-MARINE/src/geo_infer_MARINE/` | Uppercase package name | P1 |
| `GEO-INFER-ENERGY/src/geo_infer_ENERGY/` | Uppercase package name | P1 |
| `GEO-INFER-WATER/src/geo_infer_WATER/` | Uppercase package name | P1 |
| `GEO-INFER-MATH/src/geo_infer_math/api/convenience/*.py` | 3 convenience stubs | P2 |

---

## Verification (per agent group)

1. `python -c "import geo_infer_MODULE"` — import succeeds
2. `python -m pytest GEO-INFER-MODULE/tests/ -v` — all tests pass
3. `grep -rn "pass$" GEO-INFER-MODULE/src/ --include="*.py"` — no illegitimate stubs
4. Every module has >= 3 test files
5. Every source file with >50 lines has a corresponding test

## Final cross-module verification

1. `uv run python GEO-INFER-TEST/run_unified_tests.py` — full suite passes
2. All 44 modules import without errors
3. Zero `pass` stubs in non-abstract, non-exception methods

---

## Execution Strategy

Spin up 10 parallel general-purpose agents, one per group. Each agent receives:
- List of assigned modules
- Specific tasks per module (stub fixes, test writing, implementation expansion)
- Quality criteria (no mocks, type hints, real algorithms)
- Verification checklist

Groups 1-2 run first (foundation). Groups 3-5 follow (core). Groups 6-9 follow (domain). Group 10 last (application). Within each phase, all groups in that phase run simultaneously.

Given that most modules have loose coupling, **Phases 1-2 can be collapsed** — all 5 groups (1-5) can run in parallel since the inter-module dependencies are soft (try/except imports). Phase 3 groups 6-9 can also run in parallel with Phase 2 for the same reason. Only Group 10's CIV/ORG/REQ work truly depends on earlier phases being complete.

**Practical approach**: Launch all 10 groups simultaneously with instructions to focus on their assigned modules independently, using try/except patterns for cross-module imports.
