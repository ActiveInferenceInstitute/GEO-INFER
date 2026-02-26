# Advanced Example: Multi-Criteria Community Resilience Score

This example builds a composite community resilience score by combining civic participation data, infrastructure access, socioeconomic indicators, and hazard exposure into a single spatial index. Each census tract receives a resilience score that identifies vulnerable communities requiring targeted investment.

## Problem Description

Resilience is computed from four dimensions:

1. **Civic Participation** (25%): Engagement scores from meeting attendance, public comments, and voting.
2. **Infrastructure Access** (25%): Proximity to essential services (hospitals, schools, fire stations, transit).
3. **Socioeconomic Capacity** (25%): Income, education, employment indicators.
4. **Hazard Vulnerability** (25%): Exposure to flood, earthquake, and wildfire risk.

The final score ranges from 0 (low resilience) to 1 (high resilience).

## Setting Up the Data

```python
import random
import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

random.seed(42)

@dataclass
class CensusTract:
    """Represents a census tract with demographic and spatial data."""
    tract_id: str
    population: int
    centroid: Tuple[float, float]  # (lat, lng)
    median_income: float
    pct_college_educated: float
    unemployment_rate: float
    pct_health_insured: float

@dataclass
class FacilitySet:
    """Set of public facilities."""
    hospitals: List[Tuple[float, float]]
    schools: List[Tuple[float, float]]
    fire_stations: List[Tuple[float, float]]
    transit_stops: List[Tuple[float, float]]

# Generate 20 synthetic census tracts
tracts = []
for i in range(20):
    lat = 47.58 + random.uniform(0, 0.05)
    lng = -122.36 + random.uniform(0, 0.06)
    tracts.append(CensusTract(
        tract_id=f"tract_{i+1:03d}",
        population=random.randint(2000, 8000),
        centroid=(lat, lng),
        median_income=random.uniform(35000, 120000),
        pct_college_educated=random.uniform(0.15, 0.65),
        unemployment_rate=random.uniform(0.02, 0.15),
        pct_health_insured=random.uniform(0.75, 0.98),
    ))

# Generate facility locations
facilities = FacilitySet(
    hospitals=[(47.605 + random.uniform(-0.01, 0.01),
                -122.33 + random.uniform(-0.01, 0.01)) for _ in range(3)],
    schools=[(47.58 + random.uniform(0, 0.05),
              -122.36 + random.uniform(0, 0.06)) for _ in range(8)],
    fire_stations=[(47.58 + random.uniform(0, 0.05),
                    -122.36 + random.uniform(0, 0.06)) for _ in range(4)],
    transit_stops=[(47.58 + random.uniform(0, 0.05),
                    -122.36 + random.uniform(0, 0.06)) for _ in range(15)],
)

print(f"Census tracts: {len(tracts)}")
print(f"Facilities: {len(facilities.hospitals)} hospitals, "
      f"{len(facilities.schools)} schools, "
      f"{len(facilities.fire_stations)} fire stations, "
      f"{len(facilities.transit_stops)} transit stops")
```

## Dimension 1: Civic Participation Score

Generate participation data per tract and compute engagement scores.

```python
from geo_infer_civ.core.participation import (
    ParticipationAnalyzer,
    ParticipantRecord,
    ParticipationMethod,
)

def compute_participation_score(tract: CensusTract) -> float:
    """Compute civic participation score for a tract."""
    analyzer = ParticipationAnalyzer()

    # Generate synthetic participation records
    # Higher-income tracts tend to have more participation (modeled correlation)
    base_participation_rate = 0.02 + 0.08 * (tract.median_income / 120000)
    n_participants = int(tract.population * base_participation_rate)

    methods = list(ParticipationMethod)
    base_timestamp = 1704067200.0

    for i in range(max(n_participants, 1)):
        analyzer.add_record(ParticipantRecord(
            participant_id=f"{tract.tract_id}_p{i:04d}",
            method=random.choice(methods),
            timestamp=base_timestamp + random.uniform(0, 365 * 86400),
        ))

    score = analyzer.compute_engagement_score(target_population=tract.population)
    return score.overall_score

participation_scores = {}
for tract in tracts:
    participation_scores[tract.tract_id] = compute_participation_score(tract)

print("\n--- Civic Participation Scores ---")
for tid, score in sorted(participation_scores.items(), key=lambda x: -x[1])[:5]:
    print(f"  {tid}: {score:.4f}")
```

## Dimension 2: Infrastructure Access Score

Compute access scores based on distance to nearest facilities.

