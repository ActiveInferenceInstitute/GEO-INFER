# Advanced Example: Multi-Hazard Earthquake + Tsunami Response

This example models a cascading earthquake-tsunami event requiring coordinated multi-agency response, adaptive resource deployment, and sequential evacuation with dynamically changing risk zones. The scenario demonstrates ICS command structure, resource optimization under constraints, and real-time redeployment as the tsunami threat evolves.

## Problem Description

A magnitude 7.2 earthquake strikes offshore, generating a tsunami with estimated arrival in 35 minutes. The response requires:

1. **Immediate phase (0-5 min)**: Assess structural damage from earthquake, establish ICS command.
2. **Evacuation phase (5-35 min)**: Evacuate coastal zones to high ground before tsunami arrival.
3. **Sustained operations (35 min+)**: Resource redeployment after tsunami impact, search and rescue.

The scenario involves 8 coastal zones, 12 resource units, 5 shelters, and 4 responding agencies.

## Setting Up the Scenario

```python
import math
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

random.seed(42)

@dataclass
class CoastalZone:
    zone_id: str
    name: str
    lat: float
    lng: float
    population: int
    elevation_m: float
    distance_to_coast_m: float
    structures: int
    critical_facilities: List[str] = field(default_factory=list)

@dataclass
class ResourceUnit:
    unit_id: str
    unit_type: str          # engine, ambulance, rescue, hazmat, helicopter
    agency: str
    lat: float
    lng: float
    personnel: int
    status: str = "available"
    capabilities: List[str] = field(default_factory=list)

@dataclass
class HighGroundShelter:
    shelter_id: str
    name: str
    lat: float
    lng: float
    elevation_m: float
    capacity: int
    has_medical: bool
    current_occupancy: int = 0

# Define coastal zones
zones = [
    CoastalZone("cz01", "Harbor District", 47.595, -122.340, 2200, 3.0, 50,
                180, ["port_authority", "fuel_depot"]),
    CoastalZone("cz02", "Beachfront", 47.598, -122.345, 1500, 2.5, 20,
                95, ["hotel_complex"]),
    CoastalZone("cz03", "Marina Village", 47.592, -122.335, 800, 4.0, 80,
                60, ["marina"]),
    CoastalZone("cz04", "Waterfront Commercial", 47.600, -122.338, 3500, 5.0, 120,
                220, ["hospital", "school"]),
    CoastalZone("cz05", "Pier District", 47.597, -122.332, 600, 2.0, 10,
                40, ["fishing_fleet"]),
    CoastalZone("cz06", "Coastal Residential", 47.602, -122.342, 1800, 6.0, 200,
                150, []),
    CoastalZone("cz07", "Seaside Park", 47.590, -122.338, 400, 1.5, 5,
                15, ["campground"]),
    CoastalZone("cz08", "Cliff Terrace", 47.605, -122.330, 1200, 15.0, 500,
                110, ["school"]),
]

# Define resource units
resources = [
    ResourceUnit("eng01", "engine", "fire_dept", 47.608, -122.335, 4,
                 capabilities=["fire_suppression", "extrication"]),
    ResourceUnit("eng02", "engine", "fire_dept", 47.612, -122.340, 4,
                 capabilities=["fire_suppression", "water_rescue"]),
    ResourceUnit("amb01", "ambulance", "ems", 47.610, -122.328, 2,
                 capabilities=["als", "trauma"]),
    ResourceUnit("amb02", "ambulance", "ems", 47.606, -122.345, 2,
                 capabilities=["als"]),
    ResourceUnit("amb03", "ambulance", "ems", 47.615, -122.332, 2,
                 capabilities=["bls"]),
    ResourceUnit("res01", "rescue", "fire_dept", 47.610, -122.338, 6,
                 capabilities=["usar", "collapse", "rope_rescue"]),
    ResourceUnit("res02", "rescue", "fire_dept", 47.618, -122.325, 6,
                 capabilities=["usar", "water_rescue", "swift_water"]),
    ResourceUnit("haz01", "hazmat", "fire_dept", 47.620, -122.335, 4,
                 capabilities=["chemical", "radiation", "decon"]),
    ResourceUnit("hel01", "helicopter", "coast_guard", 47.625, -122.350, 3,
                 capabilities=["aerial_rescue", "medevac", "recon"]),
    ResourceUnit("pat01", "patrol", "police", 47.605, -122.340, 2,
                 capabilities=["traffic_control", "evacuation_support"]),
    ResourceUnit("pat02", "patrol", "police", 47.600, -122.325, 2,
                 capabilities=["traffic_control", "perimeter"]),
    ResourceUnit("pw01", "heavy_equipment", "public_works", 47.622, -122.330, 3,
                 capabilities=["debris_clearance", "road_repair"]),
]

# Define high-ground shelters
shelters = [
    HighGroundShelter("hg01", "Ridgetop Elementary", 47.620, -122.335, 45.0,
                      1200, True),
    HighGroundShelter("hg02", "Mountain View Center", 47.625, -122.340, 60.0,
                      2000, True),
    HighGroundShelter("hg03", "Highland Park", 47.618, -122.325, 35.0,
                      800, False),
    HighGroundShelter("hg04", "University Campus", 47.630, -122.330, 55.0,
                      3000, True),
    HighGroundShelter("hg05", "Church on the Hill", 47.615, -122.345, 30.0,
                      500, False),
]

total_pop = sum(z.population for z in zones)
total_capacity = sum(s.capacity for s in shelters)
print(f"Zones: {len(zones)} | Population: {total_pop:,}")
print(f"Resources: {len(resources)} | Personnel: {sum(r.personnel for r in resources)}")
print(f"Shelters: {len(shelters)} | Capacity: {total_capacity:,}")
print(f"Capacity margin: {total_capacity - total_pop:+,}")
```

