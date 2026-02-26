---
name: geo-infer-org
description: Organizational modeling for geospatial entities. Use when modeling organizational structures, spatial resource allocation, inter-organizational network analysis, or institutional spatial analysis for governance.
prerequisites:
  required:
    - geo-infer-data
  recommended: []
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-ORG

## Instructions

### Core Capabilities

- **Organizational modeling**: Structure analysis, capacity assessment, hierarchy mapping
- **Network analysis**: Inter-organizational relationships, collaboration networks
- **Resource management**: Spatial resource allocation, facility assignment
- **Institutional analysis**: Organizational effectiveness for spatial governance

### Key Imports

```python
from geo_infer_org.core.organization import OrganizationModel
from geo_infer_org.core.network import OrgNetworkAnalyzer
from geo_infer_org.core.resource import ResourceAllocator
```

## Examples

```python
from geo_infer_org.core.organization import OrganizationModel

model = OrganizationModel(name="Regional Authority")
model.add_unit("Planning", jurisdiction=planning_area_polygon)
model.add_unit("Emergency", jurisdiction=emergency_zone_polygon)
coverage = model.analyze_jurisdiction_overlap()
```

## Guidelines

- DAO mechanisms in development (Alpha)

### Integrations

- Integrates with METAGOV for governance structures
- Integrates with CIV for community organization mapping
- Test: `uv run python -m pytest GEO-INFER-ORG/tests/ -v`
