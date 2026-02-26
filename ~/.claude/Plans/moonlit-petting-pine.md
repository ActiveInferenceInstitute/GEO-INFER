# GEO-INFER Repo-Wide Audit: Documentation, Real Methods, Test Coverage

## Context

The GEO-INFER repo (44 modules, 860 source files, ~3,000+ tests) is at v0.2.0 (Beta).
The request is a comprehensive review ensuring:
1. All documentation is complete and **accurate** (examples use real class names)
2. All methods are **real** (no stubs/placeholders in src/)
3. All methods are **tested** (missing integration tests)
4. All methods are **configurable** (abstract base classes properly declared)

Exploration revealed concrete issues across Documentation, Tests, and Source Quality.

---

## Issues Found (Confirmed via Source Reading)

### A. Documentation — Incorrect Class Names in READMEs (CRITICAL)

**GEO-INFER-MATH/README.md** — 5 non-existent class names in code examples:
| README Shows | Real Class | File |
|---|---|---|
| `Optimizer()` (instantiated) | `ScipyOptimizer()` or `OptimizationManager()` | `core/optimization.py` |
| `GeometryEngine()` | Does not exist; use `Point`, `Polygon` from `core/geometry.py` | `core/geometry.py` |
| `MatrixOps()` | `MatrixOperations()` | `core/linalg_tensor.py` |
| `Interpolator()` | `IDWInterpolator()` or `KrigingInterpolator()` | `core/interpolation.py` |
| `FacilityOptimizer()` | `OptimizationManager()` | `core/optimization.py` |

**GEO-INFER-RISK/README.md** — 4 non-existent class names:
| README Shows | Real Class |
|---|---|
| `HazardAssessor()` | `EnhancedHazardModel()` |
| `VulnerabilityAnalyzer()` | `VulnerabilityModel()` or `EnhancedVulnerabilityModel()` |
| `RiskModeler()` | `RiskEngine()` |
| `MitigationPlanner()` | No direct equivalent — use `RiskEngine` with mitigation config |

**GEO-INFER-ECON/README.md** — 4 non-existent class names:
| README Shows | Real Class |
|---|---|
| `RegionalEconomist()` | `SpatialEconometricsEngine()` |
| `MarketAnalyzer()` | `MarketStructureAnalysis()` |
| `ImpactAnalyzer()` | `PolicyAnalysisEngine()` |
| `SiteSelector()` | `EconomicModelingEngine()` with location optimization |

### B. Documentation — Stats Inaccuracy (MEDIUM)

Root **README.md**, **CLAUDE.md**, **PAI.md** all claim "421 test files" — actual count is ~487.
Source file count shows 860 claimed vs ~864 actual.

**GEO-INFER-NORMS/src/geo_infer_norms.egg-info/PKG-INFO**:
- Python requirement says `>=3.8` but all project docs say `>=3.9`

### C. Tests — Missing Integration Tests (MEDIUM)

These 9 modules have no integration test directory/files at all:
`GEO-INFER-API`, `GEO-INFER-BIO`, `GEO-INFER-ENERGY`, `GEO-INFER-FOREST`,
`GEO-INFER-MARINE`, `GEO-INFER-NORMS`, `GEO-INFER-PEP`, `GEO-INFER-SEC`, `GEO-INFER-WATER`

### D. Tests — Modified Files Needing Verification (HIGH)

71 modified test files in git status need to be confirmed working. Known issues:
- `GEO-INFER-SPM/tests/unit/test_glm.py` line 56: `atol=0.1` tolerance may be too tight for regression with noise_std=0.1
- `GEO-INFER-ANT/tests/unit/test_algorithms.py` — algorithmic convergence issues
- `GEO-INFER-MATH/tests/unit/test_*.py` — 3 test files modified

### E. Source Quality — Abstract Base Classes (LOW-MEDIUM)

Missing `@abstractmethod` decorator on methods that use `raise NotImplementedError(...)` pattern:
- `GEO-INFER-DATA/src/geo_infer_data/core/ingestion.py`: `connect()`, `fetch_data()`
- `GEO-INFER-COMMS/src/geo_infer_comms/core/events.py`: `process_event()`
- `GEO-INFER-COMMS/src/geo_infer_comms/integrations/email_providers.py`: 3 methods
- `GEO-INFER-BAYES/src/geo_infer_bayes/core/inference.py`: backend init
- `GEO-INFER-RISK/src/geo_infer_risk/core/risk_models.py`: unknown count

