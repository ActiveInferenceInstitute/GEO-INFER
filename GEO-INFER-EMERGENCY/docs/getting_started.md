# Getting Started with GEO-INFER-EMERGENCY

This guide covers installation, core concepts, and building your first evacuation plan and resource deployment.

## Installation

```bash
uv pip install -e ./GEO-INFER-EMERGENCY
```

For transport routing and risk integration:

```bash
uv pip install -e ./GEO-INFER-EMERGENCY ./GEO-INFER-TRANSPORT ./GEO-INFER-RISK
```

### Dependencies

GEO-INFER-EMERGENCY requires Python 3.9+ with:

- Standard library (`datetime`, `dataclasses`, `enum`, `heapq`, `logging`)

Optional:

- `geo_infer_transport` -- Road network data for route optimization
- `geo_infer_risk` -- Hazard models for zone delineation
- `geo_infer_space` -- Spatial analysis for affected area calculation

## Core Concepts

### Evacuation Levels

Three alert levels control evacuation status:

| Level | Meaning | Action Required |
|-------|---------|----------------|
| `WARNING` | Be prepared to evacuate | Prepare go-bags, review routes |
| `ORDER` | Evacuate immediately | Leave the area via assigned routes |
| `LIFT` | Safe to return | Residents may re-enter the zone |

### Evacuation Phasing Strategies

| Strategy | Description | Best For |
|----------|------------|---------|
| `staged` | Move closest to hazard first (30/40/30% split) | Slow-onset events (flood, wildfire) |
| `simultaneous` | Move everyone at once (100%) | Fast-onset events (tsunami, dam failure) |
| `time_phased` | Distribute departures across time windows (40/35/25%) | Large metro evacuations |

### ICS Incident Scale

The Incident Command System uses five complexity types:

| Type | Scale | Command Structure |
|------|-------|------------------|
| Type 5 | Local, single resource | IC only |
| Type 4 | Expanding, multiple resources | IC + limited overhead |
| Type 3 | Extended, multi-discipline | IC + Operations, Planning |
| Type 2 | Complex, full overhead | IC + all four sections |
| Type 1 | National significance | Full ICS, national coordination |

### Resource Types

| Type | Description |
|------|------------|
| `ENGINE` | Fire engine |
| `TRUCK` | Fire truck (ladder/platform) |
| `AMBULANCE` | Medical transport |
| `RESCUE_UNIT` | Technical rescue team |
| `HAZMAT` | Hazardous materials unit |
| `HELICOPTER` | Rotary-wing aircraft |
| `DOZER` | Heavy equipment (bulldozer) |
| `WATER_TENDER` | Water supply vehicle |
| `PERSONNEL` | Human resources (teams) |

### Resource Status Lifecycle

```
AVAILABLE --> ASSIGNED --> EN_ROUTE --> ON_SCENE --> RETURNING --> AVAILABLE
                                                 --> OUT_OF_SERVICE
```

## First Example: Building an Evacuation Plan

Plan a staged evacuation for a riverside flood zone with two shelters.

```python
import math
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FloodZone:
    zone_id: str
    name: str
    population: int
    elevation_m: float
    flood_depth_m: float
    lat: float
    lng: float

@dataclass
class EvacShelter:
    shelter_id: str
    name: str
    capacity: int
    lat: float
    lng: float
    services: List[str]

# Define flood zones along a river
zones = [
    FloodZone("fz01", "Riverside Park", 800, 12.0, 3.5, 47.610, -122.340),
    FloodZone("fz02", "Harbor District", 1200, 8.0, 5.2, 47.605, -122.335),
    FloodZone("fz03", "Waterfront", 450, 6.0, 7.1, 47.600, -122.330),
    FloodZone("fz04", "Creek Meadows", 650, 15.0, 1.8, 47.615, -122.345),
    FloodZone("fz05", "Valley Floor", 900, 10.0, 4.0, 47.608, -122.325),
]

# Define shelters on higher ground
shelters = [
    EvacShelter("sh01", "Highland Community Center", 1500, 47.625, -122.330,
                ["food", "medical", "pet_friendly"]),
    EvacShelter("sh02", "Hilltop High School", 2000, 47.630, -122.340,
                ["food", "cots", "power"]),
    EvacShelter("sh03", "Eastside Church", 400, 47.620, -122.310,
                ["food", "medical"]),
]

def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = la2 - la1
    dlng = lo2 - lo1
    a = math.sin(dlat/2)**2 + math.cos(la1) * math.cos(la2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Assign each zone to nearest shelter with capacity
def assign_zones_to_shelters(zones, shelters):
    shelter_load = {s.shelter_id: 0 for s in shelters}
    assignments = {}

    # Sort zones by flood severity (deepest first = highest priority)
    sorted_zones = sorted(zones, key=lambda z: z.flood_depth_m, reverse=True)

    for zone in sorted_zones:
        best_shelter = None
        best_dist = float('inf')

        for shelter in shelters:
            remaining = shelter.capacity - shelter_load[shelter.shelter_id]
            if remaining >= zone.population:
                dist = haversine_km(zone.lat, zone.lng, shelter.lat, shelter.lng)
                if dist < best_dist:
                    best_dist = dist
                    best_shelter = shelter

        if best_shelter:
            shelter_load[best_shelter.shelter_id] += zone.population
            assignments[zone.zone_id] = {
                "shelter": best_shelter.shelter_id,
                "shelter_name": best_shelter.name,
                "distance_km": round(best_dist, 2),
                "travel_time_min": round(best_dist / 40 * 60, 1),  # 40 km/h
            }
        else:
            assignments[zone.zone_id] = {"shelter": None, "overflow": True}

    return assignments, shelter_load

assignments, shelter_load = assign_zones_to_shelters(zones, shelters)

print("--- Flood Evacuation Zone Assignments ---")
print(f"{'Zone':<20} {'Pop':>5} {'Depth(m)':>8} {'Shelter':<25} {'Dist(km)':>8} {'Time(min)':>9}")
for zone in sorted(zones, key=lambda z: z.flood_depth_m, reverse=True):
    a = assignments[zone.zone_id]
    if a.get("shelter"):
        print(f"{zone.name:<20} {zone.population:>5} {zone.flood_depth_m:>8.1f} "
              f"{a['shelter_name']:<25} {a['distance_km']:>8.2f} {a['travel_time_min']:>9.1f}")
    else:
        print(f"{zone.name:<20} {zone.population:>5} {zone.flood_depth_m:>8.1f} ** OVERFLOW **")

print(f"\n--- Shelter Utilization ---")
for shelter in shelters:
    load = shelter_load[shelter.shelter_id]
    pct = load / shelter.capacity * 100
    print(f"  {shelter.name}: {load}/{shelter.capacity} ({pct:.0f}%)")
```

