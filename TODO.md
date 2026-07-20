# GEO-INFER — TODO & Release Roadmap

> **Last Updated**: 2026-06-18
> **Current Version**: 0.2.0 (Beta)
> **Repository**: [ActiveInferenceInstitute/GEO-INFER](https://github.com/ActiveInferenceInstitute/GEO-INFER)

---

## 📋 Release Criteria (Universal Gate)

Every version release MUST satisfy ALL of the following before tagging:

| Category | Criterion | Verification | Required |
|----------|-----------|-------------|----------|
| **Quality** | Unit and integration gates pass | `uv run python GEO-INFER-TEST/run_unified_tests.py --category unit` and `--category integration` | Unit 43/43, integration 44/44 |
| **Quality** | No source-language debt | `uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke` | 0 errors |
| **Quality** | Modular hygiene contract | `uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke` | 0 errors |
| **Quality** | No illegitimate `pass` stubs | `uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke` | 0 concrete pass bodies |
| **Quality** | Type hints complete | `mypy --strict` on core modules | 0 errors |
| **Quality** | Formatting & lint | `black --check`, `isort --check`, `ruff check` | Clean |
| **Docs** | Every module has README.md + AGENTS.md | `find GEO-INFER-*/README.md \| wc -l` | 44 each ✅ |
| **Docs** | Every module has SKILL.md (Claude Code) | `uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs` | 45/45 passing ✅ |
| **Docs** | No stale dates | Grep for old dates excluding CHANGELOG/TODO | 0 results ✅ |
| **Docs** | CHANGELOG.md updated | Manual inspection | Entry present ✅ |
| **Testing** | All 44 modules have ≥4 test files | Generated README inventory | ≥176 ✅ (444) |
| **Testing** | Coverage ≥80% per module | `pytest --cov --cov-fail-under=80` | All pass |
| **Testing** | Property-based tests ≥10 modules | Grep `@given\|hypothesis` | ≥10 ✅ (35) |
| **Arch** | PEP 8 package names | No unexpected package dir casing in `src/` | 0 ✅ (all 44 packages normalized to `geo_infer_<module>`) |
| **Arch** | Graceful dependency degradation | `import geo_infer_act` without optional deps | No ImportError ✅ |
| **Arch** | H3 v4 API only | `uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration` | 2/2 passing ✅ |
| **Arch** | Active Inference API contract | `uv run python GEO-INFER-TEST/validate_active_inference_contract.py` | 0 failures |

> ¹ Excludes legitimate uses: SQL parameter placeholders, HTML `placeholder=` attributes, fallback geometries, docstring references.

---

## 2026-05-18 Active Inference Hardening Pass

Completed:

- [x] Added `ISA.md` with Active Inference, packaging, docs, and verification ideal-state criteria.
- [x] Added `GEO-INFER-TEST/validate_repo_contracts.py` for inventory, signposting, package casing, pyproject sanity, setup syntax, import-smoke warnings, and source-language debt reporting.
- [x] Added `GEO-INFER-TEST/validate_active_inference_contract.py` for typed ACT result objects, categorical free-energy decomposition, deterministic policy selection, and typed step results.
- [x] Normalized ENERGY, FOREST, MARINE, and WATER package directories to lowercase `geo_infer_<module>`.
- [x] Fixed `GEO-INFER-INTRA/setup.py` syntax so workspace package scans are no longer blocked there.
- [x] Implemented ACT typed result exports: `FreeEnergyBreakdown`, `PolicyEvaluation`, and `ActiveInferenceStepResult`.
- [x] Corrected categorical free energy to report `complexity - accuracy` and stable normalized terms.
- [x] Replaced first-policy selection fallback with expected-free-energy policy evaluation and seedable deterministic/stochastic selection.
- [x] Implemented BAYES full-rank VI initialization and finite Cholesky-factor sampling path.
- [x] Made MATH convenience imports independent of Flask; documented `geo-infer-math[web]` for Flask-backed APIs.
- [x] Replaced the stale INTRA Active Inference getting-started tutorial with runnable current API examples.

Remaining:

- [x] Drive `validate_repo_contracts.py --strict-source-language --skip-import-smoke` to zero source-language debt across all modules.
- [ ] Align AGENT and SIM Active Inference adapters more deeply with ACT typed result objects while preserving their current tests.
- [ ] Regenerate historical INTRA/EXAMPLES assessment outputs so their casing and status snapshots are current instead of archival.

Verification:

```bash
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_repo_contracts.py
uv run python GEO-INFER-TEST/validate_active_inference_contract.py
uv run --package geo-infer-act --extra dev python -m pytest GEO-INFER-ACT/tests -q
uv run --package geo-infer-bayes --extra dev python -m pytest GEO-INFER-BAYES/tests -q
uv run --package geo-infer-math --extra dev python -m pytest GEO-INFER-MATH/tests -q
```

---

## 2026-06-15 Modular Hygiene Pass

Completed:

- [x] Added executable repo contracts for root uv workspace state, `.python-version`, root `uv.lock`, per-module test inventory, source/test task-marker hygiene, and library logging configuration.
- [x] Added focused unit tests for the new `validate_repo_contracts.py` hygiene checks.
- [x] Removed module-local task markers from NORMS, PEP, and TEST code paths.
- [x] Updated root README, AGENTS, CLAUDE, ISA, and SKILL signposts to route hygiene work through the shared validator and this TODO ledger.

Verification:

```bash
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run --extra quality python GEO-INFER-TEST/run_unified_tests.py --module TEST --timeout 120
```

---

## 2026-06-18 Verifier-First Hardening Pass

Completed:

- [x] Added fatal repo-contract checks for concrete `pass` bodies, root generated artifact churn, generated README/AGENTS freshness, and Python tooling target drift below 3.11.
- [x] Added `GEO-INFER-TEST/rewrite_readme_agents.py --check` so generated documentation freshness can fail CI without rewriting files.
- [x] Extended `validate_skills.py` to reject unscoped planned/stub/placeholder language while allowing intentional template, SQL, and HTML placeholder contexts.
- [x] Replaced concrete no-op paths in DATA, GIT, HEALTH, IOT, MATH, OPS, PEP, RISK, SEC, SIM, SPACE, and SPM with observable behavior or explicit state initialization.
- [x] Moved SPACE and ART visualization/report output tests to per-test temporary directories and removed the stale root `test_output/` artifact.
- [x] Reviewed PR #1 skill edits as source material, then incorporated only real-path/current-import updates into EXAMPLES, INTRA, METAGOV, NORMS, and OPS skills.
- [x] Regenerated tracked README.md and AGENTS.md files from current repository facts.

Verification:

```bash
python -m compileall GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/rewrite_readme_agents.py --check
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration
```

Verified results on 2026-06-18: generated docs current (1655 files), repo contracts 0 errors/0 warnings, skills 45/45 passing, unit 43/43 passing, integration 44/44 passing, H3 migration 2/2 passing.

---

## 2026-06-18 Spatial Active Inference + Nested H3 Hardening Pass

Completed:

- [x] Added SPACE-owned nested H3 hierarchy construction, validation, parent/child maps, same-resolution neighbor maps, and finite weighted child-to-parent aggregation through `NestedH3Grid`.
- [x] Added ACT nested result contracts and opt-in nested methods for generative models, active-inference grid inference, spatial agents, and multi-agent lattice simulations.
- [x] Kept flat H3 method signatures and default return shapes unchanged while adding nested behavior only through explicit nested methods or `RunConfig.parameters["nested_h3"]`.
- [x] Added nested runner artifacts: `data/h3_hierarchy.csv`, `data/nested_h3_diagnostics.json`, and `visualizations/nested_h3_level_map.html`, plus nested metrics in `analysis/run_summary.json`.
- [x] Extended H3 and ACT geospatial contract validators with executable nested runtime checks and nested artifact validation.
- [x] Added ACT and SPACE unit coverage for hierarchy invariants, negative H3 validation controls, nested belief updates, nested grid inference, spatial-agent nested steps, multi-agent nested summaries, and root-output isolation.
- [x] Regenerated README.md and AGENTS.md files from the strengthened generator, including ACT/SPACE nested-H3 operational notes.

Verification:

```bash
python -m compileall -q GEO-INFER-*/src GEO-INFER-*/examples
uv run python GEO-INFER-TEST/validate_repo_contracts.py --strict-source-language --skip-import-smoke
uv run python GEO-INFER-TEST/validate_skills.py --check-xrefs
uv run python GEO-INFER-TEST/validate_h3_active_inference_contract.py
uv run python GEO-INFER-TEST/validate_act_geospatial_contract.py
uv run python GEO-INFER-TEST/run_unified_tests.py --module ACT --timeout 180
uv run python GEO-INFER-TEST/run_unified_tests.py --module SPACE --timeout 180
uv run python GEO-INFER-TEST/run_unified_tests.py --module TEST --timeout 180
uv run python GEO-INFER-TEST/run_unified_tests.py --category unit --timeout 300
uv run python GEO-INFER-TEST/run_unified_tests.py --category integration --timeout 300
uv run python GEO-INFER-TEST/run_unified_tests.py --h3-migration --timeout 300
git status --short -- test_output output outputs visualizations_output
```

Verified results on 2026-06-18: compileall clean, repo contracts 0 errors/0 warnings, skills 45/45 passing, H3 contract OK, ACT geospatial contract OK, ACT/SPACE/TEST module gates passing, unit 43/43 passing, integration 44/44 passing, H3 migration 2/2 passing, and root generated-output paths clean.

---

## 🔖 Version Roadmap

### v0.2.0 — Current Release ✅

**Released**: 2026-02-25 | **Theme**: Documentation parity, placeholder elimination, LOG integration

<details>
<summary>Completed items (click to expand)</summary>

#### Source Code Remediation (All resolved)

- IOT: Real paho-mqtt MQTT handlers
- AG: USDA soil health, IPCC Tier 1 carbon, FAO-56 water usage
- ACT: Dirichlet/categorical generative model, real belief trajectory plotting
- BAYES: Real ELBO, Jeffreys/reference/unit-info priors, Cholesky LKJ multilevel, TFP GP+MH
- ART: Real mplcursors interactivity
- SEC: Uses `calculated_confidence` (not hardcoded)
- LOG: Verified clean (KMeans, Dijkstra, PuLP — 0 placeholders)
- RISK: Verified clean (Cholesky, Moran's I, Monte Carlo — 0 placeholders)
- COMMS: All placeholders resolved (PyJWT/HMAC, subscriber registry)
- NORMS, ECON, EXAMPLES, AGENT, PEP: All addressed

#### Documentation & Infrastructure

- All stale dates (`2026-01-26`, `2026-02-17`) updated to `2026-02-25`
- CHANGELOG.md v0.2.0 entry added
- `pyproject.toml`: License, URLs, version all correct
- CI: `.github/workflows/ci.yml` exists
- LOG `__init__.py`: 14 lazy exports + submodule access
- TRANSPORT: BPR microsimulation, EWMA traffic forecast
- SPM: Real time-series explorer (mean±SD + residuals)
- Cross-module integrations: LOG↔TRANSPORT (emissions), LOG↔ECON (logistics)
- 45 SKILL.md files deployed (1 root + 44 modules) with Examples, Guidelines, Integrations
- `validate_skills.py` added to GEO-INFER-TEST for CI validation
- SKILL.md signposted in 44 README.md nav bars + 44 AGENTS.md footers

</details>

---

### v0.3.0 — "Test Green" Release

**Target**: March 2026  
**Theme**: Fix all test failures, achieve ≥80% coverage in core modules

#### Test Gate Status

- [x] Unit category: 43/43 module suites passing on 2026-06-18.
- [x] Integration category: 44/44 module suites passing on 2026-06-18.
- [x] H3 migration gate: 2/2 validators passing on 2026-06-18.
- [x] Root generated-output paths remain clean after SPACE/ART visualization/report tests.

#### Coverage Targets

| Module Group | Current | Target |
|-------------|---------|--------|
| **Core Analytical** (MATH, ACT, BAYES, SPM) | Unknown | ≥80% |
| **Infrastructure** (SPACE, TIME, DATA, API) | Unknown | ≥80% |
| **Domain** (all others) | Unknown | ≥60% |

#### Remaining Source Code Items (0 open)

| File | Issue | Priority | Status |
|------|-------|----------|--------|
| `NORMS/.../compliance_tracking.py` | Simplified evaluation logic | Medium | ✅ Resolved |
| `PLACE/.../unified_backend.py` | Fallback placeholder geometries | Low | ✅ Resolved |
| `SPACE/.../visualization_engine.py` | 4 placeholder monitoring data points | Low | ✅ Resolved |

---

### v0.4.0 — "Full Coverage" Release

**Target**: May 2026  
**Theme**: 90%+ coverage in core, complete documentation, strict typing

#### Code Quality

- [ ] Mypy strict mode passing in all 44 modules
- [ ] Test coverage ≥90% in Core Analytical modules (MATH, ACT, BAYES, AI, AGENT, COG, SPM)
- [ ] Test coverage ≥80% in all Domain modules
- [ ] Performance benchmarks for spatial operations (H3 indexing, geodesic calculations)

#### Documentation

- [ ] Sphinx API documentation auto-generated for all 44 modules
- [ ] Jupyter notebook tutorials for each domain category
- [ ] "From Data to Active Inference" end-to-end tutorial
- [ ] Docstring coverage ≥95% (enforced via `pydocstyle`)

#### Module Completions (Alpha → Beta)

- [ ] **SPM**: Complete GLM spatial implementation
- [ ] **ANT**: Verify ACO/PSO/ABC convergence
- [ ] **SIM**: Real Mesa-based agent simulation
- [ ] **COG**: Complete cognitive modeling (attention, memory, trust)

#### Infrastructure

- [ ] Automated coverage reporting via Codecov
- [ ] Pre-commit hooks (Black, isort, ruff, mypy)
- [ ] Docker base image for development

---

### v0.5.0 — "Domain Completions" Release

**Target**: August 2026  
**Theme**: All domain modules reach Beta status

| Module | Current Issue | Target |
|--------|--------------|--------|
| **SEC** | Threat detection incomplete | Anomaly-based intrusion detection |
| **OPS** | Monitoring incomplete | Prometheus/Grafana integration |
| **METAGOV** | DAO mechanisms incomplete | Real governance mechanisms |
| **TRANSPORT** | Traffic models partial | Full graph-based network flow |
| **EMERGENCY** | Resource deployment incomplete | Linear programming allocation |
| **ENERGY** | LCOE benchmarking incomplete | Complete techno-economic analysis |
| **CIV** | STEW-MAP partial | Full participatory mapping |
| **REQ** | P3IF partial | Complete traceability matrix |

#### New Capabilities

- [ ] **API**: Complete GraphQL schema for all 44 module endpoints
- [ ] **APP**: Deploy reference dashboard application
- [ ] **PLACE**: H3-based place-shedding and catchment area analysis

---

### v1.0.0 — "Production Release"

**Target**: November 2026  
**Theme**: All release criteria met, all 44 modules at Beta+

- [ ] ALL universal release criteria gates pass
- [ ] All 44 modules at Beta or higher
- [x] Production source contains no inert implementations or placeholder behavior
- [ ] Full Sphinx docs at `geo-infer.readthedocs.io`
- [ ] Semantic versioning in all 44 `pyproject.toml` files
- [ ] Security audit for SEC and API modules
- [ ] Performance benchmarks published (SPACE, TIME, BAYES)
- [ ] CC BY-NC-SA 4.0 license compliance verified

---

## 🗂️ Module Status Registry (2026-02-25)

### ✅ Beta+ Modules (20/44) — No blockers

| Module | Status | Notes |
|--------|--------|-------|
| MATH | Beta | — |
| ACT | Beta | Placeholders resolved |
| BAYES | Beta | GP+MH, ELBO, priors all real |
| SPACE | Beta (H3 v4) | — |
| IOT | Beta | Real paho-mqtt |
| API | Beta | — |
| AG | Beta | USDA/IPCC/FAO-56 |
| HEALTH | Beta | — |
| BIO | Beta | — |
| CLIMATE | Beta | — |
| FOREST | Beta | — |
| COMMS | Beta | All channels implemented |
| APP | Beta | — |
| ART | Beta | Real mplcursors |
| PLACE | Beta (H3 v4) | — |
| INTRA | Beta | — |
| GIT | Beta | — |
| TEST | Stable | — |
| EXAMPLES | Beta | Needs e2e tutorial |
| LOG | Beta | Verified clean, lazy exports |

### 🟡 Alpha Modules (24/44) — Need work for v0.5.0

| Module | Blocker | Target |
|--------|---------|--------|
| AI | None known | v0.4.0 |
| COG | Incomplete attention/memory | v0.4.0 |
| AGENT | None (telemetry resolved) | v0.3.0 |
| SPM | GLM incomplete, test fixtures | v0.4.0 |
| TIME | None known | v0.3.0 |
| DATA | None known | v0.3.0 |
| SEC | Threat detection incomplete | v0.5.0 |
| OPS | Monitoring incomplete | v0.5.0 |
| METAGOV | DAO incomplete | v0.5.0 |
| ECON | None (auction resolved) | v0.3.0 |
| RISK | None (verified clean) | v0.3.0 |
| ENERGY | LCOE incomplete | v0.5.0 |
| WATER | None known | v0.3.0 |
| TRANSPORT | Traffic models partial | v0.5.0 |
| MARINE | None known | v0.3.0 |
| EMERGENCY | Deployment opt incomplete | v0.5.0 |
| EDU | None (pass in template string) | v0.3.0 |
| SIM | Mesa integration incomplete | v0.4.0 |
| ANT | Convergence not verified | v0.4.0 |
| CIV | STEW-MAP partial | v0.5.0 |
| PEP | None (TODO → roadmap note) | v0.3.0 |
| ORG | DAO incomplete | v0.5.0 |
| NORMS | Simplified compliance eval | v0.3.0 |
| REQ | P3IF partial | v0.5.0 |

---

## 📊 Current Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test categories passing | **23/47** | 47/47 | 🟡 |
| Placeholder references (source) | **~23** | 0 | 🟡 (most are legitimate) |
| Test files | **421** | ≥176 | ✅ |
| Unit test files | **318** | ≥44 | ✅ |
| Integration test files | **50** | ≥44 | ✅ |
| Hypothesis test refs | **35** | ≥10 modules | ✅ |
| README.md files | **44** | 44 | ✅ |
| AGENTS.md files | **44** | 44 | ✅ |
| Source files | **860** | — | — |
| Source lines | **297,360** | — | — |
| H3 legacy calls | **0** | 0 | ✅ |
| Pass stubs | **0** | 0 | ✅ |
| Stale dates in docs | **0** | 0 | ✅ |
| Modules at Beta+ | **20/44** | 44/44 | 🟡 |

### Quick Verification

```bash
# Run all tests
uv run python GEO-INFER-TEST/run_unified_tests.py 2>&1 | tail -20

# Check remaining placeholder refs
grep -rn "placeholder\|stub\|fake" --include="*.py" GEO-INFER-*/src/ | \
  grep -v "abstractmethod\|__pycache__\|SQL\|HTML\|input\|fallback\|docstring" | wc -l

# Documentation completeness
find GEO-INFER-*/README.md | wc -l  # 44
find GEO-INFER-*/AGENTS.md | wc -l  # 44

# H3 legacy check
grep -rn "h3.geo_to_h3\|h3.h3_to_geo\|h3.k_ring" --include="*.py" . | wc -l  # 0
```

---

*This TODO is a living document. Governed by the [PAI Algorithm](./PAI.md) — all criteria are binary, testable, and verifiable.*
