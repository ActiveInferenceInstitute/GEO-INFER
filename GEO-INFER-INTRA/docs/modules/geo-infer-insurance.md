# GEO-INFER-INSURANCE: Insurance Operations

> **Explanation**: Understanding Insurance Operations in GEO-INFER
>
> This module provides underwriting, policy, claims, and pricing operations for geospatial insurance workflows, including risk-scored underwriting decisions, premium calculation, claims processing, and portfolio management.

## 🎯 What is GEO-INFER-INSURANCE?
Note: Code examples are illustrative; see `GEO-INFER-INSURANCE` package sources and tests for runnable usage.

### Links
- Module README: ../../GEO-INFER-INSURANCE/README.md GEO-INFER-INSURANCE is the insurance operations layer of GEO-INFER. It packages the underwriting subsystem (previously shipped inside GEO-INFER-RISK) as an independently installable workspace module. It enables:

- **Underwriting**: Score applications and produce approve/refer/decline decisions - **Pricing**: Calculate premiums from coverage limits and assessed risk - **Claims**: Intake, validate, and process claims with reserves and payments - **Policy Management**: Policy lifecycle, coverage, and endorsements - **Portfolio**: Aggregate policies and claims, optimize capacity - **Compliance**: Check operations against declared regulatory frameworks

### Key Concepts

#### Underwriting Decisions
The module turns an application into a scored underwriting case:

```
python from geo_infer_insurance import create_underwriting_system, underwrite_insurance_policy # Create the underwriting system underwriting_system = create_underwriting_system() # Underwrite a policy application decision = underwrite_insurance_policy(application_data=insurance_application)
```
 #### Claims Processing Process a claim through intake, validation, and settlement:
```
python from geo_infer_insurance import process_insurance_claim # Process a claim claim_result = process_insurance_claim(claim_data=claim)
```
 ## 📚 Core Features ### 1. Underwriting Engine **Purpose**: Orchestrate underwriting cases end to end.
```python from geo_infer_insurance import UnderwritingEngine, UnderwritingConfig, create_underwriting_engine # Initialize the engine engine = create_underwriting_engine() # or with explicit configuration engine = UnderwritingEngine(UnderwritingConfig()) # Underwrite an application case = engine.underwrite_policy(application_data) # case.status -> 'approved' | 'declined'; case.decision carries reason, # confidence, risk_score, conditions, and requirements
```
 ### 2. Risk Assessment Engine **Purpose**: Score insured entities; uses `geo_infer_risk.core.risk_engine.EnhancedRiskEngine` when the optional geo-infer-risk package is installed (guarded import, degrades gracefully).
```python from geo_infer_insurance import assess_risk, RiskAssessmentEngine # Convenience scoring risk = assess_risk({"entity_type": "property", "value": 500_000}) # risk is a dict: risk_score, risk_level, assessment_method, confidence, # detailed_results, factors, location_analysis, uncertainty_analysis
```
 ### 3. Pricing Engine **Purpose**: Premium calculation from coverage and risk inputs.
```python from geo_infer_insurance import PricingEngine, calculate_premium pricing = PricingEngine() # PremiumCalculator and PricingMethod are available on the pricing module # calculate_premium(application_data, risk_assessment, rule_evaluation) -> PremiumCalculation premium = calculate_premium(application_data, risk_assessment, rule_evaluation)
```
 ### 4. Policy and Claims Management **Purpose**: Policy lifecycle and claims processing.
```python from geo_infer_insurance import PolicyManager, ClaimsProcessor, Policy, Claim policy_manager = PolicyManager() claims = ClaimsProcessor() # Required application fields: 'property', 'applicant', 'coverage_requests' # Required claim fields: 'policy_id', 'date_of_loss', 'claimed_amount', 'description'
```
 ### 5. Portfolio and Compliance **Purpose**: Portfolio aggregation and regulatory checks.
```python from geo_infer_insurance import PortfolioManager from geo_infer_insurance.underwriting.utils.compliance import ComplianceEngine portfolio = PortfolioManager() compliance = ComplianceEngine()
```
 ## 🔧 API Reference ### Top-level exports (`geo_infer_insurance`) All names below are importable from the package root.

```
python from geo_infer_insurance import ( UnderwritingEngine, UnderwritingConfig, RiskAssessmentEngine, PolicyManager, ClaimsProcessor, PortfolioManager, UnderwritingRulesEngine, PricingEngine, UnderwritingDecisionEngine, Policy, Claim, UnderwritingCase, Decision, create_underwriting_engine, underwrite_policy, process_claim, assess_risk, calculate_premium, # aliases create_underwriting_system, underwrite_insurance_policy, process_insurance_claim, )
```
 ### UnderwritingEngine The core orchestrator class.

