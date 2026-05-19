# PAI Integration with GEO-INFER

## Overview

The GEO-INFER framework uses [PAI (Personal AI Infrastructure)](https://github.com/danielmiessler/PAI) as its development methodology. PAI's Algorithm provides a systematic 7-phase approach (OBSERVE, THINK, PLAN, BUILD, EXECUTE, VERIFY, LEARN) with Ideal State Criteria (ISC) for verifiable progress tracking.

## How PAI Drives Development

### The Algorithm Applied to GEO-INFER

Every significant development task follows the PAI Algorithm:

1. **OBSERVE** - Decompose the request into granular, binary-testable Ideal State Criteria (8-12 words each, state-not-action)
2. **THINK** - Pressure-test assumptions, identify risks, refine criteria
3. **PLAN** - Design execution strategy, identify parallelization opportunities
4. **BUILD** - Create artifacts (code, tests, documentation) against criteria
5. **EXECUTE** - Run the work using selected capabilities (agents, tools, skills)
6. **VERIFY** - Mechanically verify every criterion with evidence
7. **LEARN** - Capture reflections for continuous improvement

### Parallel Agent Orchestration

For large-scale tasks, PAI spawns parallel agent groups that work independently on module subsets. The February 2026 comprehensive improvement used 10 parallel agents covering all 44 modules simultaneously:

| Agent Group | Modules | Key Outcomes |
|-------------|---------|--------------|
| G1: Foundation Math/Spatial | MATH, SPACE | 128 tests, ALS decomposition, H3 v4 verified |
| G2: Foundation Temporal/Data | TIME, DATA | 340+177 tests, interpolation bug fix |
| G3: Bayesian Critical | BAYES | Real GP (Cholesky), LOO/WAIC/DIC, 150 tests |
| G4: Active Inference | ACT, SPM | 111 tests, free_energy.py bug fix |
| G5: ML/Cognitive | AI, COG | 79+146 tests, f-string/import fixes |
| G6: Agent Architecture | AGENT, ANT, SIM | 140+50+30 tests, compatibility fixes |
| G7: Environmental | FOREST, MARINE, ENERGY, WATER, CLIMATE | 4 package renames, 286 tests, 8 bugs fixed |
| G8: Applied Domains | HEALTH, ECON, RISK, AG, BIO, EMERGENCY, TRANSPORT, EDU, LOG | 740 tests, 13 bugs fixed |
| G9: Governance | NORMS, METAGOV, SEC, COMMS, GIT, IOT, PEP | 522 tests, 7 source + 11 test bugs fixed |
| G10: Application Layer | CIV, ORG, REQ, API, APP, OPS, EXAMPLES, INTRA, ART, PLACE | 3 modules built from scratch, 527 tests |

### Ideal State Criteria Examples

GEO-INFER development tasks use ISC like:

- `ISC-C1: All 44 modules import without errors` (Verify: CLI)
- `ISC-C2: Every module has minimum four test files` (Verify: Grep)
- `ISC-C3: Zero uppercase package directory names exist` (Verify: CLI)
- `ISC-C4: No illegitimate pass stubs in source code` (Verify: Grep)
- `ISC-A1: No mock or placeholder implementations introduced` (Verify: Grep)

## Development Methodology

### No Mock Policy

GEO-INFER enforces a strict no-mock policy aligned with PAI's verification principles:

- Every function has real algorithmic logic
- `pass` is only allowed in abstract methods, exception handlers, and `ImportError` guards
- Tests verify actual behavior, not mocked responses
- Bayesian methods use real mathematics (Cholesky decomposition, variational inference) not random numbers

### Active Inference Grounding

Implementations are grounded in Active Inference mathematical principles:

- **Free Energy Minimization**: `GEO-INFER-ACT/src/geo_infer_act/core/free_energy.py` exposes `FreeEnergyBreakdown` and categorical `F = complexity - accuracy`
- **Bayesian Inference**: `GEO-INFER-BAYES/src/geo_infer_bayes/` (GP, MCMC, variational, model comparison)
- **Perception-Action Loops**: `GEO-INFER-ACT/src/geo_infer_act/core/active_inference.py` can return `ActiveInferenceStepResult`
- **Generative Models**: `GEO-INFER-ACT/src/geo_infer_act/core/generative_model.py`
- **Policy Selection**: `GEO-INFER-ACT/src/geo_infer_act/core/policy_selection.py` evaluates policies by expected free energy and returns `PolicyEvaluation`

### Testing Standards

| Standard | Requirement |
|----------|-------------|
| **Minimum coverage** | 4 test files per module |
| **Test types** | Unit, integration, performance, system |
| **Real assertions** | Tests check actual computed values, not just "no error" |
| **Cross-module** | Integration tests verify module interactions |
| **Unified runner** | `GEO-INFER-TEST/run_unified_tests.py` runs all 44 modules |

### Code Quality

| Rule | Rationale |
|------|-----------|
| **Type hints everywhere** | Full annotations on all parameters and return values |
| **PEP 8 lowercase packages** | `geo_infer_module` naming convention for all 44 modules |
| **Graceful degradation** | `try/except ImportError` for optional dependencies |
| **No marketing language** | Precise technical descriptions, no hyperbole |

## Quick Reference

### Running Tests

```bash
# All modules
uv run python GEO-INFER-TEST/run_unified_tests.py

# Single module
uv run python -m pytest GEO-INFER-MATH/tests/ -v

# By category
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration

# Contract checks
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_repo_contracts.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
```

### Key Entry Points

| What | Where |
|------|-------|
| **README** | `README.md` - Project overview, module index, architecture diagrams |
| **CLAUDE.md** | `CLAUDE.md` - Claude Code development guidance |
| **AGENTS.md** | `AGENTS.md` - Multi-agent systems architecture |
| **PAI.md** | This file - Development methodology |
| **ISA.md** | `ISA.md` - Ideal state criteria and verification targets |
| **Docs Hub** | `GEO-INFER-INTRA/docs/` - Central documentation |
| **Examples** | `GEO-INFER-EXAMPLES/examples/` - Working code samples |
| **Tests** | `GEO-INFER-TEST/run_unified_tests.py` - Unified test runner |

## Current State (2026-05-18)

| Metric | Value |
|--------|-------|
| Modules | 44 |
| Skill files validated | 45/45 |
| ACT focused tests | Passing |
| AGENT focused tests | Passing |
| BAYES focused tests | Passing after full-rank VI support |
| MATH convenience tests | Passing without Flask installed |
| SIM focused tests | Passing |
| Uppercase packages | 0 (all fixed) |
| Source-language debt | Reported by `validate_repo_contracts.py`; strict mode is available |

---

*GEO-INFER development is guided by the PAI Algorithm's core principle: capture ideal state as discrete, granular, binary, testable criteria, then hill-climb toward that ideal through systematic verification.*
