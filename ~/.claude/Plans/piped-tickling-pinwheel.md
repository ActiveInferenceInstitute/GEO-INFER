# Plan: Audit and Improve CLAUDE.md + All Module Docs

**Created**: 2026-02-24
**Scope**: CLAUDE.md + GEO-INFER-INTRA/docs/modules/ (45 module docs + index.md)
**Effort**: Extended

---

## Context

The GEO-INFER documentation has drifted from reality. CLAUDE.md contains stale statistics (wrong module count, wrong file counts). 45 module documentation files in `GEO-INFER-INTRA/docs/modules/` have varying quality — the infrastructure/analytics modules (MATH, SPACE, BAYES, AI, API, etc.) are excellent (4-5/5), while many domain-specific and utility modules have stale references, incorrect import examples, missing sections, and inconsistent formatting.

The goal is to make every document factually accurate and structurally complete, so developers can rely on them without cross-checking the source code.

---

## Ground-Truth Data (Verified 2026-02-24)

| Claim in CLAUDE.md | Actual | Action |
|--------------------|--------|--------|
| "44 modules" | **45 modules** | Fix |
| "858 source files" | **903 source files** | Fix |
| "(294,403 lines)" | **(307,831 lines)** | Fix |
| "416 test files" | **381 test files** | Fix |
| "(86,793 lines)" | **(73,221 lines)** | Fix |
| TRANSPORT missing from categories | exists in repo | Add |
| TRANSPORT status "In Development" (index.md) | fully implemented | Fix |

> **Note**: At execution time, recompute file counts fresh with `find` commands to confirm — these were measured on 2026-02-24.

---

## Plan

### Phase 1: CLAUDE.md — Factual Corrections

**File**: `/Users/4d/Documents/GitHub/GEO-INFER/CLAUDE.md`

**Changes** (all surgical, exact string replacements):

1. `"44 modules"` → `"45 modules"`
2. `"858 source files"` → `"903 source files"`
3. `"(294,403 lines)"` → `"(307,831 lines)"`
4. `"416 test files"` → `"381 test files"`
5. `"(86,793 lines)"` → `"(73,221 lines)"`
6. Add `GEO-INFER-TRANSPORT` to Module Categories section (under **Operations** alongside GIT, TEST, EXAMPLES, PLACE or new **Transportation** subcategory)
7. Update the Data Flow diagram/text to acknowledge TRANSPORT module
8. Verify `"~3,000+ tests"` claim — recount at execution time

**Module Category addition** (TRANSPORT belongs in Operations or new category):
```
- **Transportation**: TRANSPORT
```
Or append to Operations:
```
- **Operations**: OPS, INTRA, GIT, TEST, EXAMPLES, PLACE, TRANSPORT
```
→ Read the actual categories section at execution to determine best placement.

---

### Phase 2: docs/modules/index.md — Status and Count Fix

**File**: `/Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-INTRA/docs/modules/index.md`

**Changes**:
1. Update TRANSPORT status from `"🔄 In Development"` → `"✅ Active"` (module has full src implementation + tests)
2. Verify total module count listed is 45
3. Check if any other modules are marked with stale status

---

### Phase 3: Stale Module Reference Fixes

These docs reference modules that **do not exist** in the 45-module framework. Fix by replacing with actual equivalent modules.

| Doc | Stale Reference | Replacement |
|-----|-----------------|-------------|
| `geo-infer-ag.md` | `OPTIMIZATION` module | Remove or replace with `MATH` / `ACT` |
| `geo-infer-ag.md` | `WATER` integration | Keep — WATER exists |
| `geo-infer-ant.md` | `OPTIMIZATION` module | Remove or replace with `MATH` |
| `geo-infer-bio.md` | `WATER` integration | Keep — WATER exists |
| `geo-infer-bio.md` | `OCEAN` module | Remove — does not exist; replace with `MARINE` |
| `geo-infer-cog.md` | Undefined integration modules | Audit and fix at execution |
| `geo-infer-econ.md` | Undefined modules | Audit and fix at execution |

**Approach**: Read each file, identify the exact stale reference, replace with correct module name or remove if no equivalent.

---

### Phase 4: Missing "Related Documentation" Sections

The environmental domain modules (FOREST, MARINE, ENERGY, WATER, CLIMATE) have good core content but are missing the "Related Documentation" section that the infrastructure modules all have.

**Template structure** (from geo-infer-space.md pattern):
```markdown
## Related Documentation

- [GEO-INFER-INTRA](geo-infer-intra.md) - Central documentation hub
- [GEO-INFER-ACT](geo-infer-act.md) - Active inference integration
- [GEO-INFER-SPACE](geo-infer-space.md) - Spatial operations
- [Module-specific dependencies...]

### Tutorials
- Getting Started with GEO-INFER-[MODULE]
- Integration with Active Inference

### How-To Guides
- Setting up [MODULE] for [use case]
- Configuring [MODULE] with [dependency]

### Technical Reference
- [API documentation link]
- [Configuration reference]
```