## Staged Evacuation Phasing

```python
def calculate_phases(zones, assignments, strategy="staged"):
    """Calculate evacuation phases based on hazard severity."""
    sorted_zones = sorted(zones, key=lambda z: z.flood_depth_m, reverse=True)

    if strategy == "staged":
        # Phase 1: zones with depth > 5m (immediate danger)
        # Phase 2: zones with depth 2-5m (high risk)
        # Phase 3: zones with depth < 2m (precautionary)
        phases = {"phase_1": [], "phase_2": [], "phase_3": []}

        for zone in sorted_zones:
            a = assignments[zone.zone_id]
            entry = {
                "zone": zone.name,
                "population": zone.population,
                "shelter": a.get("shelter_name", "N/A"),
                "flood_depth": zone.flood_depth_m,
            }
            if zone.flood_depth_m > 5.0:
                phases["phase_1"].append(entry)
            elif zone.flood_depth_m > 2.0:
                phases["phase_2"].append(entry)
            else:
                phases["phase_3"].append(entry)

        return phases
    return {}

phases = calculate_phases(zones, assignments)

print("\n--- Staged Evacuation Phases ---")
phase_delays = {"phase_1": 0, "phase_2": 2, "phase_3": 4}

for phase_name, entries in phases.items():
    delay = phase_delays[phase_name]
    pop = sum(e["population"] for e in entries)
    print(f"\n{phase_name.upper()} (T+{delay}h) -- {len(entries)} zones, {pop} people:")
    for e in entries:
        print(f"  {e['zone']}: {e['population']} people, "
              f"flood depth {e['flood_depth']:.1f}m -> {e['shelter']}")
```

## Resource Deployment

Deploy emergency resources to cover the evacuation.

```python
def deploy_resources(zones, assignments):
    """Deploy resources based on zone severity and population."""
    deployments = []

    for zone in zones:
        # Calculate resource needs
        pop = zone.population
        engines = max(1, pop // 400)
        ambulances = max(1, pop // 600)
        personnel = max(4, pop // 100)

        a = assignments[zone.zone_id]
        deployments.append({
            "zone": zone.name,
            "population": pop,
            "severity": zone.flood_depth_m,
            "engines": engines,
            "ambulances": ambulances,
            "personnel": personnel,
            "destination": a.get("shelter_name", "N/A"),
        })

    return deployments

deployments = deploy_resources(zones, assignments)

print("\n--- Resource Deployment Plan ---")
print(f"{'Zone':<20} {'Pop':>5} {'Engines':>8} {'Ambul':>6} {'Personnel':>10}")
total_eng = total_amb = total_per = 0
for d in sorted(deployments, key=lambda x: x["severity"], reverse=True):
    print(f"{d['zone']:<20} {d['population']:>5} {d['engines']:>8} "
          f"{d['ambulances']:>6} {d['personnel']:>10}")
    total_eng += d["engines"]
    total_amb += d["ambulances"]
    total_per += d["personnel"]

print(f"{'TOTAL':<20} {sum(z.population for z in zones):>5} "
      f"{total_eng:>8} {total_amb:>6} {total_per:>10}")
```

## Clearance Time Estimation

```python
def estimate_clearance_time(zones, assignments, vehicles_per_hour=800):
    """Estimate total clearance time for all zones."""
    total_pop = sum(z.population for z in zones)
    vehicles_needed = total_pop / 2.5  # Assume 2.5 people per vehicle

    # Account for phasing delays
    max_delay = 4  # hours (Phase 3 delay)
    vehicle_hours = vehicles_needed / vehicles_per_hour

    clearance_time = vehicle_hours + max_delay

    # Longest single-route travel time
    max_travel = max(
        assignments[z.zone_id].get("travel_time_min", 0) for z in zones
    ) / 60  # convert to hours

    total_time = clearance_time + max_travel

    return {
        "total_population": total_pop,
        "vehicles_needed": int(vehicles_needed),
        "vehicles_per_hour_capacity": vehicles_per_hour,
        "phasing_delay_hours": max_delay,
        "max_travel_hours": round(max_travel, 2),
        "estimated_clearance_hours": round(total_time, 2),
    }

clearance = estimate_clearance_time(zones, assignments)
print(f"\n--- Clearance Time Estimate ---")
for key, val in clearance.items():
    print(f"  {key}: {val}")
```

## Next Steps

- Read the [API Reference](api_reference.md) for complete method documentation
- Follow the [Basic Example](examples/basic_example.md) for a full flood evacuation scenario
- Explore the [Advanced Example](examples/advanced_example.md) for multi-hazard earthquake + tsunami response
