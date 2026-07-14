# GEO-INFER-NORMS/src/geo_infer_norms/core

Core workspace within `GEO-INFER-NORMS`.

## Contents

- `__init__.py`
- `compliance_tracking.py`
- `legal_frameworks.py`
- `normative_inference.py`
- `policy_impact.py`
- `zoning_analysis.py`

## Public Interface

- `compliance_tracking.py:ComplianceTracker` (class)
- `compliance_tracking.py:ComplianceReport` (class)
- `legal_frameworks.py:LegalFramework` (class)
- `legal_frameworks.py:JurisdictionHandler` (class)
- `normative_inference.py:NormativeInference` (class)
- `normative_inference.py:SocialNormDiffusion` (class)
- `policy_impact.py:PolicyImpactAnalyzer` (class)
- `policy_impact.py:RegulatoryImpactAssessment` (class)
- `zoning_analysis.py:ZoningAnalyzer` (class)
- `zoning_analysis.py:LandUseClassifier` (class)

## Module Metadata

- Module: `GEO-INFER-NORMS`
- Package: `geo_infer_norms`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-NORMS`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS`

## Dependencies

- `geopandas>=0.10.0`
- `matplotlib>=3.4.0`
- `networkx>=2.6.0`
- `numpy>=1.20.0`
- `pandas>=1.3.0`
- `shapely>=1.8.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module NORMS
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
