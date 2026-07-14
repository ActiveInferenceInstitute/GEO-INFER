# GEO-INFER-METAGOV/src/geo_infer_metagov/integrations

Integrations workspace within `GEO-INFER-METAGOV`.

## Contents

- `__init__.py`
- `normative.py`
- `organizational.py`
- `security.py`
- `spatial.py`

## Public Interface

- `normative.py:NormativeGovernanceIntegration` (class)
- `organizational.py:OrganizationalGovernanceIntegration` (class)
- `security.py:SecurityGovernanceIntegration` (class)
- `spatial.py:SpatialGovernanceIntegration` (class)

## Module Metadata

- Module: `GEO-INFER-METAGOV`
- Package: `geo_infer_metagov`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-METAGOV`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module METAGOV`

## Dependencies

- `numpy>=1.20`
- `pyyaml>=6.0`
- `typing_extensions>=4.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module METAGOV
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
