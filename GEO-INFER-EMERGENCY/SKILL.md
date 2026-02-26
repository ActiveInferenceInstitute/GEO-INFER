---
name: geo-infer-emergency
description: Emergency management and disaster response. Use when planning search and rescue, optimizing emergency resource deployment, modeling disaster scenarios, coordinating evacuation routes, or managing multi-agency response logistics.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-risk
    - geo-infer-transport
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-EMERGENCY

## Instructions

### Core Capabilities

- **Search and rescue**: SAR area prioritization, probability mapping, detection models
- **Resource deployment**: Facility location, logistics optimization, capacity planning
- **Disaster modeling**: Impact assessment, scenario simulation, cascading failures
- **Evacuation**: Route planning, shelter capacity, population flow analysis
- **Coordination**: Multi-agency response, resource allocation, real-time tracking

### Key Imports

```python
from geo_infer_emergency.core.sar import SearchAndRescue
from geo_infer_emergency.core.resource_deployment import ResourceOptimizer
from geo_infer_emergency.core.disaster import DisasterModel
from geo_infer_emergency.core.evacuation import EvacuationPlanner
```

## Examples

```python
from geo_infer_emergency.core.sar import SearchAndRescue

sar = SearchAndRescue()
priority_map = sar.compute_priority(
    last_known_position=(45.5, -122.6),
    terrain_data=terrain_raster,
    time_elapsed_hours=6
)
search_cells = sar.plan_search_pattern(priority_map, n_teams=4)
```

## Guidelines

- Resource deployment optimization in development (Alpha)

### Integrations

- Integrates with TRANSPORT for evacuation route optimization
- Integrates with COMMS for emergency notification broadcasting
- Test: `uv run python -m pytest GEO-INFER-EMERGENCY/tests/ -v`
