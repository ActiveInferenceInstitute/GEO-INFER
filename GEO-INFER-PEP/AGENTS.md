# GEO-INFER-PEP: Agent Capabilities

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> •
  <a href="../README.md#-module-overview">Module Index</a> •
  <a href="./README.md">Module Documentation</a>
</div>

---

## Overview

**GEO-INFER-PEP** (People, Engagement, Performance) provides agent-accessible operations for HR, CRM, and talent management. Agents can ingest CSV data, validate records against Pydantic schemas, orchestrate multi-step workflows (onboarding, hiring, campaigns), and produce aggregated dashboards.

## Agent Capabilities

### 1. Data Ingestion

```python
from geo_infer_pep.core import PEPEngine

engine = PEPEngine()
engine.initialize()

engine.import_hr_data("data/employees.csv")
engine.import_crm_data("data/customers.csv")
engine.import_talent_data(
    candidates_file="data/candidates.csv",
    requisitions_file="data/requisitions.csv",
)
```

### 2. Workflow Orchestration

```python
from geo_infer_pep.core import PEPOrchestrator

orchestrator = PEPOrchestrator()

outcome = orchestrator.run_workflow(
    name="employee_onboarding",
    payload={
        "employee_id": "E-2026-001",
        "start_date": "2026-05-01",
        "department": "Engineering",
    },
)
print(f"Status: {outcome.status}")
```

### 3. Data Validation

```python
from geo_infer_pep.core import PEPValidator

validator = PEPValidator()
result = validator.validate_employees(engine.data_manager._employees)
if not result.is_valid:
    for err in result.errors:
        print(err)
```

### 4. Reporting & Dashboards

```python
from geo_infer_pep.methods import (
    generate_comprehensive_hr_dashboard,
    generate_comprehensive_crm_dashboard,
    generate_comprehensive_talent_dashboard,
)

hr_dash = generate_comprehensive_hr_dashboard(engine.data_manager._employees)
crm_dash = generate_comprehensive_crm_dashboard(engine.data_manager._customers)
talent_dash = generate_comprehensive_talent_dashboard(
    engine.data_manager._candidates,
    engine.data_manager._requisitions,
)
```

## Implementation Status

### Currently Implemented

| Feature | Status | Description |
|---------|--------|-------------|
| **HR Data Ingestion** | Ready | CSV import, Pydantic validation, in-memory store |
| **CRM Data Ingestion** | Ready | Customer records with address and interaction logs |
| **Talent Data Ingestion** | Ready | Candidates and job requisitions with status tracking |
| **Workflow Orchestration** | Ready | `PEPOrchestrator` with step-level status tracking |
| **Cross-Domain Validation** | Ready | `PEPValidator` for referential integrity |
| **Reporting Dashboards** | Ready | Aggregated HR/CRM/Talent metrics |

### Planned

| Feature | Priority | Description |
|---------|----------|-------------|
| **Persistent Data Store** | High | Replace in-memory store with SQLAlchemy/Postgres backend |
| **Spatial Aggregation** | Medium | H3-indexed employee/customer distributions via SPACE |
| **Campaign Optimizer** | Medium | Budget-constrained outreach planning over segmented populations |

## Data Model Summary

| Model | Domain | Purpose |
|-------|--------|---------|
| `Employee` | HR | Person record with compensation, job history, performance |
| `Customer` | CRM | External contact with address and interaction log |
| `Candidate` | Talent | Applicant tracking through the hiring funnel |
| `JobRequisition` | Talent | Open role definition with hiring manager and status |

## Use Cases

### Integrated People Operations

```python
from geo_infer_pep.core import PEPEngine

engine = PEPEngine()
engine.initialize()

# Ingest data across domains
engine.import_hr_data("data/employees.csv")
engine.import_talent_data("data/candidates.csv", "data/requisitions.csv")

# Run a full onboarding workflow
engine.process_onboarding_workflow({
    "candidate_id": "C-123",
    "requisition_id": "R-45",
    "start_date": "2026-05-01",
})
```

---

**Last Updated**: 2026-04-16

**Claude Skill**: See [SKILL.md](./SKILL.md) for quick-reference API examples and integration map.