**Files to update**:
- `geo-infer-forest.md`
- `geo-infer-marine.md`
- `geo-infer-energy.md`
- `geo-infer-water.md`
- `geo-infer-climate.md`

---

### Phase 5: Package Import Accuracy Fixes (Lower-Quality Docs)

Many domain/utility module docs use class names without proper import paths, or reference internal classes in ways that don't match the actual `__init__.py` exports.

**Strategy**: For each affected module, read the actual `src/geo_infer_*/  __init__.py` and verify that code examples use classes that are actually exported.

**Modules requiring import audit** (from exploration findings — ~22 files):
- geo-infer-ag.md → check against `GEO-INFER-AG/src/geo_infer_ag/__init__.py`
- geo-infer-ant.md → check against `GEO-INFER-ANT/src/geo_infer_ant/__init__.py`
- geo-infer-bio.md → check against `GEO-INFER-BIO/src/geo_infer_bio/__init__.py`
- geo-infer-civ.md → check against `GEO-INFER-CIV/src/geo_infer_civ/__init__.py`
- geo-infer-cog.md → check against `GEO-INFER-COG/src/geo_infer_cog/__init__.py`
- geo-infer-comms.md → check against `GEO-INFER-COMMS/src/geo_infer_comms/__init__.py`
- geo-infer-econ.md → check against `GEO-INFER-ECON/src/geo_infer_econ/__init__.py`
- geo-infer-risk.md → check against `GEO-INFER-RISK/src/geo_infer_risk/__init__.py`
- geo-infer-sim.md → check against `GEO-INFER-SIM/src/geo_infer_sim/__init__.py`
- geo-infer-spm.md → check against `GEO-INFER-SPM/src/geo_infer_spm/__init__.py`
- geo-infer-log.md → check against `GEO-INFER-LOG/src/geo_infer_log/__init__.py`
- geo-infer-metagov.md → check against `GEO-INFER-METAGOV/src/geo_infer_metagov/__init__.py`
- geo-infer-norms.md → check against `GEO-INFER-NORMS/src/geo_infer_norms/__init__.py`
- geo-infer-org.md → check against `GEO-INFER-ORG/src/geo_infer_org/__init__.py`
- geo-infer-pep.md → check against `GEO-INFER-PEP/src/geo_infer_pep/__init__.py`
- geo-infer-place.md → check against `GEO-INFER-PLACE/src/geo_infer_place/__init__.py`
- geo-infer-req.md → check against `GEO-INFER-REQ/src/geo_infer_req/__init__.py`
- geo-infer-app.md → check against `GEO-INFER-APP/src/geo_infer_app/__init__.py`
- geo-infer-art.md → check against `GEO-INFER-ART/src/geo_infer_art/__init__.py`
- geo-infer-git.md → check against `GEO-INFER-GIT/src/geo_infer_git/__init__.py`
- geo-infer-intra.md → check against `GEO-INFER-INTRA/src/geo_infer_intra/__init__.py`
- geo-infer-test.md → check against `GEO-INFER-TEST/src/geo_infer_test/__init__.py`

**For each**: Read `__init__.py`, identify the exported classes/functions in `__all__`, then check if the doc's code examples use correct import paths and class names. Fix mismatches.

---

### Phase 6: Structural Consistency Improvements

**Emoji removal** from professional documentation files that use them inconsistently:
- geo-infer-ant.md (🎯, 📚, etc.)
- geo-infer-bio.md (🎯, 📚, 🔗, 🚨, 📊)
- Other docs identified during execution

**Exception**: Do NOT remove emojis from docs that use them consistently in a structured way (section icons) — only remove scattered/decorative emojis.

**YAML frontmatter**: Some docs (e.g., geo-infer-civ.md, geo-infer-health.md) have YAML frontmatter, others don't. Do NOT add YAML frontmatter to docs that don't have it — this would be a large cosmetic change without clear benefit. Only fix the content.

**Status markers**: geo-infer-civ.md is marked "Planning" (2025-01-19) — check actual implementation status and update if the module is now active.

---

### Phase 7: TRANSPORT Module Doc Accuracy

**File**: `geo-infer-transport.md`

Verify the doc matches actual implementation:
- Classes in doc: `TrafficAnalyzer`, `RouteOptimizer`, `DemandForecaster`, `NetworkModeler`, `InfrastructurePlanner`
- Actual exports from `__init__.py`: `TransportNetwork`, `RoutingEngine`, `TrafficAnalyzer`, `AccessibilityAnalyzer`, `TransitOptimizer`
- **Mismatch detected**: Doc uses `RouteOptimizer`/`DemandForecaster`/`NetworkModeler`/`InfrastructurePlanner` but `__init__.py` exports `RoutingEngine`/`AccessibilityAnalyzer`/`TransitOptimizer`/`TransportNetwork`
- Fix the doc's API Reference and code examples to match actual exports