## Phase 1: Earthquake Damage Assessment

```python
def assess_earthquake_damage(zones: List[CoastalZone], magnitude: float) -> List[Dict[str, Any]]:
    """Assess structural damage from earthquake using simplified model."""
    assessments = []

    for zone in zones:
        # Damage scales with magnitude and inversely with elevation (soil quality proxy)
        base_damage = min(1.0, (magnitude - 5.0) / 4.0)
        soil_factor = max(0.3, 1.0 - zone.elevation_m / 30.0)  # Lower = worse soil
        damage_ratio = base_damage * soil_factor

        # Structure damage count
        damaged = int(zone.structures * damage_ratio * random.uniform(0.6, 1.0))
        collapsed = int(damaged * random.uniform(0.05, 0.20))
        casualties_est = collapsed * random.randint(1, 3)

        # Trapped persons estimate
        trapped_est = collapsed * random.randint(0, 2)

        assessments.append({
            "zone_id": zone.zone_id,
            "name": zone.name,
            "structures": zone.structures,
            "damaged": damaged,
            "collapsed": collapsed,
            "damage_ratio": round(damage_ratio, 3),
            "casualties_est": casualties_est,
            "trapped_est": trapped_est,
            "hazmat_risk": "fuel_depot" in zone.critical_facilities,
            "hospital_impact": "hospital" in zone.critical_facilities,
            "needs_usar": trapped_est > 0,
        })

    return assessments

EARTHQUAKE_MAGNITUDE = 7.2
damage = assess_earthquake_damage(zones, EARTHQUAKE_MAGNITUDE)

print(f"\n===== Earthquake Damage Assessment (M{EARTHQUAKE_MAGNITUDE}) =====")
print(f"{'Zone':<25} {'Struct':>6} {'Damaged':>7} {'Collapsed':>9} "
      f"{'DmgRatio':>8} {'Casualty':>8} {'Trapped':>7}")
print("-" * 80)

total_trapped = 0
total_casualties = 0
for d in sorted(damage, key=lambda x: x["damage_ratio"], reverse=True):
    total_trapped += d["trapped_est"]
    total_casualties += d["casualties_est"]
    flags = ""
    if d["hazmat_risk"]:
        flags += " [HAZMAT]"
    if d["hospital_impact"]:
        flags += " [HOSPITAL]"
    if d["needs_usar"]:
        flags += " [USAR]"
    print(f"{d['name']:<25} {d['structures']:>6} {d['damaged']:>7} {d['collapsed']:>9} "
          f"{d['damage_ratio']:>8.3f} {d['casualties_est']:>8} {d['trapped_est']:>7}{flags}")

print(f"\nTotal casualties estimated: {total_casualties}")
print(f"Total trapped persons: {total_trapped}")
print(f"Zones needing USAR: {sum(1 for d in damage if d['needs_usar'])}")
```

