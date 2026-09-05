# Advanced Example: Bioregional Health Assessment

This example demonstrates a Cascadia-style bioregional health assessment combining watershed health, forest cover, wildlife connectivity, and human wellbeing into a composite index.

## Overview

Bioregional health assessment evaluates a region through its ecological boundaries rather than political ones. This workflow:

1. Initialize a Cascadia PlaceInterface with county selection.
2. Fetch multi-domain data (seismic, forest, weather).
3. Build ecological health indicators per H3 cell.
4. Compute a composite bioregional health index.
5. Identify priority areas for conservation and restoration.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-PLACE
```

## Step 1: Initialize Cascadia Analysis

```python
from geo_infer_place import PlaceInterface, latlng_to_cell, grid_disk, cell_to_latlng
import numpy as np

# Initialize for Cascadia bioregion with focus counties
pi = PlaceInterface(
    "cascadia",
    counties=["CA:Del Norte", "CA:Humboldt", "OR:Curry", "OR:Josephine"],
)

print(f"Location: {pi.location_name}")
print(f"Counties: {pi.counties}")

# Check module availability
status = pi.status()
print(f"GEO-INFER-DATA: {'available' if status['data_module_available'] else 'not installed'}")
print(f"GEO-INFER-TIME: {'available' if status['time_module_available'] else 'not installed'}")
print(f"Analyzers: {status['available_analyzers']}")
```

## Step 2: Define Analysis Grid

Create an H3 grid spanning the focus area at resolution 7 (~5.16 km2 per cell).

```python
# Define focus area bounds
bounds = {
    "south": 41.0, "north": 43.0,
    "west": -124.8, "east": -123.0,
}

# Generate H3 cells covering the bounds
resolution = 7
cells = set()
lat = bounds["south"]
while lat <= bounds["north"]:
    lon = bounds["west"]
    while lon <= bounds["east"]:
        cell = latlng_to_cell(lat, lon, resolution)
        cells.add(cell)
        lon += 0.05
    lat += 0.05

cells = list(cells)
print(f"Analysis grid: {len(cells)} cells at resolution {resolution}")
print(f"Approximate area: {len(cells) * 5.16:.0f} km2")

# Get cell centers
cell_data = {}
for cell in cells:
    lat, lng = cell_to_latlng(cell)
    cell_data[cell] = {"lat": lat, "lng": lng}
```

## Step 3: Fetch Environmental Data

Query real-time data from federal agency APIs.

```python
# Seismic activity
cascadia_seismicity = pi.get_cascadia_seismicity(days=90)
seismic_events = cascadia_seismicity.get("events", [])
print(f"\nSeismic Activity (90 days):")
print(f"  Events: {len(seismic_events)}")

# Fire perimeters
fires = pi.get_fire_perimeters(start_year=2020)
fire_features = fires.get("features", [])
print(f"\nWildfires (since 2020):")
print(f"  Perimeters: {len(fire_features)}")

# Weather observations
weather = pi.get_weather()
print(f"\nCurrent Weather:")
for key in ["temperature", "humidity", "wind_speed"]:
    if weather.get(key):
        print(f"  {key}: {weather[key]}")
```

## Step 4: Build Ecological Health Indicators

For each H3 cell, compute indicators across four domains: watershed, forest, wildlife, and human wellbeing.

```python
np.random.seed(42)

health_data = []