Also fix version inconsistency in TRANSPORT:
- `pyproject.toml`: version = "0.2.0"
- `__init__.py`: `__version__ = "0.1.0"`
- → Update `__init__.py` to match `pyproject.toml` (0.2.0)

---

## Execution Strategy

**Sequential execution** — docs are independent so this can be parallelized across multiple Engineer agents, but given complexity, use this order:

1. **CLAUDE.md** — highest visibility, factual fixes (5 min)
2. **index.md** — status and count fixes (2 min)
3. **TRANSPORT doc + __init__.py** — API mismatch fix (5 min)
4. **Stale reference fixes** (AG, ANT, BIO, COG, ECON) — read each, targeted fixes (10 min)
5. **Missing Related Documentation sections** (FOREST, MARINE, ENERGY, WATER, CLIMATE) — add standard section to each (10 min)
6. **Import accuracy audit** (22 files) — read __init__.py → verify/fix doc examples (20 min, parallelize 4-5 at a time)
7. **Emoji/formatting cleanup** (identified files) — spot fixes (5 min)

**Parallel tracks** for Phase 6:
- Track A: ag, ant, bio, cog, comms
- Track B: econ, risk, sim, spm, log
- Track C: metagov, norms, org, pep, place
- Track D: req, app, art, git, intra, test

---

## Critical Files to Modify

| File | Type | Changes |
|------|------|---------|
| `CLAUDE.md` | Project root | Stats, module count, categories |
| `GEO-INFER-INTRA/docs/modules/index.md` | Doc index | TRANSPORT status, counts |
| `GEO-INFER-INTRA/docs/modules/geo-infer-transport.md` | Module doc | API names mismatch |
| `GEO-INFER-TRANSPORT/src/geo_infer_transport/__init__.py` | Source | Version 0.1.0 → 0.2.0 |
| `GEO-INFER-INTRA/docs/modules/geo-infer-ag.md` | Module doc | Stale OPTIMIZATION ref |
| `GEO-INFER-INTRA/docs/modules/geo-infer-ant.md` | Module doc | Stale OPTIMIZATION ref, emojis |
| `GEO-INFER-INTRA/docs/modules/geo-infer-bio.md` | Module doc | Stale OCEAN ref, emojis |
| `GEO-INFER-INTRA/docs/modules/geo-infer-forest.md` | Module doc | Add Related Documentation |
| `GEO-INFER-INTRA/docs/modules/geo-infer-marine.md` | Module doc | Add Related Documentation |
| `GEO-INFER-INTRA/docs/modules/geo-infer-energy.md` | Module doc | Add Related Documentation |
| `GEO-INFER-INTRA/docs/modules/geo-infer-water.md` | Module doc | Add Related Documentation |
| `GEO-INFER-INTRA/docs/modules/geo-infer-climate.md` | Module doc | Add Related Documentation |
| 22 lower-quality module docs | Module docs | Import path verification + fixes |

---

## Verification Strategy

After all changes:

1. **Count check**: Run `find /Users/4d/Documents/GitHub/GEO-INFER -path "*/src/*.py" -not -path "*/test*" | wc -l` and confirm matches CLAUDE.md
2. **Module count check**: `ls -d /Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-* | wc -l` = 45
3. **Grep check**: `grep "44 modules" CLAUDE.md` returns no results (all 44→45 fixed)
4. **Stale ref check**: `grep -r "OPTIMIZATION\|OCEAN" GEO-INFER-INTRA/docs/modules/` returns no results
5. **TRANSPORT doc**: Classes in doc match `__init__.py` `__all__` list
6. **Related Documentation**: All 5 environmental module docs have "## Related Documentation" section

---

## ISC (Ideal State Criteria)

- ISC-C1: CLAUDE.md module count accurately reflects 45 existing modules
- ISC-C2: CLAUDE.md source file and line counts match repository ground truth
- ISC-C3: CLAUDE.md test file and line counts match repository ground truth
- ISC-C4: TRANSPORT module present in CLAUDE.md module categories section
- ISC-C5: index.md TRANSPORT entry shows active/complete status correctly
- ISC-C6: All module doc references to non-existent modules removed or corrected
- ISC-C7: geo-infer-transport.md API classes match actual module exports
- ISC-C8: GEO-INFER-TRANSPORT version consistent across pyproject.toml and __init__.py
- ISC-C9: All five environmental modules have complete Related Documentation section
- ISC-C10: All module docs reference only modules that exist in the 45-module framework
- ISC-C11: Import examples in module docs match actual __init__.py exports
- ISC-A1: No doc references OPTIMIZATION or OCEAN as standalone modules
- ISC-A2: CLAUDE.md stats not updated to incorrect values
- ISC-A3: High-quality docs (4-5/5) not regressed by unnecessary changes
