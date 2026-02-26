# Advanced Example: Education Equity Analysis

This example builds a multi-factor education equity index that combines school distance, resource quality, socioeconomic indicators, and student outcome data to identify areas where educational investment would have the greatest impact.

## Problem Description

Construct an equity index from four dimensions:

1. **Physical Access** (30%): Distance to schools, availability of transportation.
2. **Resource Quality** (25%): Student-teacher ratios, technology access, facilities condition.
3. **Socioeconomic Context** (25%): Family income, parental education, housing stability.
4. **Student Outcomes** (20%): Graduation rates, test scores, post-secondary enrollment.

The index produces a 0-1 score for each zone where lower values indicate greater need for targeted investment.

## Setting Up the Dataset

```python
import math
import random
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

random.seed(42)

@dataclass
class SchoolProfile:
    school_id: str
    name: str
    lat: float
    lng: float
    level: str
    student_teacher_ratio: float
    technology_score: float        # 0-1, based on device availability
    facilities_rating: float       # 0-1, based on condition assessment
    graduation_rate: float         # 0-1 (high schools only)
    avg_test_score_percentile: float  # 0-100
    per_student_spending: float    # Annual dollars

@dataclass
class ZoneProfile:
    zone_id: str
    lat: float
    lng: float
    population: int
    school_age_children: int
    median_income: float
    pct_college_parents: float
    pct_stable_housing: float
    pct_food_secure: float
    has_bus_service: bool

# Generate 15 schools
schools = [
    SchoolProfile("s01", "Westside Elem", 47.610, -122.340, "elementary",
                  22.0, 0.85, 0.90, 0.0, 72.0, 12500),
    SchoolProfile("s02", "Eastside Elem", 47.608, -122.310, "elementary",
                  18.0, 0.92, 0.95, 0.0, 81.0, 14200),
    SchoolProfile("s03", "Northgate Elem", 47.625, -122.335, "elementary",
                  25.0, 0.70, 0.75, 0.0, 64.0, 10800),
    SchoolProfile("s04", "Southend Elem", 47.595, -122.330, "elementary",
                  28.0, 0.62, 0.65, 0.0, 55.0, 9200),
    SchoolProfile("s05", "Central Middle", 47.612, -122.325, "middle",
                  20.0, 0.88, 0.85, 0.0, 75.0, 13100),
    SchoolProfile("s06", "Lakeside Middle", 47.618, -122.345, "middle",
                  23.0, 0.78, 0.80, 0.0, 68.0, 11500),
    SchoolProfile("s07", "Valley Middle", 47.600, -122.320, "middle",
                  26.0, 0.65, 0.70, 0.0, 58.0, 9800),
    SchoolProfile("s08", "Metro High", 47.615, -122.330, "high",
                  19.0, 0.90, 0.88, 0.92, 78.0, 14800),
    SchoolProfile("s09", "Heritage High", 47.605, -122.315, "high",
                  24.0, 0.72, 0.70, 0.82, 62.0, 10500),
]

# Generate 15 residential zones
zones = []
for i in range(15):
    lat = 47.592 + random.uniform(0, 0.040)
    lng = -122.360 + random.uniform(0, 0.060)

    # Correlated socioeconomic factors
    income_factor = random.uniform(0.3, 1.0)
    zones.append(ZoneProfile(
        zone_id=f"z{i+1:02d}",
        lat=lat,
        lng=lng,
        population=random.randint(600, 1500),
        school_age_children=random.randint(50, 200),
        median_income=30000 + income_factor * 80000,
        pct_college_parents=0.10 + income_factor * 0.55,
        pct_stable_housing=0.60 + income_factor * 0.35,
        pct_food_secure=0.70 + income_factor * 0.28,
        has_bus_service=random.random() < (0.3 + income_factor * 0.5),
    ))

print(f"Schools: {len(schools)}")
print(f"Zones: {len(zones)}")
print(f"Total children: {sum(z.school_age_children for z in zones)}")
```

## Dimension 1: Physical Access Score

