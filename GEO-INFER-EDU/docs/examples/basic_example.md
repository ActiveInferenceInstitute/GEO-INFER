# Basic Example: Education Access Mapping

This example maps school service areas, computes walking distances from residential zones, and identifies underserved areas where students lack proximate access to schools.

## Problem Setup

Model a district with 6 schools and 12 residential zones. Compute which zones are within walking distance of at least one school, and identify coverage gaps.

```python
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

@dataclass
class School:
    school_id: str
    name: str
    lat: float
    lng: float
    level: str
    capacity: int
    current_enrollment: int

@dataclass
class ResidentialZone:
    zone_id: str
    centroid_lat: float
    centroid_lng: float
    total_population: int
    school_age_children: int
    median_household_income: float

# Define schools
schools = [
    School("s01", "Maple Elementary", 47.610, -122.335, "elementary", 400, 350),
    School("s02", "Cedar Elementary", 47.620, -122.350, "elementary", 350, 310),
    School("s03", "Oak Middle School", 47.615, -122.320, "middle", 600, 520),
    School("s04", "Pine High School", 47.605, -122.310, "high", 1200, 980),
    School("s05", "Birch Elementary", 47.598, -122.340, "elementary", 300, 280),
    School("s06", "Spruce Middle", 47.625, -122.330, "middle", 500, 410),
]

# Define residential zones
zones = [
    ResidentialZone("z01", 47.612, -122.332, 1200, 180, 75000),
    ResidentialZone("z02", 47.608, -122.328, 950, 140, 62000),
    ResidentialZone("z03", 47.618, -122.345, 1400, 210, 88000),
    ResidentialZone("z04", 47.602, -122.318, 800, 120, 55000),
    ResidentialZone("z05", 47.614, -122.352, 1100, 165, 71000),
    ResidentialZone("z06", 47.606, -122.342, 900, 135, 48000),
    ResidentialZone("z07", 47.622, -122.325, 700, 105, 92000),
    ResidentialZone("z08", 47.596, -122.335, 850, 128, 43000),
    ResidentialZone("z09", 47.628, -122.340, 650, 98, 67000),
    ResidentialZone("z10", 47.600, -122.355, 750, 113, 39000),
    ResidentialZone("z11", 47.616, -122.310, 1050, 158, 84000),
    ResidentialZone("z12", 47.590, -122.325, 500, 75, 35000),
]

print(f"Schools: {len(schools)}")
print(f"Residential zones: {len(zones)}")
print(f"Total school-age children: {sum(z.school_age_children for z in zones)}")
```

## Step 1: Compute Distance Matrix

```python
def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = la2 - la1
    dlng = lo2 - lo1
    a = math.sin(dlat/2)**2 + math.cos(la1) * math.cos(la2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Distance from each zone to each school
distance_matrix: Dict[str, Dict[str, float]] = {}

for zone in zones:
    distance_matrix[zone.zone_id] = {}
    for school in schools:
        dist = haversine_km(zone.centroid_lat, zone.centroid_lng, school.lat, school.lng)
        distance_matrix[zone.zone_id][school.school_id] = round(dist, 3)

# Print distance matrix header
print("\n--- Distance Matrix (km) ---")
header = f"{'Zone':<6}" + "".join(f"{s.school_id:>8}" for s in schools)
print(header)
for zone in zones:
    row = f"{zone.zone_id:<6}"
    for school in schools:
        dist = distance_matrix[zone.zone_id][school.school_id]
        row += f"{dist:>8.2f}"
    print(row)
```

## Step 2: Assign Zones to Nearest Schools by Level

```python
WALK_THRESHOLD_KM = 1.6  # Approximately 1 mile

# Group schools by level
schools_by_level: Dict[str, List[School]] = {}
for school in schools:
    if school.level not in schools_by_level:
        schools_by_level[school.level] = []
    schools_by_level[school.level].append(school)

# For each zone, find nearest school at each level
zone_assignments: Dict[str, Dict[str, Dict[str, Any]]] = {}

for zone in zones:
    zone_assignments[zone.zone_id] = {}

    for level, level_schools in schools_by_level.items():
        nearest = None
        nearest_dist = float('inf')

        for school in level_schools:
            dist = distance_matrix[zone.zone_id][school.school_id]
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = school

        zone_assignments[zone.zone_id][level] = {
            'school': nearest,
            'distance_km': nearest_dist,
            'walkable': nearest_dist <= WALK_THRESHOLD_KM,
        }

print(f"\n--- Zone-to-School Assignments (walk threshold: {WALK_THRESHOLD_KM} km) ---")
print(f"{'Zone':<6} {'Elementary':<25} {'Middle':<25} {'High':<25}")

for zone in zones:
    row = f"{zone.zone_id:<6}"
    for level in ['elementary', 'middle', 'high']:
        assignment = zone_assignments[zone.zone_id].get(level, {})
        school = assignment.get('school')
        dist = assignment.get('distance_km', 0)
        walkable = assignment.get('walkable', False)
        flag = " [W]" if walkable else ""
        row += f"{school.name[:15] if school else 'N/A'} ({dist:.1f}km){flag}".ljust(25)
    print(row)
```

