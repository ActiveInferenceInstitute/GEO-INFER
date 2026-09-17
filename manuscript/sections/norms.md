## GEO-INFER-NORMS — Norms, Regulations, and Compliance

GEO-INFER-NORMS performs social-technical compliance modeling with deterministic and probabilistic analysis of norms, regulations, and spatial governance (per its `README.md`). The package `geo_infer_norms` comprises `api/`, `core/`, and `models/`, and at approximately 10,701 lines of Python it is a substantial rule-engineering module: it turns legal text and zoning structures into inspectable, testable objects.

The public interface, verified from `__init__.py`, exports ten module-level names organized as domain surfaces: `legal_frameworks` for jurisdiction-level legal structures, `zoning_analysis` for spatial regulation checks, `compliance_tracking` for ongoing adherence state, `policy_impact` for counterfactual policy evaluation, and `normative_inference` for reasoning over obligations. Alongside these, dataclass-style symbols `legal_entity`, `regulation`, `compliance_status`, `zoning`, and `policy` define the interoperable record types that the analysis surfaces consume and produce.

The test census counts 15 test files with 32 test classes and 206 test functions — a high test-to-export ratio reflecting the module's compliance posture, where each regulatory pathway must be demonstrably checked.

Under the root README's Module Themes, NORMS belongs to Governance, Risk & Domain together with METAGOV, ORG, PEP, REQ, SEC, and RISK. Its role in that theme is the rule layer: METAGOV designs governance and ORG models organizations, while NORMS encodes the specific norms and zoning constraints that any spatial decision must satisfy, deterministically where possible and probabilistically where regulation is uncertain.