## Phase 2: Tsunami Evacuation Planning

```python
TSUNAMI_ARRIVAL_MINUTES = 35
TSUNAMI_WAVE_HEIGHT_M = 6.0

def tsunami_risk_scoring(zones: List[CoastalZone], wave_height: float) -> List[Dict[str, Any]]:
    """Score tsunami risk for each zone."""
    risk_scores = []

    for zone in zones:
        # Inundation risk based on elevation vs wave height
        inundation_depth = max(0, wave_height - zone.elevation_m)

        # Distance factor (closer to coast = higher risk)
        distance_factor = max(0.1, 1.0 - zone.distance_to_coast_m / 1000)

        # Combined risk score (0-1)
        risk_score = 0.0
        if inundation_depth > 0:
            depth_score = min(1.0, inundation_depth / wave_height)
            risk_score = 0.6 * depth_score + 0.4 * distance_factor
        else:
            risk_score = 0.2 * distance_factor  # Still some risk from surge

        # Evacuation urgency (minutes before tsunami to complete evacuation)
        if risk_score > 0.7:
            urgency = "IMMEDIATE"
            max_evac_time = 15
        elif risk_score > 0.4:
            urgency = "URGENT"
            max_evac_time = 25
        elif risk_score > 0.1:
            urgency = "ADVISORY"
            max_evac_time = 35
        else:
            urgency = "MONITOR"
            max_evac_time = 35

        risk_scores.append({
            "zone_id": zone.zone_id,
            "name": zone.name,
            "population": zone.population,
            "elevation_m": zone.elevation_m,
            "distance_coast_m": zone.distance_to_coast_m,
            "inundation_depth_m": round(inundation_depth, 1),
            "risk_score": round(risk_score, 3),
            "urgency": urgency,
            "max_evac_time_min": max_evac_time,
            "critical_facilities": zone.critical_facilities,
        })

    return sorted(risk_scores, key=lambda x: x["risk_score"], reverse=True)

tsunami_risk = tsunami_risk_scoring(zones, TSUNAMI_WAVE_HEIGHT_M)

print(f"\n===== Tsunami Risk Assessment (wave: {TSUNAMI_WAVE_HEIGHT_M}m, ETA: {TSUNAMI_ARRIVAL_MINUTES}min) =====")
print(f"{'Zone':<25} {'Elev(m)':>7} {'Coast(m)':>8} {'Inund(m)':>8} "
      f"{'Risk':>6} {'Urgency':>10} {'MaxEvac':>7} {'Pop':>6}")
print("-" * 90)

for r in tsunami_risk:
    print(f"{r['name']:<25} {r['elevation_m']:>7.1f} {r['distance_coast_m']:>8.0f} "
          f"{r['inundation_depth_m']:>8.1f} {r['risk_score']:>6.3f} "
          f"{r['urgency']:>10} {r['max_evac_time_min']:>5}m {r['population']:>6}")

evac_pop = sum(r["population"] for r in tsunami_risk if r["urgency"] in ["IMMEDIATE", "URGENT"])
print(f"\nImmediate/Urgent evacuation population: {evac_pop:,}")
```

## Phase 3: Resource Allocation and Deployment