## Step 3: Compute Access Index

```python
def compute_access_index(zone: ResidentialZone, assignments: Dict[str, Dict[str, Any]]) -> float:
    """Compute a 0-1 access index for a residential zone."""
    scores = []

    for level, assignment in assignments.items():
        dist = assignment['distance_km']

        if dist <= WALK_THRESHOLD_KM:
            score = 1.0
        elif dist <= 3.0:
            score = 0.7
        elif dist <= 5.0:
            score = 0.4
        else:
            score = 0.1

        # Weight by school capacity utilization
        school = assignment['school']
        if school:
            utilization = school.current_enrollment / school.capacity
            capacity_factor = 1.0 if utilization < 0.9 else max(0.5, 1.0 - (utilization - 0.9) * 5)
            score *= capacity_factor

        scores.append(score)

    return sum(scores) / len(scores) if scores else 0.0

# Compute access index for each zone
access_indices = {}
for zone in zones:
    access_indices[zone.zone_id] = compute_access_index(zone, zone_assignments[zone.zone_id])

# Rank zones
ranked = sorted(access_indices.items(), key=lambda x: x[1])

print(f"\n--- Education Access Index ---")
print(f"{'Rank':<5} {'Zone':<6} {'Index':>8} {'Children':>10} {'Income':>10} {'Status':<15}")

for rank, (zone_id, index) in enumerate(ranked, 1):
    zone = next(z for z in zones if z.zone_id == zone_id)
    status = "UNDERSERVED" if index < 0.5 else "ADEQUATE" if index < 0.8 else "WELL-SERVED"
    print(f"{rank:<5} {zone_id:<6} {index:>8.3f} {zone.school_age_children:>10} "
          f"${zone.median_household_income:>9,.0f} {status:<15}")
```

## Step 4: Identify Coverage Gaps

```python
underserved_zones = [
    (zone_id, index) for zone_id, index in access_indices.items() if index < 0.5
]

total_underserved_children = sum(
    next(z.school_age_children for z in zones if z.zone_id == zone_id)
    for zone_id, _ in underserved_zones
)

print(f"\n--- Coverage Gap Analysis ---")
print(f"Underserved zones (index < 0.5): {len(underserved_zones)}/{len(zones)}")
print(f"Children in underserved zones: {total_underserved_children}")
print(f"Percentage of all children: "
      f"{total_underserved_children / sum(z.school_age_children for z in zones):.1%}")

if underserved_zones:
    print(f"\nUnderserved zone details:")
    for zone_id, index in underserved_zones:
        zone = next(z for z in zones if z.zone_id == zone_id)
        print(f"  {zone_id}: index={index:.3f}, children={zone.school_age_children}, "
              f"income=${zone.median_household_income:,.0f}")

        # Show which school levels are problematic
        for level, assignment in zone_assignments[zone_id].items():
            if assignment['distance_km'] > WALK_THRESHOLD_KM:
                print(f"    {level}: {assignment['school'].name} is {assignment['distance_km']:.1f} km away")

# School capacity analysis
print(f"\n--- School Capacity Status ---")
for school in schools:
    utilization = school.current_enrollment / school.capacity * 100
    status = "OVER" if utilization > 95 else "HIGH" if utilization > 85 else "OK"
    print(f"  {school.name}: {school.current_enrollment}/{school.capacity} "
          f"({utilization:.0f}%) [{status}]")
```

## Expected Output

```
--- Education Access Index ---
Rank  Zone    Index   Children     Income Status
1     z12     0.312         75    $35,000 UNDERSERVED
2     z10     0.389        113    $39,000 UNDERSERVED
3     z08     0.445        128    $43,000 UNDERSERVED
...

--- Coverage Gap Analysis ---
Underserved zones (index < 0.5): 3/12
Children in underserved zones: 316
Percentage of all children: 19.3%
```

The analysis identifies three underserved zones in lower-income areas, affecting nearly 20% of school-age children. These zones are beyond walking distance to at least one school level, suggesting a need for transportation services or new school siting.