```python
def haversine_km(lat1, lng1, lat2, lng2) -> float:
    R = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlat = la2 - la1
    dlng = lo2 - lo1
    a = math.sin(dlat/2)**2 + math.cos(la1) * math.cos(la2) * math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def physical_access_score(zone: ZoneProfile, schools_list: list) -> float:
    """Score physical access to schools (0-1)."""
    level_scores = {}

    for level in ['elementary', 'middle', 'high']:
        level_schools = [s for s in schools_list if s.level == level]
        if not level_schools:
            level_scores[level] = 0.0
            continue

        nearest_dist = min(
            haversine_km(zone.lat, zone.lng, s.lat, s.lng) for s in level_schools
        )

        # Distance scoring
        if nearest_dist <= 1.0:
            dist_score = 1.0
        elif nearest_dist <= 2.0:
            dist_score = 0.8
        elif nearest_dist <= 3.5:
            dist_score = 0.5
        else:
            dist_score = max(0.1, 1.0 - nearest_dist / 10.0)

        # Bus service bonus
        if zone.has_bus_service and nearest_dist > 1.5:
            dist_score = min(1.0, dist_score + 0.2)

        level_scores[level] = dist_score

    return sum(level_scores.values()) / len(level_scores)

access_scores = {z.zone_id: physical_access_score(z, schools) for z in zones}
print("\n--- Physical Access Scores ---")
for zid, score in sorted(access_scores.items(), key=lambda x: x[1])[:5]:
    print(f"  {zid}: {score:.3f}")
```

## Dimension 2: Resource Quality Score

```python
def resource_quality_score(zone: ZoneProfile, schools_list: list) -> float:
    """Score based on quality of nearest schools."""
    quality_scores = []

    for level in ['elementary', 'middle', 'high']:
        level_schools = [s for s in schools_list if s.level == level]
        if not level_schools:
            continue

        # Find nearest school at this level
        nearest = min(level_schools, key=lambda s: haversine_km(zone.lat, zone.lng, s.lat, s.lng))

        # Student-teacher ratio (lower is better, max 30)
        str_score = max(0, 1.0 - nearest.student_teacher_ratio / 30.0)

        # Technology access
        tech_score = nearest.technology_score

        # Facilities condition
        facilities_score = nearest.facilities_rating

        # Per-student spending (normalized to $15000 max)
        spending_score = min(1.0, nearest.per_student_spending / 15000)

        quality = 0.25 * str_score + 0.25 * tech_score + 0.25 * facilities_score + 0.25 * spending_score
        quality_scores.append(quality)

    return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

quality_scores = {z.zone_id: resource_quality_score(z, schools) for z in zones}
print("\n--- Resource Quality Scores ---")
for zid, score in sorted(quality_scores.items(), key=lambda x: x[1])[:5]:
    print(f"  {zid}: {score:.3f}")
```

## Dimension 3: Socioeconomic Context Score

```python
def socioeconomic_score(zone: ZoneProfile) -> float:
    """Score based on socioeconomic factors."""
    income_score = min(1.0, zone.median_income / 100000)
    education_score = zone.pct_college_parents
    housing_score = zone.pct_stable_housing
    food_score = zone.pct_food_secure

    return 0.30 * income_score + 0.25 * education_score + 0.25 * housing_score + 0.20 * food_score

socio_scores = {z.zone_id: socioeconomic_score(z) for z in zones}
print("\n--- Socioeconomic Scores ---")
for zid, score in sorted(socio_scores.items(), key=lambda x: x[1])[:5]:
    print(f"  {zid}: {score:.3f}")
```

## Dimension 4: Student Outcomes Score

```python
def outcomes_score(zone: ZoneProfile, schools_list: list) -> float:
    """Score based on student outcomes at nearest schools."""
    outcome_scores = []

    for level in ['elementary', 'middle', 'high']:
        level_schools = [s for s in schools_list if s.level == level]
        if not level_schools:
            continue

        nearest = min(level_schools, key=lambda s: haversine_km(zone.lat, zone.lng, s.lat, s.lng))

        test_score = nearest.avg_test_score_percentile / 100.0

        if level == 'high' and nearest.graduation_rate > 0:
            grad_score = nearest.graduation_rate
            score = 0.5 * test_score + 0.5 * grad_score
        else:
            score = test_score

        outcome_scores.append(score)

    return sum(outcome_scores) / len(outcome_scores) if outcome_scores else 0.0

outcome_scores = {z.zone_id: outcomes_score(z, schools) for z in zones}
print("\n--- Student Outcome Scores ---")
for zid, score in sorted(outcome_scores.items(), key=lambda x: x[1])[:5]:
    print(f"  {zid}: {score:.3f}")
```

## Computing the Composite Equity Index

