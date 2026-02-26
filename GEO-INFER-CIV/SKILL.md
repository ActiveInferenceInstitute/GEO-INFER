---
name: geo-infer-civ
description: Civic engagement and participatory mapping. Use when building participatory GIS, STEW-MAP implementations, community mapping platforms, citizen science data collection, or democratic spatial planning processes.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-econ
    - geo-infer-risk
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-CIV

## Instructions

### Core Capabilities

- **STEW-MAP**: Stewardship mapping for community organizations and land trusts
- **Participatory GIS**: Community-driven spatial data collection and validation
- **Civic engagement**: Public participation in spatial planning processes
- **Citizen science**: Volunteer geographic information (VGI) management
- **Democratic planning**: Inclusive spatial decision support systems

### Key Imports

```python
from geo_infer_civ.core.stew_map import StewardshipMapper
from geo_infer_civ.core.participatory import ParticipatoryGIS
from geo_infer_civ.core.engagement import CivicEngagementPlatform
```

## Examples

```python
from geo_infer_civ.core.stew_map import StewardshipMapper

mapper = StewardshipMapper()
mapper.register_organization("Friends of Park", boundary=park_polygon)
stewardship_map = mapper.build_map(region_bounds)
overlap = mapper.analyze_coverage_gaps(stewardship_map)
```

## Guidelines

- STEW-MAP partially implemented (Alpha)

### Integrations

- Integrates with PLACE for geographic boundary resolution
- Integrates with COMMS for community notification
- Test: `uv run python -m pytest GEO-INFER-CIV/tests/ -v`
