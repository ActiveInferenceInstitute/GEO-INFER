# GEO-INFER-NORMS/src/geo_infer_norms/api

Api workspace within `GEO-INFER-NORMS`.

## Contents

- `__init__.py`
- `compliance_api.py`
- `legal_api.py`
- `normative_api.py`
- `policy_api.py`
- `zoning_api.py`

## Public Interface

- `compliance_api.py:ComplianceStatusCreate` (class)
- `compliance_api.py:ComplianceMetricCreate` (class)
- `compliance_api.py:EvaluationData` (class)
- `compliance_api.py:GeoPoint` (class)
- `compliance_api.py:ReportParams` (class)
- `compliance_api.py:ComplianceAPI` (class)
- `legal_api.py:GeometryModel` (class)
- `legal_api.py:JurisdictionCreate` (class)
- `legal_api.py:RegulationCreate` (class)
- `legal_api.py:RegulatoryFrameworkCreate` (class)
- `legal_api.py:PointLocation` (class)
- `legal_api.py:LegalAPI` (class)
- `normative_api.py:GeometryModel` (class)
- `normative_api.py:SocialNormCreate` (class)
- `normative_api.py:NormDiffusionRequest` (class)
- `normative_api.py:NormativeInferenceRequest` (class)
- `normative_api.py:NormPolicyImpactRequest` (class)
- `normative_api.py:PointLocation` (class)
- `normative_api.py:NormativeAPI` (class)
- `policy_api.py:GeometryModel` (class)

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
