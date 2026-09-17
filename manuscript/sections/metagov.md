## GEO-INFER-METAGOV — Meta-Governance Frameworks

GEO-INFER-METAGOV implements advanced meta-governance frameworks, organizational governance methods, and multilevel governance coordination for geospatial systems (per its `README.md`). The package `geo_infer_metagov` splits into `api/`, `core/`, `integrations/`, `models/`, and `utils/`, with a `config/` directory and an `IMPLEMENTATION_SUMMARY.md` at the module root documenting how the design maps to code.

The public interface, verified from `__init__.py`, exposes fourteen exported symbols that trace the governance lifecycle: `MultiLevelGovernanceFramework` and `PolycentricGovernanceSystem` for structuring authority across scales; `InstitutionalDesigner` for rule architecture; `StakeholderGovernanceCoordinator` for participant coordination; `AdaptiveGovernanceSystem` for feedback-driven adjustment; `AccountabilityFramework` for oversight; `ConflictResolver` with `ConflictResolutionMethod` for dispute handling; and `PerformanceEvaluator`, `PerformanceMetrics`, and `PerformanceDimension` for measuring governance outcomes. `ScenarioPlanner`, `Scenario`, and `ScenarioAnalysis` round out forward-looking policy exploration.

The test census counts 16 test files with 35 test classes and 151 test functions, concentrated on framework behavior — governance structures, conflict resolution paths, and scenario evaluation — rather than on numerics.

In the root README's Module Themes, METAGOV sits in Governance, Risk & Domain alongside NORMS, ORG, SEC, REQ, and RISK. Its distinctive role is the "meta" level: where ORG models an organization and NORMS models rules, METAGOV models how governance itself is designed, coordinated across levels, evaluated, and revised — the layer the other governance modules can be configured through.
