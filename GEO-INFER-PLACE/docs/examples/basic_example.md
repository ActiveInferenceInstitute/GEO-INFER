# Basic Example: Place Characterization

This example demonstrates how to define a neighborhood's identity from multiple data layers including land use, amenities, demographics, and ecological context using GEO-INFER-PLACE.

## Overview

Place characterization involves overlaying multiple spatial datasets on a location to understand its unique identity. This workflow:

1. Define a place boundary using H3 cells.
2. Query environmental data (earthquakes, weather, tides).
3. Combine data layers into a place identity profile.
4. Generate a characterization summary.

## Prerequisites

```bash
uv pip install -e ./GEO-INFER-PLACE
```

## Step 1: Define Place Boundary with H3

Use H3 hexagonal cells to define the spatial extent of analysis for Crescent City, the county seat of Del Norte County.

```python
from geo_infer_place import (
    PlaceInterface,
    latlng_to_cell,
    cell_to_latlng,
    grid_disk,
    cell_area,
)

# Crescent City center point
crescent_city_lat = 41.756
crescent_city_lon = -124.202

# Create H3 cells at resolution 8 (~0.74 km2 per cell)
center_cell = latlng_to_cell(crescent_city_lat, crescent_city_lon, 8)
print(f"Center cell: {center_cell}")

# Define analysis area as k=3 ring (~37 cells, ~27 km2)
analysis_cells = grid_disk(center_cell, 3)
print(f"Analysis cells: {len(analysis_cells)}")

# Calculate total analysis area
total_area_km2 = len(analysis_cells) * cell_area(center_cell, unit="km^2")
print(f"Total area: {total_area_km2:.1f} km2")

# Get cell centers for data queries
cell_centers = {}
for cell in analysis_cells:
    lat, lng = cell_to_latlng(cell)
    cell_centers[cell] = {"lat": lat, "lng": lng}
```

## Step 2: Query Environmental Data

Use the `PlaceInterface` to pull real-time environmental data.

```python
pi = PlaceInterface("del_norte")

# Fetch recent seismic activity
earthquakes = pi.get_earthquakes()
eq_features = earthquakes.get("features", [])
print(f"\nSeismic Activity:")
print(f"  Recent earthquakes: {len(eq_features)}")

if eq_features:
    magnitudes = [f["properties"]["mag"] for f in eq_features if f["properties"].get("mag")]
    if magnitudes:
        print(f"  Magnitude range: {min(magnitudes):.1f} - {max(magnitudes):.1f}")

# Fetch Cascadia subduction zone data
cascadia = pi.get_cascadia_seismicity(days=30)
cascadia_events = cascadia.get("events", [])
print(f"  Cascadia events (30d): {len(cascadia_events)}")

# Fetch tide data
tides = pi.get_tide_data()
tide_stations = tides.get("stations", [])
print(f"\nCoastal Data:")
print(f"  Tide stations: {len(tide_stations)}")

# Fetch weather
weather = pi.get_weather()
print(f"\nWeather:")
print(f"  Station: {weather.get('station', 'N/A')}")
if weather.get("temperature"):
    print(f"  Temperature: {weather['temperature']}")
```

## Step 3: Build Place Identity Layers

Create a multi-layer characterization of the place. In a production system, each layer would come from a real data source (census, land cover, OSM amenities). Here we define a structured place profile.

```python
import numpy as np

# Define place identity layers
place_identity = {
    "name": "Crescent City, Del Norte County, CA",
    "center": {"lat": crescent_city_lat, "lon": crescent_city_lon},
    "h3_resolution": 8,
    "cell_count": len(analysis_cells),
    "area_km2": round(total_area_km2, 1),

    # Ecological context
    "ecology": {
        "ecoregion": "Klamath Mountains / California High North Coast Range",
        "primary_vegetation": "Coastal Redwood and Mixed Evergreen Forest",
        "watershed": "Smith River / Klamath River",
        "notable_species": ["Coastal Redwood", "Chinook Salmon", "Marbled Murrelet"],
        "protected_areas": ["Jedediah Smith Redwoods State Park", "Tolowa Dunes State Park"],
    },

    # Hazard profile
    "hazards": {
        "seismic": {
            "fault_zone": "Cascadia Subduction Zone",
            "recent_events": len(eq_features),
            "tsunami_risk": "High (coastal location near subduction zone)",
        },
        "wildfire": {
            "fire_regime": "Mixed severity, 30-100 year return interval",
            "recent_fires_nearby": True,
        },
        "coastal": {
            "erosion_risk": "Moderate to High",
            "sea_level_exposure": "Significant for low-lying areas",
        },
    },

    # Demographics (representative values)
    "demographics": {
        "population_estimate": 7800,
        "density_per_km2": round(7800 / total_area_km2, 1),
        "median_income": 35000,
        "primary_industries": ["Fishing", "Forestry", "Tourism", "Government"],
    },

    # Infrastructure
    "infrastructure": {
        "road_connectivity": "US-101 (primary highway)",
        "nearest_airport": "Jack McNamara Field (CEC)",
        "harbor": "Crescent City Harbor",
        "hospital": "Sutter Coast Hospital",
    },
}

print("\nPlace Identity Summary:")
print(f"  Name: {place_identity['name']}")
print(f"  Area: {place_identity['area_km2']} km2")
print(f"  Population: ~{place_identity['demographics']['population_estimate']:,}")
print(f"  Ecoregion: {place_identity['ecology']['ecoregion']}")
print(f"  Primary hazard: {place_identity['hazards']['seismic']['fault_zone']}")
```

