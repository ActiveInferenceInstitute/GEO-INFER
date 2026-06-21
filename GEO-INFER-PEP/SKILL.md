---
name: geo-infer-pep
description: Public engagement platform for geospatial projects. Use when building CRM for spatial stakeholders, managing public consultations, tracking community engagement with geographic planning, or running participation analytics.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended: []
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-PEP

## Instructions

### Core Capabilities

- **Stakeholder CRM**: Contact management with spatial context and engagement history
- **Consultation tracking**: Public hearing management, comment collection, sentiment analysis
- **Engagement analytics**: Participation metrics by geography, demographics, time
- **Campaign management**: Multi-channel outreach with spatial targeting
- **Notification**: Geographic notification delivery with audience segmentation

### Key Imports

```python
from geo_infer_pep.core.engagement import EngagementPlatform
from geo_infer_pep.core.crm import StakeholderCRM
from geo_infer_pep.core.analytics import EngagementAnalytics
from geo_infer_pep.api.crm_endpoints import CRMRouter
```

## Examples

```python
from geo_infer_pep.core.crm import StakeholderCRM

crm = StakeholderCRM()
crm.add_contact("Jane Doe", location=(45.5, -122.6), interests=["parks", "transit"])
nearby = crm.find_stakeholders(center=(45.5, -122.6), radius_km=5)
report = crm.engagement_report(period="2026-Q1")
```

## Guidelines

- CRM work uses implemented import, reporting, and visualization helpers

### Integrations

- Integrates with COMMS for multi-channel notification delivery
- Integrates with CIV for participatory engagement workflows
- Test: `uv run python -m pytest GEO-INFER-PEP/tests/ -v`