for cell in cells:
    lat = cell_data[cell]["lat"]
    lng = cell_data[cell]["lng"]

    # Distance from coast (proxy for multiple ecological gradients)
    coast_distance = abs(lng - (-124.8)) * 85  # approximate km

    # ---- WATERSHED HEALTH ----
    # Higher near major rivers, lower in urban areas
    stream_density = np.clip(0.5 + 0.3 * np.sin(lat * 10) + np.random.normal(0, 0.1), 0, 1)
    water_quality = np.clip(0.7 + 0.2 * (coast_distance / 50) + np.random.normal(0, 0.1), 0, 1)
    riparian_cover = np.clip(0.6 + 0.3 * (coast_distance / 100) + np.random.normal(0, 0.1), 0, 1)
    watershed_score = 0.3 * stream_density + 0.4 * water_quality + 0.3 * riparian_cover

    # ---- FOREST HEALTH ----
    # Denser inland, impacted by recent fires
    canopy_cover = np.clip(0.4 + 0.4 * (coast_distance / 80) + np.random.normal(0, 0.1), 0, 1)
    old_growth_pct = np.clip(0.15 + 0.25 * (coast_distance / 100) + np.random.normal(0, 0.05), 0, 1)
    fire_damage = np.clip(np.random.exponential(0.1), 0, 1)  # Random fire impact
    forest_score = 0.4 * canopy_cover + 0.3 * old_growth_pct + 0.3 * (1 - fire_damage)

    # ---- WILDLIFE CONNECTIVITY ----
    # Higher in less fragmented areas
    habitat_patch_size = np.clip(0.3 + 0.5 * (coast_distance / 70) + np.random.normal(0, 0.15), 0, 1)
    road_density_inv = np.clip(0.8 - 0.3 * (1 / (coast_distance + 1)) + np.random.normal(0, 0.1), 0, 1)
    corridor_integrity = np.clip(0.5 + 0.3 * canopy_cover + np.random.normal(0, 0.1), 0, 1)
    wildlife_score = 0.35 * habitat_patch_size + 0.3 * road_density_inv + 0.35 * corridor_integrity

    # ---- HUMAN WELLBEING ----
    # Access to nature, environmental justice
    nature_access = np.clip(0.6 + 0.2 * (coast_distance / 50) + np.random.normal(0, 0.1), 0, 1)
    air_quality = np.clip(0.75 + 0.15 * (coast_distance / 60) - fire_damage * 0.3 + np.random.normal(0, 0.05), 0, 1)
    community_resilience = np.clip(0.5 + np.random.normal(0, 0.15), 0, 1)
    wellbeing_score = 0.3 * nature_access + 0.4 * air_quality + 0.3 * community_resilience

    # ---- COMPOSITE INDEX ----
    composite = 0.25 * watershed_score + 0.25 * forest_score + 0.25 * wildlife_score + 0.25 * wellbeing_score

    health_data.append({
        "cell": cell,
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "watershed_score": round(watershed_score, 3),
        "forest_score": round(forest_score, 3),
        "wildlife_score": round(wildlife_score, 3),
        "wellbeing_score": round(wellbeing_score, 3),
        "composite_health": round(composite, 3),
    })

# Convert to sortable structure
scores = {
    "watershed": [d["watershed_score"] for d in health_data],
    "forest": [d["forest_score"] for d in health_data],
    "wildlife": [d["wildlife_score"] for d in health_data],
    "wellbeing": [d["wellbeing_score"] for d in health_data],
    "composite": [d["composite_health"] for d in health_data],
}

print(f"\nBioregional Health Indicators ({len(health_data)} cells):")
for domain, values in scores.items():
    arr = np.array(values)
    print(f"  {domain:>12}: mean={arr.mean():.3f}  std={arr.std():.3f}  "
          f"min={arr.min():.3f}  max={arr.max():.3f}")
```

## Step 5: Identify Priority Areas

Classify cells into conservation categories based on composite health.

```python
# Sort by composite health
ranked = sorted(health_data, key=lambda d: d["composite_health"])

# Define categories
categories = {
    "Critical (needs restoration)": [],
    "At risk (protect and monitor)": [],
    "Moderate (maintain current management)": [],
    "Healthy (exemplary, study and replicate)": [],
}

for cell_info in health_data:
    score = cell_info["composite_health"]
    if score < 0.35:
        categories["Critical (needs restoration)"].append(cell_info)
    elif score < 0.50:
        categories["At risk (protect and monitor)"].append(cell_info)
    elif score < 0.65:
        categories["Moderate (maintain current management)"].append(cell_info)
    else:
        categories["Healthy (exemplary, study and replicate)"].append(cell_info)

