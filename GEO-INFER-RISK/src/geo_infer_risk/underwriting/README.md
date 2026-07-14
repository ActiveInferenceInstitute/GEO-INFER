# GEO-INFER-RISK/src/geo_infer_risk/underwriting

Underwriting workspace within `GEO-INFER-RISK`.

## Contents

- `core/`
- `models/`
- `utils/`
- `__init__.py`

## Public Interface

- `__init__.py:underwrite_policy` (function)
- `__init__.py:process_claim` (function)
- `__init__.py:assess_risk` (function)
- `__init__.py:calculate_premium` (function)
- `__init__.py:create_underwriting_engine` (function)
- `__init__.py:create_risk_assessment` (function)
- `__init__.py:create_policy_manager` (function)
- `__init__.py:create_claims_processor` (function)

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