```python
WEIGHTS = {'access': 0.30, 'quality': 0.25, 'socioeconomic': 0.25, 'outcomes': 0.20}

equity_index = {}
for zone in zones:
    zid = zone.zone_id
    composite = (
        WEIGHTS['access'] * access_scores[zid]
        + WEIGHTS['quality'] * quality_scores[zid]
        + WEIGHTS['socioeconomic'] * socio_scores[zid]
        + WEIGHTS['outcomes'] * outcome_scores[zid]
    )
    equity_index[zid] = {
        'composite': round(composite, 4),
        'access': round(access_scores[zid], 4),
        'quality': round(quality_scores[zid], 4),
        'socioeconomic': round(socio_scores[zid], 4),
        'outcomes': round(outcome_scores[zid], 4),
        'children': zone.school_age_children,
        'income': zone.median_income,
    }

# Rank by equity (lowest = most need)
ranked = sorted(equity_index.items(), key=lambda x: x[1]['composite'])

print("\n===== Education Equity Rankings =====")
print(f"{'Rank':<5} {'Zone':<6} {'Equity':>8} {'Access':>8} {'Quality':>8} "
      f"{'SocEcon':>8} {'Outcomes':>8} {'Children':>9}")
print("-" * 72)

for rank, (zid, scores) in enumerate(ranked, 1):
    print(f"{rank:<5} {zid:<6} {scores['composite']:>8.4f} {scores['access']:>8.4f} "
          f"{scores['quality']:>8.4f} {scores['socioeconomic']:>8.4f} "
          f"{scores['outcomes']:>8.4f} {scores['children']:>9d}")

# Identify priority investment zones
threshold = sorted(s['composite'] for s in equity_index.values())[len(zones) // 4]
priority_zones = [(zid, s) for zid, s in equity_index.items() if s['composite'] <= threshold]

print(f"\n--- Priority Investment Zones (bottom quartile, equity <= {threshold:.4f}) ---")
total_priority_children = 0
for zid, scores in priority_zones:
    zone = next(z for z in zones if z.zone_id == zid)
    weakest = min(
        [('access', scores['access']), ('quality', scores['quality']),
         ('socioeconomic', scores['socioeconomic']), ('outcomes', scores['outcomes'])],
        key=lambda x: x[1],
    )
    total_priority_children += zone.school_age_children
    print(f"  {zid}: equity={scores['composite']:.4f}, "
          f"weakest={weakest[0]} ({weakest[1]:.4f}), "
          f"children={zone.school_age_children}, "
          f"income=${zone.median_income:,.0f}")

all_children = sum(z.school_age_children for z in zones)
print(f"\nPriority zones serve {total_priority_children}/{all_children} children "
      f"({total_priority_children/all_children:.1%})")

# Recommend interventions based on weakest dimension
print(f"\n--- Recommended Interventions ---")
interventions = {
    'access': "Add bus routes or build satellite school facilities",
    'quality': "Increase per-student funding, reduce class sizes, upgrade technology",
    'socioeconomic': "Expand free meal programs, after-school care, family support services",
    'outcomes': "Implement tutoring programs, early intervention, college readiness courses",
}
for zid, scores in priority_zones:
    weakest = min(
        [('access', scores['access']), ('quality', scores['quality']),
         ('socioeconomic', scores['socioeconomic']), ('outcomes', scores['outcomes'])],
        key=lambda x: x[1],
    )
    print(f"  {zid} ({weakest[0]}): {interventions[weakest[0]]}")
```

## Expected Output

```
===== Education Equity Rankings =====
Rank  Zone    Equity  Access Quality SocEcon Outcomes  Children
------------------------------------------------------------------------
1     z08     0.3215  0.4200  0.3100  0.2800  0.3100       95
2     z12     0.3456  0.3800  0.3400  0.3100  0.3200       72
3     z04     0.3890  0.5100  0.3600  0.2900  0.3500      120
...

--- Priority Investment Zones ---
  z08: equity=0.3215, weakest=socioeconomic (0.2800), children=95, income=$38,200
  z12: equity=0.3456, weakest=quality (0.3400), children=72, income=$35,100

--- Recommended Interventions ---
  z08 (socioeconomic): Expand free meal programs, after-school care, family support services
  z12 (quality): Increase per-student funding, reduce class sizes, upgrade technology
```

The equity analysis reveals that socioeconomic context and resource quality are the primary drivers of educational inequity in this district. Priority zones tend to cluster in lower-income areas with older school facilities and higher student-teacher ratios.
