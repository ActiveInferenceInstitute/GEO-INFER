# GEO-INFER-RISK/src/geo_infer_risk/underwriting/core

Core workspace within `GEO-INFER-RISK`.

## Contents

- `claims_processing.py`
- `policy_management.py`
- `portfolio_management.py`
- `pricing_engine.py`
- `risk_assessment.py`
- `underwriting_decisions.py`
- `underwriting_engine.py`
- `underwriting_rules.py`

## Public Interface

- `claims_processing.py:ClaimStatus` (class)
- `claims_processing.py:ClaimType` (class)
- `claims_processing.py:Reserve` (class)
- `claims_processing.py:Payment` (class)
- `claims_processing.py:Claim` (class)
- `claims_processing.py:ClaimsProcessingConfig` (class)
- `claims_processing.py:ClaimsProcessor` (class)
- `claims_processing.py:ClaimsEngine` (class)
- `claims_processing.py:create_claims_processor` (function)
- `policy_management.py:PolicyStatus` (class)
- `policy_management.py:CoverageType` (class)
- `policy_management.py:Coverage` (class)
- `policy_management.py:Endorsement` (class)
- `policy_management.py:Policy` (class)
- `policy_management.py:PolicyLifecycle` (class)
- `policy_management.py:PolicyManager` (class)
- `policy_management.py:create_policy_manager` (function)
- `portfolio_management.py:PortfolioManager` (class)
- `portfolio_management.py:PortfolioOptimizer` (class)
- `pricing_engine.py:PricingMethod` (class)

## Module Metadata

- Module: `GEO-INFER-RISK`
- Package: `geo_infer_risk`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-RISK`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module RISK`

## Dependencies

- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `scipy>=1.7.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module RISK
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