## Step 4: Per-Cell Characterization

Assign attributes to each H3 cell based on its position relative to key features.

```python
cell_profiles = []

for cell in analysis_cells:
    lat, lng = cell_centers[cell]["lat"], cell_centers[cell]["lng"]

    # Distance from coast (proxy: longitude)
    distance_from_coast_km = abs(lng - (-124.35)) * 85  # rough km conversion

    # Elevation proxy (increases inland)
    elevation_estimate = max(0, distance_from_coast_km * 5 + np.random.normal(0, 3))

    # Land use classification based on position
    if distance_from_coast_km < 1:
        land_use = "coastal"
        tsunami_zone = True
    elif distance_from_coast_km < 3:
        land_use = "urban_residential" if abs(lat - crescent_city_lat) < 0.02 else "rural"
        tsunami_zone = elevation_estimate < 10
    else:
        land_use = "forest"
        tsunami_zone = False

    cell_profiles.append({
        "cell": cell,
        "lat": round(lat, 4),
        "lng": round(lng, 4),
        "distance_coast_km": round(distance_from_coast_km, 1),
        "elevation_m": round(elevation_estimate, 1),
        "land_use": land_use,
        "tsunami_zone": tsunami_zone,
    })

# Summary statistics
land_use_counts = {}
tsunami_count = 0
for p in cell_profiles:
    land_use_counts[p["land_use"]] = land_use_counts.get(p["land_use"], 0) + 1
    if p["tsunami_zone"]:
        tsunami_count += 1

print(f"\nPer-Cell Characterization ({len(cell_profiles)} cells):")
print(f"  Land use distribution:")
for lu, count in sorted(land_use_counts.items()):
    print(f"    {lu}: {count} cells ({count / len(cell_profiles):.0%})")
print(f"  Cells in tsunami zone: {tsunami_count} ({tsunami_count / len(cell_profiles):.0%})")
```

## Step 5: Generate Place Report

```python
print("\n" + "=" * 60)
print("PLACE CHARACTERIZATION REPORT")
print("=" * 60)
print(f"Location: {place_identity['name']}")
print(f"Analysis date: generated via GEO-INFER-PLACE")
print(f"Spatial resolution: H3 resolution {place_identity['h3_resolution']}")
print(f"Coverage: {place_identity['cell_count']} cells, {place_identity['area_km2']} km2")
print()
print("ECOLOGICAL CONTEXT")
print(f"  Ecoregion: {place_identity['ecology']['ecoregion']}")
print(f"  Vegetation: {place_identity['ecology']['primary_vegetation']}")
print(f"  Watershed: {place_identity['ecology']['watershed']}")
print(f"  Protected areas: {len(place_identity['ecology']['protected_areas'])}")
print()
print("HAZARD PROFILE")
print(f"  Seismic: {place_identity['hazards']['seismic']['fault_zone']}")
print(f"  Recent earthquakes: {place_identity['hazards']['seismic']['recent_events']}")
print(f"  Tsunami risk: {place_identity['hazards']['seismic']['tsunami_risk']}")
print(f"  Cells in tsunami zone: {tsunami_count}/{len(cell_profiles)}")
print()
print("COMMUNITY")
print(f"  Population: ~{place_identity['demographics']['population_estimate']:,}")
print(f"  Primary industries: {', '.join(place_identity['demographics']['primary_industries'])}")
print(f"  Key infrastructure: {place_identity['infrastructure']['harbor']}, "
      f"{place_identity['infrastructure']['hospital']}")
```

## Key Takeaways

1. **H3 cells provide consistent spatial units**: Every analysis layer maps cleanly to the same hexagonal grid, enabling direct comparison and aggregation.
2. **Real-time data adds currency**: Earthquake and weather feeds complement static datasets with up-to-the-day observations.
3. **Multi-layer identity captures complexity**: No single variable defines a place. The combination of ecology, hazards, demographics, and infrastructure creates a unique fingerprint.

## Next Steps

- Use GEO-INFER-DATA to pull real land cover, census, and OSM amenity layers.
- See the [Bioregional Health Example](advanced_example.md) for Cascadia-scale composite assessment.
- Integrate with GEO-INFER-SPACE for cross-resolution H3 analysis.
