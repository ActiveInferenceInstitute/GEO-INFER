---
title: "GEO-INFER-PEP: People, Engagement, Performance"
description: "HR, CRM, and talent management with spatial context for place-based organizations"
purpose: "Unified data model and workflows for employee, customer, and candidate management"
module_type: "Community & Applications"
status: "Stable"
last_updated: "2026-04-16"
dependencies: ["DATA", "COMMS"]
compatibility: ["GEO-INFER-DATA", "GEO-INFER-COMMS", "GEO-INFER-CIV"]
tags: ["hr", "crm", "talent", "people-operations", "engagement"]
difficulty: "Intermediate"
estimated_time: "30"
---

<div align="center">
  <h3><a href="../README.md">GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">Agent Architecture</a> |
  <a href="../README.md#-module-overview">Module Index</a> |
  <a href="./docs/">Documentation</a> •
  <a href="./SKILL.md">Claude Skill</a>
</div>

---

# GEO-INFER-PEP: People, Engagement, Performance

## Overview

**GEO-INFER-PEP** is a unified platform for people operations in place-based organizations. It combines HR (employees), CRM (customers), and talent (candidates, requisitions) into a single Pydantic-validated data model, with CSV importers, transformers, and dashboard reporting. The module targets civic organizations, municipalities, and mission-driven companies that need to manage staff, constituents, and hiring pipelines with a consistent data layer.

## Core Objectives

- **Unified People Data Model**: Pydantic models for `Employee`, `Customer`, `Candidate`, and `JobRequisition` with shared address, contact, and interaction schemas
- **Data Ingestion**: CSV importers for HR, CRM, and talent data sources with validation and error reporting
- **Workflow Orchestration**: Onboarding, offboarding, and campaign workflows coordinated through the `PEPOrchestrator`
- **Reporting & Dashboards**: Aggregated HR, CRM, and talent dashboards via `generate_comprehensive_*_dashboard` helpers
- **Validation**: `PEPValidator` checks referential integrity and schema conformance across imported data

## Features

### HR — Employee Management

```python
from geo_infer_pep.core import PEPEngine

engine = PEPEngine()
engine.initialize()

result = engine.import_hr_data("data/employees.csv")
print(f"Imported {result['records_imported']} employees")
```

### CRM — Customer Management

```python
result = engine.import_crm_data("data/customers.csv")
print(f"Imported {result['records_imported']} customers")
```

### Talent — Candidate & Requisition Management

```python
result = engine.import_talent_data(
    candidates_file="data/candidates.csv",
    requisitions_file="data/requisitions.csv",
)
print(f"Candidates: {result['candidates_imported']}, Requisitions: {result['requisitions_imported']}")
```

### Onboarding Workflow

```python
outcome = engine.process_onboarding_workflow({
    "employee_id": "E-2026-001",
    "start_date": "2026-05-01",
    "department": "Engineering",
})
```

## API Reference

| Class / Function | Purpose |
|------------------|---------|
| `PEPEngine(data_manager=None)` | High-level orchestrator across HR/CRM/Talent domains |
| `PEPDataManager` | In-memory data store for employees, customers, candidates, requisitions |
| `PEPOrchestrator` | Runs multi-step workflows (onboarding, campaign, hiring) with status tracking |
| `PEPValidator` | Cross-model referential-integrity and schema validation |
| `CSVHRImporter`, `CSVCRMImporter`, `CSVTalentImporter` | Typed CSV ingestion for each domain |
| `Employee`, `Customer`, `Candidate`, `JobRequisition` | Pydantic models with validation |
| `generate_comprehensive_hr_dashboard(employees)` | Aggregated HR metrics (headcount, tenure, performance) |
| `generate_comprehensive_crm_dashboard(customers)` | Aggregated CRM metrics (segments, interaction frequency) |
| `generate_comprehensive_talent_dashboard(candidates, requisitions)` | Hiring funnel, time-to-fill, offer rates |

## Module Structure

```text
GEO-INFER-PEP/src/geo_infer_pep/
├── core/          # PEPEngine, PEPOrchestrator, PEPValidator
├── models/        # hr_models, crm_models, talent_models (Pydantic)
├── hr/            # HR importers and transformers
├── crm/           # CRM importers and transformers
├── talent/        # Talent importers and transformers
├── reporting/     # Dashboard generators
├── visualizations/# Plotting utilities
├── api/           # API endpoints
└── methods.py     # Flat functional facade over engine capabilities
```

## Data Models

| Model | Domain | Key Fields |
|-------|--------|------------|
| `Employee` | HR | `employee_id`, `personal_info`, `compensation`, `job_history`, `performance_reviews` |
| `Customer` | CRM | `customer_id`, `address`, `interactions`, `segment` |
| `Candidate` | Talent | `candidate_id`, `requisition_id`, `status`, `interviews`, `offer` |
| `JobRequisition` | Talent | `requisition_id`, `title`, `status`, `hiring_manager`, `opened_date` |

## Integration

| Module | Direction | Purpose |
|--------|-----------|---------|
| **GEO-INFER-DATA** | PEP ← DATA | Source datasets (employee records, customer lists, applicant pools) |
| **GEO-INFER-COMMS** | PEP → COMMS | Outreach and communication triggers from PEP workflows |
| **GEO-INFER-CIV** | PEP ↔ CIV | Shared constituent / member concepts with civic participation data |

Data flow: DATA provides raw records. PEP ingests, validates, and models them. Downstream dashboards and COMMS-driven outreach consume the structured output.

## Installation

```bash
uv pip install -e "./GEO-INFER-PEP"
```

## Testing

```bash
uv run python -m pytest GEO-INFER-PEP/tests/ -v
uv run python -m pytest GEO-INFER-PEP/tests/unit/ -v
uv run python -m pytest GEO-INFER-PEP/tests/ --cov=GEO-INFER-PEP/src --cov-report=html
```

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |

---

**Status**: Stable

**Last Updated**: 2026-04-16