Note: AG base.py `save()`/`load()` are intentionally optional (documented as default implementations).

---

## Execution Plan

### Track 1: Fix Documentation (MATH, RISK, ECON READMEs + stats)

**Files to modify:**
1. `GEO-INFER-MATH/README.md` — Replace 5 wrong class names with real ones
   - `Optimizer()` → `ScipyOptimizer()` (or `OptimizationManager()` for orchestration)
   - `GeometryEngine()` → Example using `Point`, `Polygon` primitives
   - `MatrixOps()` → `MatrixOperations()`
   - `Interpolator()` → `IDWInterpolator()` or `KrigingInterpolator()`
   - `FacilityOptimizer()` → `OptimizationManager()`
   - Verify all imports against `GEO-INFER-MATH/src/geo_infer_math/__init__.py`

2. `GEO-INFER-RISK/README.md` — Replace 4 wrong class names
   - `HazardAssessor()` → `EnhancedHazardModel()`
   - `VulnerabilityAnalyzer()` → `VulnerabilityModel()`
   - `RiskModeler()` → `RiskEngine()`
   - `MitigationPlanner()` → remove or show `RiskEngine` config-driven mitigation
   - Verify imports against `GEO-INFER-RISK/src/geo_infer_risk/__init__.py`

3. `GEO-INFER-ECON/README.md` — Replace 4 wrong class names
   - `RegionalEconomist()` → `SpatialEconometricsEngine()`
   - `MarketAnalyzer()` → `MarketStructureAnalysis()`
   - `ImpactAnalyzer()` → `PolicyAnalysisEngine()`
   - `SiteSelector()` → `EconomicModelingEngine()`
   - Verify imports against `GEO-INFER-ECON/src/geo_infer_econ/__init__.py`

4. `GEO-INFER-NORMS/src/geo_infer_norms.egg-info/PKG-INFO` — Change `>=3.8` to `>=3.9`

5. Root `README.md` + `CLAUDE.md` + `PAI.md` — Update test file count:
   - Run `find GEO-INFER-*/tests -name "test_*.py" | wc -l` to get actual count
   - Update "421 test files" stat to actual count

### Track 2: Fix Tests (SPM tolerance + verify modified test files)

**SPM test tolerance fix:**
- `GEO-INFER-SPM/tests/unit/test_glm.py` line 56: Change `atol=0.1` → `atol=0.3` (noise_std=0.1 → max error ~0.3 in predictions; OLS beta estimates should still be tight at `atol=0.1`)
  - Actually: line 56 is for beta coefficients, not predictions. The `atol=0.1` for beta estimates is tight but should work with seed(42). Keep unless failing.

**Verify modified SPM tests run clean:**
- Run `uv run python -m pytest GEO-INFER-SPM/tests/unit/test_glm.py -v` and fix any failures
- Run `uv run python -m pytest GEO-INFER-MATH/tests/ -v` for the 3 modified MATH tests
- Run `uv run python -m pytest GEO-INFER-ANT/tests/ -v` for ANT

**Add integration tests for 9 missing modules** (prioritized by importance):

High priority (Beta modules):
1. `GEO-INFER-BIO/tests/integration/test_bio_integration.py` — sequence analysis + visualization pipeline
2. `GEO-INFER-SEC/tests/integration/test_sec_integration.py` — anonymization + encryption pipeline
3. `GEO-INFER-NORMS/tests/integration/test_norms_integration.py` — normative inference + zoning

Medium priority (Alpha modules):
4. `GEO-INFER-API/tests/integration/test_api_integration.py` — endpoint integration
5. `GEO-INFER-ENERGY/tests/integration/test_energy_integration.py`
6. `GEO-INFER-FOREST/tests/integration/test_forest_integration.py`
7. `GEO-INFER-MARINE/tests/integration/test_marine_integration.py`
8. `GEO-INFER-WATER/tests/integration/test_water_integration.py`
9. `GEO-INFER-PEP/tests/integration/test_pep_integration.py`