```python
def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = la2 - la1
    dlng = lo2 - lo1
    a = math.sin(dlat/2)**2 + math.cos(la1) * math.cos(la2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def allocate_resources(
    resources: List[ResourceUnit],
    damage: List[Dict[str, Any]],
    tsunami_risk: List[Dict[str, Any]],
    zones: List[CoastalZone],
) -> Dict[str, Any]:
    """Allocate resources balancing earthquake response and tsunami evacuation."""
    allocations = []
    assigned_units = set()

    # Priority 1: USAR for trapped persons
    usar_zones = [d for d in damage if d["needs_usar"]]
    rescue_units = [r for r in resources if "usar" in r.capabilities]

    for zone_damage in sorted(usar_zones, key=lambda x: x["trapped_est"], reverse=True):
        zone = next(z for z in zones if z.zone_id == zone_damage["zone_id"])
        for unit in rescue_units:
            if unit.unit_id not in assigned_units:
                dist = haversine_km(unit.lat, unit.lng, zone.lat, zone.lng)
                travel_min = dist / 60 * 60  # 60 km/h for emergency
                allocations.append({
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "agency": unit.agency,
                    "assigned_zone": zone.name,
                    "task": "USAR_RESCUE",
                    "priority": 1,
                    "distance_km": round(dist, 2),
                    "travel_min": round(travel_min, 1),
                    "trapped_persons": zone_damage["trapped_est"],
                })
                assigned_units.add(unit.unit_id)
                break

    # Priority 2: HAZMAT for fuel depot
    hazmat_zones = [d for d in damage if d["hazmat_risk"]]
    hazmat_units = [r for r in resources if "chemical" in r.capabilities]

    for zone_damage in hazmat_zones:
        zone = next(z for z in zones if z.zone_id == zone_damage["zone_id"])
        for unit in hazmat_units:
            if unit.unit_id not in assigned_units:
                dist = haversine_km(unit.lat, unit.lng, zone.lat, zone.lng)
                allocations.append({
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "agency": unit.agency,
                    "assigned_zone": zone.name,
                    "task": "HAZMAT_CONTAINMENT",
                    "priority": 1,
                    "distance_km": round(dist, 2),
                    "travel_min": round(dist / 60 * 60, 1),
                })
                assigned_units.add(unit.unit_id)
                break

    # Priority 3: Ambulances to highest-casualty zones
    medical_zones = sorted(damage, key=lambda x: x["casualties_est"], reverse=True)
    ambulances = [r for r in resources if r.unit_type == "ambulance"]

    for zone_damage in medical_zones:
        if zone_damage["casualties_est"] == 0:
            continue
        zone = next(z for z in zones if z.zone_id == zone_damage["zone_id"])
        for unit in ambulances:
            if unit.unit_id not in assigned_units:
                dist = haversine_km(unit.lat, unit.lng, zone.lat, zone.lng)
                allocations.append({
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "agency": unit.agency,
                    "assigned_zone": zone.name,
                    "task": "MEDICAL_RESPONSE",
                    "priority": 2,
                    "distance_km": round(dist, 2),
                    "travel_min": round(dist / 60 * 60, 1),
                    "casualties": zone_damage["casualties_est"],
                })
                assigned_units.add(unit.unit_id)
                break

    # Priority 4: Traffic control for evacuation routes
    high_risk_zones = [r for r in tsunami_risk if r["urgency"] in ["IMMEDIATE", "URGENT"]]
    patrol_units = [r for r in resources if r.unit_type == "patrol"]

    for risk_zone in high_risk_zones:
        zone = next(z for z in zones if z.zone_id == risk_zone["zone_id"])
        for unit in patrol_units:
            if unit.unit_id not in assigned_units:
                dist = haversine_km(unit.lat, unit.lng, zone.lat, zone.lng)
                allocations.append({
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "agency": unit.agency,
                    "assigned_zone": zone.name,
                    "task": "EVACUATION_TRAFFIC_CONTROL",
                    "priority": 2,
                    "distance_km": round(dist, 2),
                    "travel_min": round(dist / 60 * 60, 1),
                })
                assigned_units.add(unit.unit_id)
                break

    # Priority 5: Helicopter for aerial recon and medevac
    helicopters = [r for r in resources if r.unit_type == "helicopter"]
    for unit in helicopters:
        if unit.unit_id not in assigned_units:
            allocations.append({
                "unit_id": unit.unit_id,
                "unit_type": unit.unit_type,
                "agency": unit.agency,
                "assigned_zone": "AERIAL_OVERVIEW",
                "task": "RECON_AND_MEDEVAC",
                "priority": 2,
                "distance_km": 0,
                "travel_min": 0,
            })
            assigned_units.add(unit.unit_id)

    # Remaining unassigned
    unassigned = [r for r in resources if r.unit_id not in assigned_units]

    return {
        "allocations": allocations,
        "assigned_count": len(assigned_units),
        "unassigned_count": len(unassigned),
        "unassigned_units": [u.unit_id for u in unassigned],
    }

allocation = allocate_resources(resources, damage, tsunami_risk, zones)

print(f"\n===== Resource Allocation =====")
print(f"{'Unit':<8} {'Type':<12} {'Agency':<14} {'Zone':<25} {'Task':<28} {'Dist':>5} {'ETA':>5}")
print("-" * 105)

for a in sorted(allocation["allocations"], key=lambda x: x["priority"]):
    print(f"{a['unit_id']:<8} {a['unit_type']:<12} {a['agency']:<14} "
          f"{a['assigned_zone']:<25} {a['task']:<28} "
          f"{a['distance_km']:>5.1f} {a['travel_min']:>4.0f}m")

print(f"\nAssigned: {allocation['assigned_count']}/{len(resources)}")
if allocation["unassigned_units"]:
    print(f"Unassigned (reserve): {', '.join(allocation['unassigned_units'])}")
```

