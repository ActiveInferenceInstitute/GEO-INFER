# GEO-INFER-EMERGENCY Documentation

GEO-INFER-EMERGENCY provides emergency management tools for evacuation planning, multi-agency incident coordination, and resource deployment optimization. The module implements ICS (Incident Command System) and NIMS principles with geospatial awareness for hazard-driven decision-making.

## Module Overview

GEO-INFER-EMERGENCY operates across three functional areas:

1. **Evacuation Planning** -- Zone delineation, route optimization with contraflow support, shelter management, clearance time estimation, and special population handling for hospitals, nursing homes, and schools.
2. **Incident Coordination** -- Multi-agency coordination following ICS/NIMS principles with command structure establishment, communication channel assignment, sector-based resource allocation, and situation reporting.
3. **Resource Deployment** -- Optimization of emergency resource allocation using mixed-integer programming, real-time tracking, priority-based request queuing, and dynamic redeployment as conditions change.

## Core Capabilities

- **Evacuation zone management**: Create and manage zones with population data, special populations, and alert levels (WARNING, ORDER, LIFT).
- **Route optimization**: Multi-objective route planning with safety and clearance time objectives, contraflow lane identification, and road capacity constraints.
- **Phased evacuation**: Staged, simultaneous, and time-phased evacuation strategies with population percentage allocation per phase.
- **Shelter management**: Register shelters with capacity tracking, service availability, and accessibility flags.
- **ICS command structure**: Establish incident command with standard ICS positions (IC, Operations, Planning, Logistics, Finance, Safety, Liaison, PIO).
- **Multi-agency coordination**: Coordinate across fire, police, medical, and public works agencies with mutual aid agreements.
- **Resource allocation**: Priority-based resource deployment with greedy nearest-available assignment and coverage rate optimization.
- **Dynamic redeployment**: Move-up and redistribution strategies responding to changing incident conditions and predicted demand.
- **Communication management**: Automatic channel assignment (Command, Tactical, Medical, Logistics) per incident.

## Incident Types

| Type | Description |
|------|------------|
| `WILDFIRE` | Wildland fire events |
| `FLOOD` | River, coastal, flash floods |
| `EARTHQUAKE` | Seismic events |
| `HURRICANE` | Tropical cyclone events |
| `HAZMAT` | Hazardous materials incidents |
| `MASS_CASUALTY` | Mass casualty incidents |
| `TERRORISM` | Terrorism events |
| `CIVIL_UNREST` | Civil disturbance events |
| `INFRASTRUCTURE` | Infrastructure failures |
| `OTHER` | Unclassified incidents |

## ICS Scale Classifications

| Scale | ICS Type | Description |
|-------|----------|------------|
| `TYPE_5` | Local | Handled by initial response, single resource |
| `TYPE_4` | Expanding | Expanding incident, multiple resources |
| `TYPE_3` | Extended | Extended attack, multi-discipline response |
| `TYPE_2` | Complex | Complex incident, full ICS overhead |
| `TYPE_1` | National | Most complex, national significance |

## Integration Points

| Module | Integration |
|--------|------------|
| GEO-INFER-SPACE | Spatial analysis for evacuation zones and hazard mapping |
| GEO-INFER-TRANSPORT | Road network data for route optimization |
| GEO-INFER-RISK | Hazard models and risk zone delineation |
| GEO-INFER-CLIMATE | Weather and climate hazard data |
| GEO-INFER-IOT | Real-time sensor data for situational awareness |
| GEO-INFER-COMMS | Communication infrastructure for coordination |
| GEO-INFER-DATA | Population, infrastructure, and facility datasets |

## Documentation Contents

- [Getting Started](getting_started.md) -- Installation, core concepts, first evacuation plan
- [API Reference](api_reference.md) -- Class and method documentation
- [Basic Example: Flood Evacuation](examples/basic_example.md) -- Single-hazard evacuation planning
- [Advanced Example: Multi-Hazard Response](examples/advanced_example.md) -- Earthquake + tsunami with adaptive resource deployment

## Architecture

```
geo_infer_emergency/
  core/
    evacuation.py      -- EvacuationPlanner, zones, routes, shelters
    coordinator.py     -- EmergencyCoordinator, ICS, multi-agency
    resources.py       -- ResourceDeployer, allocation, redeployment
  models/
    emergency_models.py -- Data models for incidents and resources
  api/
    endpoints.py       -- REST API for emergency operations
  utils/
    hazard_mapping.py  -- Hazard zone geometry utilities
```

## Quick Start

```python
from geo_infer_emergency.core.evacuation import (
    EvacuationPlanner,
    EvacuationLevel,
)

planner = EvacuationPlanner(
    shelters=[
        {"id": "shelter_a", "name": "Community Center", "capacity": 500,
         "location": {"lat": 47.62, "lon": -122.34}},
    ]
)

plan = planner.plan(
    affected_zone={"id": "zone_1", "name": "Riverside", "level": "order",
                   "geometry": {"type": "Polygon", "coordinates": []}},
    population={"total": 2400, "special_populations": ["hospitals", "schools"]},
    destinations=[{"id": "shelter_a"}],
    phasing="staged",
    contraflow=True,
)

print(f"Plan: {plan['plan_id']}")
print(f"Population: {plan['affected_zone']['population']}")
print(f"Clearance time: {plan['estimated_clearance_time_hours']:.1f} hours")
print(f"Phases: {len(plan['phasing']['phases'])}")
```

## Key Concepts

**Incident Command System (ICS)** is a standardized management structure for emergency response. It defines a modular hierarchy: Incident Commander at the top, with Operations, Planning, Logistics, and Finance sections. GEO-INFER-EMERGENCY implements ICS positions and sector-based resource assignment.

**Evacuation phasing** controls the timing of population movement. Staged evacuation moves people closest to the hazard first, reducing road congestion. Simultaneous evacuation moves everyone at once, suitable for fast-onset events. Time-phased evacuation distributes departures across morning, afternoon, and evening windows.

**Contraflow** reverses inbound highway lanes to increase outbound capacity during evacuations. The module identifies suitable road segments and calculates the capacity increase from lane reversal.

**Resource deployment optimization** assigns available units (engines, ambulances, rescue teams) to demand points using response-time minimization. Coverage rate measures the fraction of demand points served within the response-time constraint.