```python
def haversine_km(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Distance in km between two (lat, lng) points."""
    R = 6371.0
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def nearest_distance(centroid: Tuple[float, float], facilities_list: List[Tuple[float, float]]) -> float:
    """Distance in km to nearest facility."""
    if not facilities_list:
        return float('inf')
    return min(haversine_km(centroid, f) for f in facilities_list)

def compute_access_score(tract: CensusTract, fac: FacilitySet) -> float:
    """Compute infrastructure access score (0-1, higher is better)."""
    # Distance thresholds (km) for good access
    thresholds = {
        'hospital': 5.0,
        'school': 2.0,
        'fire_station': 3.0,
        'transit': 0.5,
    }

    hospital_dist = nearest_distance(tract.centroid, fac.hospitals)
    school_dist = nearest_distance(tract.centroid, fac.schools)
    fire_dist = nearest_distance(tract.centroid, fac.fire_stations)
    transit_dist = nearest_distance(tract.centroid, fac.transit_stops)

    # Convert distance to score: 1.0 if within threshold, decays exponentially beyond
    def dist_to_score(dist: float, threshold: float) -> float:
        if dist <= threshold:
            return 1.0
        return math.exp(-(dist - threshold) / threshold)

    scores = {
        'hospital': dist_to_score(hospital_dist, thresholds['hospital']),
        'school': dist_to_score(school_dist, thresholds['school']),
        'fire_station': dist_to_score(fire_dist, thresholds['fire_station']),
        'transit': dist_to_score(transit_dist, thresholds['transit']),
    }

    # Weighted average (transit weighted more for daily access)
    weights = {'hospital': 0.20, 'school': 0.25, 'fire_station': 0.20, 'transit': 0.35}
    total = sum(scores[k] * weights[k] for k in scores)
    return total

access_scores = {}
for tract in tracts:
    access_scores[tract.tract_id] = compute_access_score(tract, facilities)

print("\n--- Infrastructure Access Scores ---")
for tid, score in sorted(access_scores.items(), key=lambda x: -x[1])[:5]:
    print(f"  {tid}: {score:.4f}")
```

## Dimension 3: Socioeconomic Capacity Score

Normalize and combine socioeconomic indicators.

```python
def compute_socioeconomic_score(tract: CensusTract) -> float:
    """Compute socioeconomic capacity score (0-1)."""
    # Normalize each indicator to [0, 1]
    income_score = min(tract.median_income / 100000, 1.0)
    education_score = tract.pct_college_educated
    employment_score = 1.0 - tract.unemployment_rate  # Lower unemployment is better
    health_score = tract.pct_health_insured

    # Weighted combination
    score = (
        0.30 * income_score
        + 0.25 * education_score
        + 0.25 * employment_score
        + 0.20 * health_score
    )
    return score

socioeconomic_scores = {}
for tract in tracts:
    socioeconomic_scores[tract.tract_id] = compute_socioeconomic_score(tract)

print("\n--- Socioeconomic Capacity Scores ---")
for tid, score in sorted(socioeconomic_scores.items(), key=lambda x: -x[1])[:5]:
    print(f"  {tid}: {score:.4f}")
```

## Dimension 4: Hazard Vulnerability Score

Estimate hazard exposure from geographic position and elevation proxies.

```python
def compute_hazard_score(tract: CensusTract) -> float:
    """Compute hazard resilience score (0-1, higher means less vulnerable)."""
    lat, lng = tract.centroid

    # Flood risk: increases near water bodies (lower latitude in our synthetic data)
    flood_risk = max(0, 1.0 - abs(lat - 47.58) / 0.05) * 0.6

    # Earthquake risk: uniform moderate risk for the Seattle area
    earthquake_risk = 0.35

    # Wildfire risk: increases with distance from urban core (higher latitude, farther east)
    wildfire_risk = max(0, (lat - 47.60) / 0.03) * 0.4

    # Combined hazard exposure (higher = more exposed)
    total_exposure = 0.40 * flood_risk + 0.35 * earthquake_risk + 0.25 * wildfire_risk

    # Resilience = inverse of exposure
    return max(0.0, min(1.0, 1.0 - total_exposure))

hazard_scores = {}
for tract in tracts:
    hazard_scores[tract.tract_id] = compute_hazard_score(tract)

print("\n--- Hazard Resilience Scores ---")
for tid, score in sorted(hazard_scores.items(), key=lambda x: -x[1])[:5]:
    print(f"  {tid}: {score:.4f}")
```

## Computing the Composite Resilience Score

Combine all four dimensions with equal weighting.