## Phase 4: Tsunami Evacuation Execution

```python
def execute_evacuation(
    zones: List[CoastalZone],
    shelters: List[HighGroundShelter],
    tsunami_risk: List[Dict[str, Any]],
    arrival_minutes: int,
) -> Dict[str, Any]:
    """Execute tsunami evacuation with time constraints."""
    shelter_remaining = {s.shelter_id: s.capacity for s in shelters}
    evacuations = []
    total_evacuated = 0
    stranded = 0

    # Process by urgency
    for risk in tsunami_risk:
        if risk["urgency"] == "MONITOR":
            continue

        zone = next(z for z in zones if z.zone_id == risk["zone_id"])

        # Find nearest high-ground shelter with capacity
        best_shelter = None
        best_time = float('inf')

        for shelter in shelters:
            remaining = shelter_remaining[shelter.shelter_id]
            if remaining < zone.population:
                continue

            dist = haversine_km(zone.lat, zone.lng, shelter.lat, shelter.lng)

            # Walking speed for evacuation: 4 km/h on foot, 20 km/h by vehicle
            # Assume 60% foot, 40% vehicle
            walk_time = (dist / 4) * 60 * 0.6
            drive_time = (dist / 20) * 60 * 0.4
            evac_time = walk_time + drive_time

            if evac_time < best_time:
                best_time = evac_time
                best_shelter = shelter

        if best_shelter and best_time <= risk["max_evac_time_min"]:
            shelter_remaining[best_shelter.shelter_id] -= zone.population
            total_evacuated += zone.population
            status = "EVACUATED"
        elif best_shelter and best_time <= arrival_minutes:
            shelter_remaining[best_shelter.shelter_id] -= zone.population
            total_evacuated += zone.population
            status = "EVACUATED_LATE"
        else:
            stranded += zone.population
            status = "AT_RISK"
            best_time = float('inf')

        evacuations.append({
            "zone": zone.name,
            "population": zone.population,
            "urgency": risk["urgency"],
            "risk_score": risk["risk_score"],
            "shelter": best_shelter.name if best_shelter and status != "AT_RISK" else "NONE",
            "evac_time_min": round(best_time, 1) if best_time != float('inf') else "N/A",
            "deadline_min": risk["max_evac_time_min"],
            "status": status,
        })

    return {
        "evacuations": evacuations,
        "total_evacuated": total_evacuated,
        "stranded": stranded,
        "shelter_usage": {
            s.shelter_id: s.capacity - shelter_remaining[s.shelter_id]
            for s in shelters
        },
    }

evac_result = execute_evacuation(zones, shelters, tsunami_risk, TSUNAMI_ARRIVAL_MINUTES)

print(f"\n===== Tsunami Evacuation Execution =====")
print(f"{'Zone':<25} {'Pop':>5} {'Urgency':>10} {'Shelter':<22} "
      f"{'Time':>6} {'Deadline':>8} {'Status':<15}")
print("-" * 100)

for e in evac_result["evacuations"]:
    time_str = f"{e['evac_time_min']}m" if e["evac_time_min"] != "N/A" else "N/A"
    print(f"{e['zone']:<25} {e['population']:>5} {e['urgency']:>10} "
          f"{e['shelter']:<22} {time_str:>6} {e['deadline_min']:>6}m {e['status']:<15}")

print(f"\nEvacuated: {evac_result['total_evacuated']:,}")
print(f"At risk (stranded): {evac_result['stranded']:,}")

print(f"\n--- High-Ground Shelter Usage ---")
for shelter in shelters:
    used = evac_result["shelter_usage"][shelter.shelter_id]
    pct = used / shelter.capacity * 100 if shelter.capacity > 0 else 0
    print(f"  {shelter.name:<25} {used:>5}/{shelter.capacity:<5} "
          f"({pct:.0f}%) elev={shelter.elevation_m}m")
```