Each integration test must:
- Test at least 2 classes working together (real data, no mocks)
- Cover the module's primary use case end-to-end
- Pass with `pytest -v` without external services

### Track 3: Source Quality (abstract method decorators)

**Files to modify:**

1. `GEO-INFER-DATA/src/geo_infer_data/core/ingestion.py`
   - Add `@abstractmethod` to `connect()` and `fetch_data()` methods in base class

2. `GEO-INFER-COMMS/src/geo_infer_comms/core/events.py`
   - Add `@abstractmethod` to `process_event()` in `EventProcessor`

3. `GEO-INFER-COMMS/src/geo_infer_comms/integrations/email_providers.py`
   - Add `@abstractmethod` to `send_email()`, `start_streaming()`, `stop_streaming()`

4. `GEO-INFER-BAYES/src/geo_infer_bayes/core/inference.py`
   - Add `@abstractmethod` where applicable (verify not already present)

5. `GEO-INFER-RISK/src/geo_infer_risk/core/risk_models.py`
   - Add `@abstractmethod` where applicable

---

## Execution Strategy

These 3 tracks are fully independent. Use parallel Engineer agents:
- **Agent 1**: Track 1 (Documentation fixes — 5 files)
- **Agent 2**: Track 2 (Test fixes — SPM + 3 module tests + 9 integration test files)
- **Agent 3**: Track 3 (Abstract method decorators — 5 source files)

Each agent should run their tests before declaring done.

---

## Verification

```bash
# After Track 1: Verify class names import correctly
python -c "from geo_infer_math import ScipyOptimizer, MatrixOperations, IDWInterpolator; print('MATH OK')"
python -c "from geo_infer_risk import EnhancedHazardModel, VulnerabilityModel, RiskEngine; print('RISK OK')"
python -c "from geo_infer_econ import SpatialEconometricsEngine, MarketStructureAnalysis, PolicyAnalysisEngine; print('ECON OK')"

# After Track 2: Run affected module tests
uv run python -m pytest GEO-INFER-SPM/tests/unit/test_glm.py -v
uv run python -m pytest GEO-INFER-MATH/tests/unit/ -v
uv run python -m pytest GEO-INFER-ANT/tests/ -v
# Verify new integration tests run
uv run python -m pytest GEO-INFER-BIO/tests/integration/ -v
uv run python -m pytest GEO-INFER-SEC/tests/integration/ -v
uv run python -m pytest GEO-INFER-NORMS/tests/integration/ -v

# After Track 3: Verify abstract classes still work (subclasses still instantiable)
uv run python -m pytest GEO-INFER-DATA/tests/ -v
uv run python -m pytest GEO-INFER-COMMS/tests/ -v
uv run python -m pytest GEO-INFER-BAYES/tests/ -v

# Full suite sanity check
uv run python GEO-INFER-TEST/run_unified_tests.py 2>&1 | tail -30

# Verify no placeholder grep regressions
grep -rn "placeholder\|stub\|fake" --include="*.py" GEO-INFER-*/src/ | \
  grep -v "abstractmethod\|__pycache__\|SQL\|HTML\|input\|fallback\|docstring" | wc -l
```

---

## Critical Files

| File | Track | Issue |
|---|---|---|
| `GEO-INFER-MATH/README.md` | Doc | 5 wrong class names |
| `GEO-INFER-RISK/README.md` | Doc | 4 wrong class names |
| `GEO-INFER-ECON/README.md` | Doc | 4 wrong class names |
| `GEO-INFER-NORMS/src/geo_infer_norms.egg-info/PKG-INFO` | Doc | Python >=3.8 vs >=3.9 |
| Root `README.md` / `CLAUDE.md` / `PAI.md` | Doc | Test file count stale |
| `GEO-INFER-SPM/tests/unit/test_glm.py` | Test | May need tolerance fix |
| `GEO-INFER-{BIO,SEC,NORMS,...}/tests/integration/` | Test | 9 new files needed |
| `GEO-INFER-DATA/src/geo_infer_data/core/ingestion.py` | Quality | @abstractmethod |
| `GEO-INFER-COMMS/src/geo_infer_comms/core/events.py` | Quality | @abstractmethod |
| `GEO-INFER-COMMS/src/geo_infer_comms/integrations/email_providers.py` | Quality | @abstractmethod |