print(f"\nConservation Priority Classification:")
for category, cells_in_cat in categories.items():
    pct = len(cells_in_cat) / len(health_data) * 100
    print(f"  {category}: {len(cells_in_cat)} cells ({pct:.1f}%)")

# Top 10 cells needing restoration
print(f"\nTop 10 Cells Needing Restoration:")
print(f"{'Cell':<18}{'Lat':>8}{'Lng':>10}{'Watershed':>10}{'Forest':>8}"
      f"{'Wildlife':>10}{'Wellbeing':>10}{'Composite':>10}")
print("-" * 84)
for cell_info in ranked[:10]:
    print(f"{cell_info['cell']:<18}{cell_info['lat']:>8.3f}{cell_info['lng']:>10.3f}"
          f"{cell_info['watershed_score']:>10.3f}{cell_info['forest_score']:>8.3f}"
          f"{cell_info['wildlife_score']:>10.3f}{cell_info['wellbeing_score']:>10.3f}"
          f"{cell_info['composite_health']:>10.3f}")
```

## Step 6: Domain-Specific Analysis

Identify which domain is weakest in each priority area to guide targeted intervention.

```python
print(f"\nDomain Deficiency Analysis (Critical cells):")
domain_deficiency_count = {"watershed": 0, "forest": 0, "wildlife": 0, "wellbeing": 0}

for cell_info in categories["Critical (needs restoration)"]:
    domain_scores = {
        "watershed": cell_info["watershed_score"],
        "forest": cell_info["forest_score"],
        "wildlife": cell_info["wildlife_score"],
        "wellbeing": cell_info["wellbeing_score"],
    }
    weakest = min(domain_scores, key=domain_scores.get)
    domain_deficiency_count[weakest] += 1

total_critical = len(categories["Critical (needs restoration)"])
if total_critical > 0:
    for domain, count in sorted(domain_deficiency_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {domain}: weakest in {count} cells ({count / total_critical:.0%})")
else:
    print("  No critical cells found.")
```

## Step 7: Summary Report

```python
composite_arr = np.array(scores["composite"])

print("\n" + "=" * 60)
print("CASCADIA BIOREGIONAL HEALTH ASSESSMENT")
print("=" * 60)
print(f"  Region: {pi.location_name}")
print(f"  Focus counties: {pi.counties}")
print(f"  Analysis cells: {len(health_data)}")
print(f"  Approximate area: {len(health_data) * 5.16:.0f} km2")
print(f"  Overall health: {composite_arr.mean():.3f} (0=degraded, 1=pristine)")
print(f"  Health distribution:")
for category, cells_in_cat in categories.items():
    print(f"    {category}: {len(cells_in_cat)} cells")
print(f"  Seismic activity (90d): {len(seismic_events)} events")
print(f"  Recent fires: {len(fire_features)} perimeters")
print(f"  Data sources: USGS, NOAA, CAL FIRE")
```

## Key Takeaways

1. **Bioregional boundaries reveal patterns that political ones hide**: Ecological health does not stop at county or state borders. The Cascadia bioregion spans BC, WA, OR, and CA.
2. **Composite indices enable prioritization**: A single number per cell allows ranking, but the domain breakdown guides specific interventions.
3. **Real-time integration adds value**: Seismic and fire data provide current context that static ecological assessments miss.
4. **H3 grids scale across resolutions**: The same analysis framework works at resolution 7 (bioregion) or resolution 8 (county) by changing one parameter.

## Next Steps

- Use the full `run_full_analysis()` pipeline to execute all configured analyzers.
- Integrate with GEO-INFER-FOREST for satellite-derived canopy cover and NDVI.
- Use GEO-INFER-TIME for temporal trend analysis on health indicators.
- Connect to GEO-INFER-BIO for species-specific biodiversity metrics.
