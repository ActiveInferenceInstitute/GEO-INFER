---
prd: true
id: PRD-20260225-geo-infer-docs-audit
status: PLANNED
mode: interactive
effort_level: Comprehensive
created: 2026-02-25
updated: 2026-02-25
iteration: 0
maxIterations: 128
loopStatus: null
last_phase: PLAN
failing_criteria: []
verification_summary: "0/44"
parent: null
children: []
---

# GEO-INFER Comprehensive Documentation Audit & Remediation

> Systematic audit and correction of all 44-module documentation — fixing fictional API
> examples, stale class names, wrong stats, and scope mismatches across README.md files.

## Context

### Problem Space

A full documentation audit across all 44 GEO-INFER modules revealed a **systematic pattern**:
many module `README.md` files contain code examples referencing fictional "illustrative" wrapper
classes that do not exist in the actual public API. The `SKILL.md` files are generally accurate
(they reference real classes), but the READMEs are misaligned — likely written before implementations
were finalized and never updated.

Additionally, root-level stats (README.md, CLAUDE.md) are outdated by ~41 files. The authoritative
count is in `GEO-INFER-INTRA/docs/overview.md`: **901 source files, 307,361 lines, 466 test files**.

### Scope Confirmed

- **44 modules** — all have README.md, SKILL.md, AGENTS.md ✓
- **GEO-INFER-INTRA/docs/modules/** — 46 .md files covering all 44 modules ✓
- **Root docs**: README.md, SKILL.md, AGENTS.md, CLAUDE.md

### Key Files

- `GEO-INFER-*/src/geo_infer_*/___init__.py` — source of truth for public API
- `GEO-INFER-*/README.md` — primary docs (many need fixing)
- `GEO-INFER-*/SKILL.md` — generally accurate
- `GEO-INFER-INTRA/docs/overview.md` — authoritative stats (901 files, 466 tests)
- `GEO-INFER-INTRA/docs/modules/index.md` — module status table

---

## Audit Findings: Issues By Severity

### CRITICAL — README uses entirely fictional classes (complete example rewrites needed)

| Module | Issue | Source of Truth |
|--------|-------|-----------------|
| **MATH** | `GeometryEngine`, `MatrixOps`, `FacilityOptimizer`, `Interpolator` don't exist | `__init__.py` exports: `MatrixOperations`, `IDWInterpolator`, `KrigingInterpolator`, `MoranI`, `getis_ord_g` |
| **AI** | `SpatialClassifier`, `DeepLearning`, `ObjectDetector` fictional | Actual: `ModelTrainer`, `TrainingConfig`, `ModelExplainer`, `GeospatialModelEvaluator` |
| **COG** | README and SKILL.md describe different incompatible APIs, neither fully matches exports | Actual: `CognitiveProcessingEngine`, `SpatialPerceptionModel`, `SpatialReasoningEngine`, `SpatialMemoryModel` |
| **AGENT** | `__init__.py` exports ONLY `__version__`; README uses `AgentManager`, `MultiAgentCoordinator` | Must add real exports AND fix README examples to match SKILL.md |
| **SPM** | `ParametricMapper`, `SpatialRegressor`, `Geostatistics` don't exist | Actual: `GeneralLinearModel`, `fit_glm`, `RandomFieldTheory`, `compute_spm`, `SPMData`, `SPMResult` |
| **SPACE** | 140+ line README describing `UnifiedH3Backend`, OSC Geo integration, planned features | Actual: `SpatialIndexingInterface`, `GeometricOperationsInterface`, backend dispatcher. OSC Geo explicitly disabled. |
| **IOT** | `SensorNetwork`, `DataStreamer`, `EdgeProcessor`, `DeviceCoordinator` don't exist | Actual: `MQTTIngestionEngine`, `SpatialQualityChecker`, `DeviceRegistry`, `IoTDataIngestion` |
| **BIO** | `SpeciesModeler`, `HabitatAnalyzer`, `ConservationPlanner`, `BiodiversityCalculator` don't exist; scope confusion (claims ecology, exports bioinformatics classes) | Actual: `SequenceAnalyzer`, `NetworkAnalyzer`, `SpatialMapper`, `BiologicalNetwork` |
| **API** | `__init__.py` is stub (only `__version__`); README documents 100+ fictional endpoints, `create_app()`, `FastAPI`, `GraphQLService`, `WebhookManager` | Only version string exported; entire README is aspirational |
| **LOG** | README describes logistics/routing/fleet features. Module is actually a logging/observability system | Actual: `EnhancedLogger`, `PerformanceMetrics`, `LogAnalyzer`, `GeoInferLogger` |
| **EMERGENCY** | `EmergencyOperationsCenter`, `DamageAssessor`, `SensorMonitor`, `InterAgencyComms` don't exist | Actual: `EmergencyCoordinator`, `ResourceDeployer`, `EvacuationPlanner`, `SituationalAwareness`, `SearchAndRescue` |
| **ECON** | `RegionalEconomist`, `MarketAnalyzer`, `ImpactAnalyzer`, `SiteSelector` don't exist | Actual: `EconomicModelingEngine`, `ConsumerChoiceModels`, `AggregateGrowthModels`, `BioregionalMarketDesign` |
| **HEALTH** | `DiseaseMapper`→`DiseaseHotspotAnalyzer`, `HealthAccessAnalyzer`→`HealthcareAccessibilityAnalyzer`, `EnvironmentalHealth`→`EnvironmentalHealthAnalyzer` | HEALTH has real exports — just wrong names in README |
| **CIV** | README documents PEP-style features (`ProposalManager`, `ReviewCoordinator`, `DecisionTracker`) instead of civic engagement features | Actual: `ParticipationPlatform`, `ParticipatoryMapper` from `stew_map.py`, `participatory.py`, `engagement.py` |
| **PEP** | Examples show `ProposalManager`, `ReviewCoordinator` which are wrong | Actual primary classes: `ConstituentMapper`, `OutreachOptimizer`, `PEPEngine`, `PEPOrchestrator` |

### HIGH — Wrong class names (specific mismatches, not complete rewrites)

| Module | Issue |
|--------|-------|
| **TIME** | README uses `TimeSeriesAnalyzer` but actual export is `TemporalAnalyzer`; also `ForecastingEngine` not `Forecaster` |
| **MARINE** | `OceanMonitor`→verify, `MarinePlanner`→`MarineSpatialPlanner`, `FisheriesAnalyzer`→verify/remove, `BlueEconomyPlanner`→verify/remove |
| **TRANSPORT** | `NetworkAnalyzer`→`TransportNetwork`, `TrafficModeler`→`TrafficAnalyzer`, `TransitPlanner`→`TransitOptimizer`; `DemandForecaster`, `CongestionAnalyzer`, `EquityAnalyzer` unverified |
| **WATER** | `WaterQualityMonitor`→`WaterQualityAssessor`, `FloodModeler`→`FloodDroughtAnalyzer`; `GroundwaterAnalyzer` and `WaterResourcesManager` unverified |
| **ACT** | `EnvironmentalActiveInferenceEngine`, `EcologicalModel` used in README examples but not exported in `__init__.py` |

### HIGH — Outdated stats

| File | Issue |
|------|-------|
| `README.md` (root) | Claims 860 files (297,360 lines), 421 test files. Actual: **901 files (307,361 lines), 466 test files** per INTRA overview.md |
| `CLAUDE.md` | Same outdated stats: "860 source files (297,360 lines) \| 421 test files (~87,000+ lines)" → should be "901 source files (307,361 lines) \| 466 test files (89,179 lines)" |

### MEDIUM — Minor fixes

| Module/File | Issue |
|-------------|-------|
| `GEO-INFER-AG/__init__.py` | Export typo: `__all__` contains `"AgricultureAPI"` but imports `AgriculturalAPI` |
| `GEO-INFER-INTRA/docs/modules/index.md` | Status indicators: SIM, REQ, METAGOV show "📝 Planning" but these modules have real implementations now |

### CLEAN — No issues found

ACT (mostly), ANT, SIM, ORG, COMMS, APP, ART, NORMS, REQ, GIT, EXAMPLES, PLACE, INTRA (hub), EDU,
DATA, SEC, OPS, RISK, FOREST, METAGOV, CLIMATE (mostly), ENERGY (mostly), TEST, BAYES ✅

---

## Plan

### Execution Strategy

5 parallel Engineer agents, each owning a group of modules. Each agent:
1. Reads actual `__init__.py` to confirm current exports
2. Reads key source files (core/, models/, api/) as needed
3. Updates README.md examples to use real exported classes
4. Preserves accurate sections (installation, architecture overview, badges)
5. Only changes what's wrong — no wholesale rewrites of accurate content
6. Runs no tests (docs-only changes)

### Agent A: Analytical Core — MATH, AI, COG, AGENT, SPM

**Modules**: GEO-INFER-MATH, GEO-INFER-AI, GEO-INFER-COG, GEO-INFER-AGENT, GEO-INFER-SPM

**Per module**:

**MATH**: Read `__init__.py`. Fix README examples:
- Replace `GeometryEngine` with actual geometry operations (use `haversine_distance`, `vincenty_distance`, `Polygon`)
- Replace `MatrixOps` with `MatrixOperations`
- Replace generic `Interpolator` with `IDWInterpolator` or `KrigingInterpolator`
- Remove/replace `FacilityOptimizer` (not exported)

**AI**: Read `__init__.py`. Completely rewrite README example section:
- Remove: `SpatialClassifier`, `DeepLearning`, `ObjectDetector`
- Use: `ModelTrainer`, `TrainingConfig`, `ModelExplainer`, `GeospatialModelEvaluator`, `GeospatialFeatureEngineer`

**COG**: Read `__init__.py` and `core/` files. Reconcile README + SKILL.md to use actual exports:
- Use: `CognitiveProcessingEngine`, `SpatialPerceptionModel`, `SpatialReasoningEngine`, `SpatialMemoryModel`
- Remove: `SpatialCognitionModel`, `MentalMapAnalyzer`, `AttentionModel`, `CognitiveAgent`

**AGENT**:
1. First fix `__init__.py` — add real exports that match SKILL.md (read `models/` files to get class names: `GeoAgent`, `ActiveInferenceAgent`, `RuleBasedAgent`, `AgentTelemetry`, `BDIAgent`)
2. Then fix README to use those exports
3. Remove: `AgentManager`, `MultiAgentCoordinator`, `AgentMessaging`, `TaskDelegator`

**SPM**: Read `__init__.py`. Fix README examples:
- Remove: `ParametricMapper`, `SpatialRegressor`, `Geostatistics`, `SpatialTester`
- Use: `GeneralLinearModel`, `fit_glm`, `RandomFieldTheory`, `compute_spm`, `SPMData`, `SPMResult`, `ContrastResult`

---

### Agent B: Spatial/Infrastructure — SPACE, IOT, BIO, TIME

**Modules**: GEO-INFER-SPACE, GEO-INFER-IOT, GEO-INFER-BIO, GEO-INFER-TIME

**SPACE**: Major README overhaul. Read `__init__.py`:
- Remove: entire "UnifiedH3Backend" section, OSC Geo section, planned feature sections
- Keep: H3 v4 API description, backend dispatcher explanation
- Use: `SpatialIndexingInterface`, `GeometricOperationsInterface`, `SpatialAnalyticsInterface`, `latlng_to_cell`, `cell_to_latlng`, `polygon_to_cells`
- The SKILL.md is accurate — use it as a guide for the correct content

**IOT**: Read `__init__.py`. Fix README examples:
- Remove: `SensorNetwork`, `DataStreamer`, `EdgeProcessor`, `DeviceCoordinator`
- Use: `MQTTIngestionEngine`, `SpatialQualityChecker`, `DeviceRegistry`, `IoTDataIngestion`, `RadiationMonitoringSystem`

**BIO**: Read `__init__.py`. Clarify scope and fix examples:
- The module is bioinformatics (sequences, networks, metabolic pathways) not ecology/conservation
- Remove: `SpeciesModeler`, `HabitatAnalyzer`, `ConservationPlanner`, `BiodiversityCalculator`
- Use: `SequenceAnalyzer`, `NetworkAnalyzer`, `SpatialMapper`, `BiologicalNetwork`, `PopulationDynamics`
- Update overview section to accurately reflect bioinformatics scope

**TIME**: Read `__init__.py`. Fix class names:
- `TimeSeriesAnalyzer` → `TemporalAnalyzer`
- `Forecaster` → `ForecastingEngine`
- `PatternMiner` → check exports, replace with actual
- Keep `EventDetector` (confirmed exported)

---

### Agent C: Domain Modules — EMERGENCY, ECON, HEALTH, LOG

**Modules**: GEO-INFER-EMERGENCY, GEO-INFER-ECON, GEO-INFER-HEALTH, GEO-INFER-LOG

**EMERGENCY**: Read `__init__.py`. Fix README examples:
- Remove: `EmergencyOperationsCenter`, `ResourceDeploymentOptimizer`, `DamageAssessor`, `SensorMonitor`, `InterAgencyComms`, `WildfireResponse`
- Use: `EmergencyCoordinator`, `ResourceDeployer`, `EvacuationPlanner`, `SituationalAwareness`, `SearchAndRescue`

**ECON**: Read `__init__.py`. Fix README examples:
- Remove: `RegionalEconomist`, `MarketAnalyzer`, `ImpactAnalyzer`, `SiteSelector`
- Use: `EconomicModelingEngine`, `SpatialEconometricsEngine`, `ConsumerChoiceModels`, `BioregionalMarketDesign`, `EcosystemServicesValuation`, `CircularEconomyModels`
- Show the three-tier structure: Microeconomics, Macroeconomics, Bioregional modules

**HEALTH**: Read `__init__.py`. Fix class names in README:
- `DiseaseMapper` → `DiseaseHotspotAnalyzer`
- `ClusterDetector` → verify (may not exist; check core/ for actual cluster detection class)
- `HealthAccessAnalyzer` → `HealthcareAccessibilityAnalyzer`
- `EnvironmentalHealth` → `EnvironmentalHealthAnalyzer`
- Update test documentation note (test_disease_surveillance.py was replaced by test_disease_surveillance_integration.py)

**LOG**: This module IS logging/observability, not logistics. Fix README completely:
- The title "Logistics and Supply Chain" is WRONG — the module IS a logging system
- Read `__init__.py` to confirm: `EnhancedLogger`, `PerformanceMetrics`, `LogAnalyzer`, `SpatialLogContext`, `GeoInferLogger`, `get_logger`
- Check if there's a separate logistics submodule via lazy loading
- Update README to accurately describe: structured JSON logging, performance metrics, Prometheus/Grafana integration, distributed tracing
- If logistics classes exist via lazy loading, document them as a secondary section

---

### Agent D: Community + More Domain — CIV, PEP, MARINE, TRANSPORT, WATER, API

**Modules**: GEO-INFER-CIV, GEO-INFER-PEP, GEO-INFER-MARINE, GEO-INFER-TRANSPORT, GEO-INFER-WATER, GEO-INFER-API

**CIV**: Read `src/geo_infer_civ/` (core/stew_map.py, participatory.py, engagement.py). Fix README:
- Remove: `ProposalManager`, `ReviewCoordinator`, `DecisionTracker`
- Use actual civic engagement classes: `ParticipationPlatform`, `ParticipatoryMapper`, engagement/stewardship classes from actual source
- Module is about civic participation / STEW-MAP, not proposal workflows

**PEP**: Read `src/geo_infer_pep/core/` (pep_engine.py, orchestrator.py). Fix README:
- Module = People Engagement Platform (HR/constituent management), not Python Enhancement Proposals
- Remove: `ProposalManager`, `ReviewCoordinator`
- Use: `ConstituentMapper`, `OutreachOptimizer`, `PEPEngine`, `PEPOrchestrator`
- The correct examples already exist in README (lines 140-156) — the WRONG examples (lines 41-86) need replacing

**MARINE**: Read `__init__.py`. Fix class names:
- `OceanMonitor` → check if exists, otherwise use `OceanographicDataProcessor`
- `MarinePlanner` → `MarineSpatialPlanner`
- `FisheriesAnalyzer` → check if exists, otherwise remove
- `BlueEconomyPlanner` → check if exists, otherwise remove

**TRANSPORT**: Read `__init__.py`. Fix class names:
- `NetworkAnalyzer` → `TransportNetwork`
- `TrafficModeler` → `TrafficAnalyzer`
- `TransitPlanner` → `TransitOptimizer`
- `DemandForecaster`, `CongestionAnalyzer`, `EquityAnalyzer` → check if exist, otherwise use `AccessibilityAnalyzer` or remove

**WATER**: Read `__init__.py`. Fix class names:
- `WaterQualityMonitor` → `WaterQualityAssessor`
- `FloodModeler` → `FloodDroughtAnalyzer`
- `GroundwaterAnalyzer` → check if exists in `HydrologicalModeler`, otherwise remove
- `WaterResourcesManager` → verify or remove

**API**: This is the hardest case — the module is a near-empty stub:
- Read `__init__.py` to confirm what actually exists
- Read `src/geo_infer_api/` to see what's actually implemented
- If truly a stub: replace README with honest description of what's planned vs implemented
- Do NOT document 100+ fictional endpoints
- Add a "Current Status" section indicating what's implemented

---

### Agent E: Stats, Typos, Index Updates

**Files**: root README.md, CLAUDE.md, GEO-INFER-AG/__init__.py, GEO-INFER-INTRA/docs/modules/index.md, GEO-INFER-ACT/README.md

**ROOT README.md**: Update stats table (around lines 41-48):
- `860 files, 297,360 lines` → `901 source files (307,361 lines)`
- `421 test files, ~87,000+ lines` → `466 test files (89,179 lines)`
- Also update the `📊 Codebase at a Glance` table

**CLAUDE.md**: Update stats (around lines 9-11):
- Same numbers: 860→901 files, 297,360→307,361 lines, 421→466 test files, ~87,000+→89,179 lines

**GEO-INFER-AG/__init__.py**: Fix typo in `__all__` list:
- Change `"AgricultureAPI"` → `"AgriculturalAPI"` (matches the actual import name)

**GEO-INFER-INTRA/docs/modules/index.md**: Update status indicators:
- `GEO-INFER-SIM`: Change from `📝 Planning` to `🔄 In Development` (has real implementations)
- `GEO-INFER-REQ`: Change from `📝 Planning` to `🔄 In Development` (has real implementations)
- `GEO-INFER-METAGOV`: Change from `📝 Planning` to `🔄 In Development` (has real implementations)

**GEO-INFER-ACT/README.md**: Check and add exports for `EnvironmentalActiveInferenceEngine` and `EcologicalModel` — either export them in `__init__.py` or remove from README examples

---

## Verification Strategy

After all agents complete:

1. **Grep check**: `grep -r "GeometryEngine\|MatrixOps\|FacilityOptimizer\|SpatialClassifier\|DeepLearning\|ParametricMapper\|SensorNetwork\|DataStreamer\|UnifiedH3Backend\|EmergencyOperationsCenter\|RegionalEconomist\|DiseaseMapper\|HealthAccessAnalyzer\|ProposalManager\|ReviewCoordinator" GEO-INFER-*/README.md` — should return ZERO results

2. **Stats check**: `grep "860\|297,360\|421 test" README.md CLAUDE.md` — should return ZERO results

3. **Import check**: For each fixed module, verify the first code example can be parsed syntactically (class names match `__init__.py`)

4. **AGENT __init__.py check**: `grep -c "class\|def\|import" GEO-INFER-AGENT/src/geo_infer_agent/__init__.py` — should be > 5 lines (real exports added)

5. **LOG README check**: README.md should NOT contain "Logistics" or "fleet management" as primary topic

6. **API README check**: README.md should NOT reference `create_app()`, `GraphQLService`, or `WebhookManager` unless they're actually implemented

---

## IDEAL STATE CRITERIA

### Accuracy
- [ ] ISC-C1: All README.md code examples use classes that exist in `__init__.py`
- [ ] ISC-C2: No README.md references fictional wrapper class names
- [ ] ISC-C3: Root README.md stats match INTRA overview.md (901 files, 466 tests)
- [ ] ISC-C4: CLAUDE.md stats match INTRA overview.md (901 files, 466 tests)
- [ ] ISC-C5: GEO-INFER-AGENT `__init__.py` exports real agent classes
- [ ] ISC-C6: GEO-INFER-LOG README describes logging/observability not logistics
- [ ] ISC-C7: GEO-INFER-API README accurately reflects stub status or real implementations
- [ ] ISC-C8: GEO-INFER-BIO README accurately describes bioinformatics scope
- [ ] ISC-C9: GEO-INFER-CIV README describes civic engagement not proposal workflows
- [ ] ISC-C10: GEO-INFER-PEP README uses ConstituentMapper/OutreachOptimizer not ProposalManager

### Consistency
- [ ] ISC-C11: SKILL.md and README.md in each module reference same class names
- [ ] ISC-C12: INTRA modules/index.md status indicators reflect actual implementation state
- [ ] ISC-C13: GEO-INFER-AG `__init__.py` `__all__` has `AgriculturalAPI` not `AgricultureAPI`
- [ ] ISC-C14: SPACE README does not mention OSC Geo or removed features

### Completeness
- [ ] ISC-C15: All 15 critical modules have updated README examples

### Anti-Criteria
- [ ] ISC-A1: No README.md stats claim 860 source files or 421 test files
- [ ] ISC-A2: No README introduces new incorrect class names during fixing
- [ ] ISC-A3: No accurate README sections (installation, architecture) are damaged
- [ ] ISC-A4: No SKILL.md files modified (they are already accurate)
- [ ] ISC-A5: No source code logic changed (docs-only fix, except AGENT __init__.py and AG typo)