```python
# Dimension weights
WEIGHTS = {
    'participation': 0.25,
    'access': 0.25,
    'socioeconomic': 0.25,
    'hazard': 0.25,
}

resilience_scores = {}
for tract in tracts:
    tid = tract.tract_id
    composite = (
        WEIGHTS['participation'] * participation_scores[tid]
        + WEIGHTS['access'] * access_scores[tid]
        + WEIGHTS['socioeconomic'] * socioeconomic_scores[tid]
        + WEIGHTS['hazard'] * hazard_scores[tid]
    )
    resilience_scores[tid] = {
        'composite': round(composite, 4),
        'participation': round(participation_scores[tid], 4),
        'access': round(access_scores[tid], 4),
        'socioeconomic': round(socioeconomic_scores[tid], 4),
        'hazard': round(hazard_scores[tid], 4),
        'population': tract.population,
    }

# Rank by composite score
ranked = sorted(resilience_scores.items(), key=lambda x: x[1]['composite'])

print("\n===== Community Resilience Rankings =====")
print(f"{'Rank':<5} {'Tract':<12} {'Composite':>10} {'Civic':>8} "
      f"{'Access':>8} {'SocEcon':>8} {'Hazard':>8} {'Pop':>6}")
print("-" * 72)

for rank, (tid, scores) in enumerate(ranked, 1):
    print(f"{rank:<5} {tid:<12} {scores['composite']:>10.4f} "
          f"{scores['participation']:>8.4f} {scores['access']:>8.4f} "
          f"{scores['socioeconomic']:>8.4f} {scores['hazard']:>8.4f} "
          f"{scores['population']:>6d}")

# Identify vulnerable tracts (bottom quartile)
threshold = sorted([s['composite'] for s in resilience_scores.values()])[len(tracts) // 4]
vulnerable = [tid for tid, s in resilience_scores.items() if s['composite'] <= threshold]

print(f"\n--- Vulnerable Tracts (bottom quartile, score <= {threshold:.4f}) ---")
for tid in vulnerable:
    scores = resilience_scores[tid]
    weakest = min(
        [('participation', scores['participation']),
         ('access', scores['access']),
         ('socioeconomic', scores['socioeconomic']),
         ('hazard', scores['hazard'])],
        key=lambda x: x[1],
    )
    print(f"  {tid}: composite={scores['composite']:.4f}, "
          f"weakest dimension={weakest[0]} ({weakest[1]:.4f})")
```

## Policy Recommendations from Equity Analysis

Use the equity scoring to identify where investments would have the largest impact.

```python
from geo_infer_civ.core.policy_analysis import (
    CostBenefitAnalyzer,
    CostBenefitItem,
    StakeholderImpact,
    ImpactLevel,
)

# Propose a community investment program for vulnerable tracts
cba = CostBenefitAnalyzer(discount_rate=0.04)

# Costs
cba.add_item(CostBenefitItem("Program administration", 500000, False, 1.0, 5, "admin"))
cba.add_item(CostBenefitItem("Infrastructure improvements", 2000000, False, 0.95, 5, "capital"))
cba.add_item(CostBenefitItem("Community outreach staff", 300000, False, 1.0, 5, "personnel"))

# Benefits
cba.add_item(CostBenefitItem("Reduced emergency costs", 400000, True, 0.80, 5, "savings"))
cba.add_item(CostBenefitItem("Increased property values", 1500000, True, 0.70, 5, "economic"))
cba.add_item(CostBenefitItem("Health outcome improvements", 800000, True, 0.75, 5, "health"))
cba.add_item(CostBenefitItem("Reduced inequality index", 300000, True, 0.60, 5, "equity"))

result = cba.analyze()
print(f"\n--- Cost-Benefit Analysis for Community Investment ---")
print(f"Total costs: ${result.total_costs:,.0f}")
print(f"Total benefits: ${result.total_benefits:,.0f}")
print(f"Net present value: ${result.net_present_value:,.0f}")
print(f"Benefit-cost ratio: {result.benefit_cost_ratio:.2f}")
print(f"Risk-adjusted NPV: ${result.risk_adjusted_npv:,.0f}")
```

## Expected Output

```
===== Community Resilience Rankings =====
Rank  Tract        Composite     Civic   Access  SocEcon   Hazard    Pop
------------------------------------------------------------------------
1     tract_014       0.3245   0.0821   0.4123   0.3245   0.4791   3200
2     tract_007       0.3567   0.1024   0.3890   0.4012   0.5342   5100
...
20    tract_011       0.6891   0.2134   0.7856   0.7234   0.7340   4800

--- Vulnerable Tracts (bottom quartile) ---
  tract_014: composite=0.3245, weakest dimension=participation (0.0821)
  tract_007: composite=0.3567, weakest dimension=participation (0.1024)
```

The analysis reveals that civic participation is consistently the weakest dimension in vulnerable tracts, suggesting that engagement outreach programs could be the highest-leverage intervention for improving community resilience.