```
python class UnderwritingEngine: def __init__(self, config): """Initialize with an UnderwritingConfig.""" def underwrite_policy(self, application_data): """Run the full underwriting flow; returns an UnderwritingCase with .status, .premium, and a .decision (approved, reason, confidence, risk_score, conditions)."""
```
 ### UnderwritingCase Dataclass produced by underwriting.

```
python class UnderwritingCase: case_id: str application_data: dict status: str # 'approved' | 'declined' risk_assessment premium: float decision: Decision # approved, reason, confidence, risk_score, conditions, requirements
```
 ### Convenience functions

```
python underwrite_policy(application_data, config=None) -> UnderwritingCase process_claim(claim_data, config=None) -> Claim assess_risk(entity_data, assessment_type="comprehensive") -> dict calculate_premium(application_data, risk_assessment, rule_evaluation) -> PremiumCalculation
```
 ## 🎯 Use Cases ### 1. Property Underwriting **Problem**: Decide whether to underwrite a property insurance application. **Solution**: Use the end-to-end underwriting flow.
```python from geo_infer_insurance import underwrite_policy application = { "property": { "address": "1420 Cedar Lane, Coastal County", "property_value": 750_000.0, "year_built": 1998, "construction_type": "masonry", "occupancy": "primary_residence", }, "applicant": { "name": "Jordan Rivera", "contact_info": {"email": "jordan.rivera@example.com", "phone": "555-0100"}, "credit_score": 760, }, "coverage_requests": [{"coverage_type": "fire", "limit": 600_000.0}], } case = underwrite_policy(application) print(case.case_id, case.status, case.premium, case.decision.reason)
```
 ### 2. Claims Intake **Problem**: Validate and process a filed claim. **Solution**: Use the claims processor.
```python from geo_infer_insurance import process_claim claim = process_claim({ "policy_id": "POL-1001", "date_of_loss": "2026-08-01", "claimed_amount": 12_000.0, "description": "Wind damage to roof", }) print(claim.claim_id, claim.status)
```
 ### 3. Risk Scoring for Pricing **Problem**: Score an insured entity before rating. **Solution**: Use `assess_risk`; feed its result into `calculate_premium` for pricing.
```python from geo_infer_insurance import assess_risk risk = assess_risk({"entity_type": "property", "value": 500_000}) print(risk["risk_score"], risk["risk_level"], risk["confidence"])
```
 ## 🔗 Integration with Other Modules ### GEO-INFER-RISK Integration The risk assessment engine uses `geo_infer_risk.core.risk_engine.EnhancedRiskEngine` for hazard scoring when the optional geo-infer-risk dependency is installed. All cross-module imports are guarded; the module works without them and reports degraded scoring rather than guessing.

### GEO-INFER-SPACE Integration `geo_infer_space` spatial indexing/analytics interfaces support location-aware rating when the optional geo-infer-space dependency is installed.

## 🚨 Troubleshooting ### Common Issues **Application validation failures:** Underwriting requires the fields `property`, `applicant`, and `coverage_requests` (each coverage request needs `coverage_type` and `limit`). Missing fields produce a declined case with `decision.reason = 'Application validation failed'` and the missing fields listed in `decision.conditions`.

```
python # Inspect validation errors before underwriting from geo_infer_insurance.underwriting.utils.validation import validate_underwriting_application result = validate_underwriting_application(application_data) print(result.errors)
```
 **Claim validation failures:** Claims require `policy_id`, `date_of_loss`, `claimed_amount`, and `description`.

**Optional integrations missing:** If geo-infer-risk or geo-infer-space are not installed, risk scoring degrades gracefully; check `assessment_method` in the risk result to see which path was used.

## 📊 Performance Optimization ### Batch Underwriting The `UnderwritingEngine` initializes with batch mode enabled for processing multiple applications in one pass.

### Efficient Claims Processing Use the `ClaimsEngine` for high-volume claim intake instead of one-off `process_claim` calls.

## 🔗 Related Documentation ### Tutorials - **[Risk Assessment](geo-infer-risk.md)** — the upstream risk engine feeding hazard scores ### How-to Guides - **[Examples Gallery](../../../GEO-INFER-EXAMPLES/docs/index.md)** — runnable examples including the INSURANCE orchestrator ### Technical Reference - **[Module README](../../GEO-INFER-INSURANCE/README.md)** — install and validation commands - **[Skill Notes](../../GEO-INFER-INSURANCE/SKILL.md)** — capability map and guidelines