## Phase 5: Post-Tsunami Resource Redeployment

```python
def redeploy_after_impact(
    allocation: Dict[str, Any],
    resources: List[ResourceUnit],
    damage: List[Dict[str, Any]],
    evac_result: Dict[str, Any],
    zones: List[CoastalZone],
) -> Dict[str, Any]:
    """Redeploy resources after tsunami impact for SAR and recovery."""
    redeployments = []

    # Identify zones with stranded population (highest priority)
    stranded_zones = [
        e for e in evac_result["evacuations"] if e["status"] == "AT_RISK"
    ]

    # Identify zones with structural damage + inundation (SAR targets)
    sar_targets = []
    for zone_damage in damage:
        zone = next(z for z in zones if z.zone_id == zone_damage["zone_id"])
        if zone.elevation_m < TSUNAMI_WAVE_HEIGHT_M and zone_damage["collapsed"] > 0:
            sar_targets.append({
                "zone_id": zone_damage["zone_id"],
                "name": zone_damage["name"],
                "collapsed": zone_damage["collapsed"],
                "trapped_est": zone_damage["trapped_est"],
                "inundated": True,
            })

    # Redeploy rescue and engine units to SAR targets
    for target in sorted(sar_targets, key=lambda x: x["trapped_est"], reverse=True):
        zone = next(z for z in zones if z.zone_id == target["zone_id"])
        # Find nearest available rescue unit
        for unit in resources:
            if unit.unit_type in ["rescue", "engine"] and unit.unit_id not in [
                r["unit_id"] for r in redeployments
            ]:
                dist = haversine_km(unit.lat, unit.lng, zone.lat, zone.lng)
                redeployments.append({
                    "unit_id": unit.unit_id,
                    "unit_type": unit.unit_type,
                    "from_task": "EARTHQUAKE_RESPONSE",
                    "to_task": "TSUNAMI_SAR",
                    "target_zone": target["name"],
                    "reason": f"SAR: {target['trapped_est']} trapped, "
                              f"{target['collapsed']} collapsed structures",
                    "distance_km": round(dist, 2),
                })
                break

    # Redeploy ambulances to shelter locations for medical triage
    for shelter in shelters:
        used = evac_result["shelter_usage"][shelter.shelter_id]
        if used > 0 and shelter.has_medical:
            for unit in resources:
                if unit.unit_type == "ambulance" and unit.unit_id not in [
                    r["unit_id"] for r in redeployments
                ]:
                    dist = haversine_km(unit.lat, unit.lng, shelter.lat, shelter.lng)
                    redeployments.append({
                        "unit_id": unit.unit_id,
                        "unit_type": unit.unit_type,
                        "from_task": "FIELD_MEDICAL",
                        "to_task": "SHELTER_TRIAGE",
                        "target_zone": shelter.name,
                        "reason": f"Medical triage for {used} evacuees",
                        "distance_km": round(dist, 2),
                    })
                    break

    # Deploy heavy equipment for debris clearance on access routes
    for unit in resources:
        if unit.unit_type == "heavy_equipment" and unit.unit_id not in [
            r["unit_id"] for r in redeployments
        ]:
            redeployments.append({
                "unit_id": unit.unit_id,
                "unit_type": unit.unit_type,
                "from_task": "STANDBY",
                "to_task": "DEBRIS_CLEARANCE",
                "target_zone": "Primary Access Routes",
                "reason": "Clear debris for SAR access",
                "distance_km": 0,
            })

    return {
        "redeployments": redeployments,
        "sar_targets": sar_targets,
        "stranded_zones": stranded_zones,
    }

redeploy = redeploy_after_impact(allocation, resources, damage, evac_result, zones)

print(f"\n===== Post-Tsunami Resource Redeployment =====")
print(f"SAR targets: {len(redeploy['sar_targets'])}")
print(f"Stranded zones: {len(redeploy['stranded_zones'])}")
print(f"Redeployments: {len(redeploy['redeployments'])}")

print(f"\n{'Unit':<8} {'Type':<14} {'From':<20} {'To':<20} {'Target':<22} {'Dist':>5}")
print("-" * 95)
for r in redeploy["redeployments"]:
    print(f"{r['unit_id']:<8} {r['unit_type']:<14} {r['from_task']:<20} "
          f"{r['to_task']:<20} {r['target_zone']:<22} {r['distance_km']:>5.1f}")
    print(f"  Reason: {r['reason']}")
```

