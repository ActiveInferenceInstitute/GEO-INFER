# GEO-INFER-METAGOV/src/geo_infer_metagov/models

Models workspace within `GEO-INFER-METAGOV`.

## Contents

- `__init__.py`
- `governance_models.py`

## Public Interface

- `governance_models.py:GovernanceStatus` (class)
- `governance_models.py:DecisionType` (class)
- `governance_models.py:ParticipationLevel` (class)
- `governance_models.py:GoverningEntity` (class)
- `governance_models.py:StakeholderProfile` (class)
- `governance_models.py:DecisionDomain` (class)
- `governance_models.py:GovernanceRule` (class)
- `governance_models.py:CoordinationMechanism` (class)
- `governance_models.py:PerformanceIndicator` (class)
- `governance_models.py:GovernanceStructure` (class)
- `governance_models.py:ConflictRecord` (class)
- `governance_models.py:AdaptiveManagementCycle` (class)
- `governance_models.py:TransparencyRecord` (class)
- `governance_models.py:AccountabilityReport` (class)

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
