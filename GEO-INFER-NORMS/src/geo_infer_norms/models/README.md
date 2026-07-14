# GEO-INFER-NORMS/src/geo_infer_norms/models

Models workspace within `GEO-INFER-NORMS`.

## Contents

- `__init__.py`
- `compliance_status.py`
- `legal_entity.py`
- `policy.py`
- `regulation.py`
- `zoning.py`

## Public Interface

- `compliance_status.py:ComplianceStatus` (class)
- `compliance_status.py:ComplianceMetric` (class)
- `legal_entity.py:LegalEntity` (class)
- `legal_entity.py:Jurisdiction` (class)
- `policy.py:Policy` (class)
- `policy.py:PolicyImplementation` (class)
- `regulation.py:Regulation` (class)
- `regulation.py:RegulatoryFramework` (class)
- `zoning.py:ZoningCode` (class)
- `zoning.py:ZoningDistrict` (class)
- `zoning.py:LandUseType` (class)

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