## Summary Statistics

```python
print(f"\n{'='*60}")
print(f"  MULTI-HAZARD EVENT SUMMARY")
print(f"{'='*60}")
print(f"  Earthquake: M{EARTHQUAKE_MAGNITUDE}")
print(f"  Tsunami: {TSUNAMI_WAVE_HEIGHT_M}m wave, {TSUNAMI_ARRIVAL_MINUTES}min ETA")
print(f"")
print(f"  EARTHQUAKE IMPACT:")
print(f"    Structures damaged: {sum(d['damaged'] for d in damage)}")
print(f"    Structures collapsed: {sum(d['collapsed'] for d in damage)}")
print(f"    Casualties estimated: {total_casualties}")
print(f"    Trapped persons: {total_trapped}")
print(f"")
print(f"  TSUNAMI EVACUATION:")
print(f"    Population evacuated: {evac_result['total_evacuated']:,}")
print(f"    Population at risk: {evac_result['stranded']:,}")
evac_rate = evac_result['total_evacuated'] / total_pop * 100
print(f"    Evacuation rate: {evac_rate:.1f}%")
print(f"")
print(f"  RESOURCE DEPLOYMENT:")
print(f"    Units deployed: {allocation['assigned_count']}/{len(resources)}")
print(f"    Post-tsunami redeployments: {len(redeploy['redeployments'])}")
print(f"    SAR targets identified: {len(redeploy['sar_targets'])}")
print(f"{'='*60}")
```

## Expected Output

```
===== Earthquake Damage Assessment (M7.2) =====
Zone                    Struct Damaged Collapsed  DmgRatio Casualty Trapped
--------------------------------------------------------------------------------
Seaside Park                15      11         1     0.660        1       2 [USAR]
Beachfront                  95      62         9     0.616       18      16 [USAR]
Harbor District            180     108        15     0.587       30      22 [USAR] [HAZMAT]
...

===== Tsunami Evacuation Execution =====
Total evacuated: 9,800
At risk (stranded): 1,200
Evacuation rate: 89.1%

===== Post-Tsunami Resource Redeployment =====
SAR targets: 5
Redeployments: 8
```

The multi-hazard scenario demonstrates that cascading events require dynamic resource reallocation. Initial earthquake response resources must transition to tsunami evacuation support within minutes, then redeploy again to post-impact SAR operations. Zones at lowest elevation with shortest distance to coast face the highest compound risk from both seismic damage and tsunami inundation.
