# GEO-INFER-PEP/src/geo_infer_pep/models

Models workspace within `GEO-INFER-PEP`.

## Contents

- `__init__.py`
- `crm_models.py`
- `hr_models.py`
- `talent_models.py`

## Public Interface

- `crm_models.py:InteractionLog` (class)
- `crm_models.py:Address` (class)
- `crm_models.py:Customer` (class)
- `hr_models.py:EmploymentStatus` (class)
- `hr_models.py:Gender` (class)
- `hr_models.py:Compensation` (class)
- `hr_models.py:JobHistoryEntry` (class)
- `hr_models.py:PerformanceReview` (class)
- `hr_models.py:Employee` (class)
- `talent_models.py:JobRequisitionStatus` (class)
- `talent_models.py:CandidateStatus` (class)
- `talent_models.py:InterviewType` (class)
- `talent_models.py:InterviewFeedback` (class)
- `talent_models.py:Interview` (class)
- `talent_models.py:Offer` (class)
- `talent_models.py:Candidate` (class)
- `talent_models.py:JobRequisition` (class)

## Module Metadata

- Module: `GEO-INFER-PEP`
- Package: `geo_infer_pep`
- Version: `0.2.0`
- Install: `uv pip install -e ./GEO-INFER-PEP`
- Tests: `uv run python GEO-INFER-TEST/run_unified_tests.py --module PEP`

## Dependencies

- `fastapi>=0.100.0`
- `uvicorn[standard]>=0.23.2`
- `pydantic>=2.0`
- `pandas>=2.0`
- `matplotlib>=3.7.0`
- `seaborn>=0.13.0`


## Validation

```bash
uv run python GEO-INFER-TEST/run_unified_tests.py --module PEP
```


## Documentation Notes

This README describes current repository state only. Keep examples and claims tied to importable code, tracked files, or validation commands.
