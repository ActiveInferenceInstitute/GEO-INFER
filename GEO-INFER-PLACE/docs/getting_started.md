# Getting Started with GEO-INFER-PLACE

This guide covers installation, core concepts, and first working examples for place-based geospatial analysis.

## Installation

Install the module in editable mode using `uv`:

```bash
uv pip install -e ./GEO-INFER-PLACE
```

GEO-INFER-PLACE has optional integration with other GEO-INFER modules:

```
```bash
# For full integration (data quality + temporal analysis)
uv pip install -e ./GEO-INFER-PLACE ./GEO-INFER-DATA ./GEO-INFER-TIME ./GEO-INFER-SPACE
```

Verify the installation:

```
```python
import geo_infer_place
print(geo_infer_place.__version__)
# 1.1.0
```

## Core Concepts

### Place-Based Identity

GEO-INFER-PLACE operates on the principle that every geographic location has a unique identity shaped by overlapping natural, built, and social systems. A "place" is not just coordinates -- it is the intersection of:

- **Ecology**: Forest cover, watershed health, wildlife corridors.
- **Geology**: Seismic risk, soil types, terrain.
- **Climate**: Temperature, precipitation, extreme weather patterns.
- **Human systems**: Population, land use, infrastructure, cultural heritage.

The `PlaceInterface` brings these layers together through location-specific analyzers and real-time data feeds.

### Bioregional Thinking

The Cascadia bioregion example demonstrates bioregional analysis -- understanding a place through its ecological boundaries (watersheds, ecoregions) rather than political ones. This approach integrates:

- Salmon Evolutionarily Significant Units (ESUs)
- Indigenous territory boundaries
- Climate zones
- Ecoregion classifications

### Supported Locations

Currently two locations are fully supported:

#### Del Norte County, California

- Bounds: 41.458N-42.006N, 124.408W-123.536W
- H3 resolution: 8 (0.74 km2 per cell)
- Analyzers: forest health, coastal resilience, fire risk, seismic hazard
- Data sources: CAL FIRE, NOAA, USGS

#### Cascadia Bioregion

- Bounds: 40.0N-49.0N, 124.8W-114.5W
- H3 resolution: 7 (5.16 km2 per cell)
- Analyzers: seismic hazard, forest health, salmon habitat, volcanic hazard
- Data sources: USGS, NOAA, CAL FIRE

### Lazy Initialization

All `PlaceInterface` components are lazily initialized. The interface object itself is lightweight. API clients, analyzers, and bridge modules are created only when first accessed:

```
```python
from geo_infer_place import PlaceInterface

# Lightweight -- no network calls yet
pi = PlaceInterface("del_norte")

# First access triggers initialization of the forest health analyzer
forest = pi.get_analyzer("forest_health")

# First access to data_manager triggers PlaceDataManager creation
quality = pi.data_manager.validate_dataset(some_data)
```

## First Example: Check Location Status

```
```python
from geo_infer_place import PlaceInterface

pi = PlaceInterface("del_norte")
status = pi.status()

print(f"Location: {status['location_name']}")
print(f"Output directory: {status['output_dir']}")
print(f"Available analyzers: {status['available_analyzers']}")
print(f"GEO-INFER-DATA available: {status['data_module_available']}")
print(f"GEO-INFER-TIME available: {status['time_module_available']}")
```

## Second Example: Fetch Live Data

Retrieve real-time environmental data from federal agencies.

```
```python
from geo_infer_place import PlaceInterface

pi = PlaceInterface("del_norte")

# Fetch recent earthquakes near Del Norte County
earthquakes = pi.get_earthquakes()
print(f"Recent earthquakes: {len(earthquakes.get('features', []))}")

# Fetch Cascadia subduction zone seismicity
cascadia = pi.get_cascadia_seismicity(days=30)
print(f"Cascadia events (30 days): {len(cascadia.get('events', []))}")

# Fetch tide gauge data
tides = pi.get_tide_data()
print(f"Tide stations: {len(tides.get('stations', []))}")

# Fetch fire perimeter data
fires = pi.get_fire_perimeters(start_year=2020)
print(f"Fire perimeters since 2020: {len(fires.get('features', []))}")

# Fetch current weather
weather = pi.get_weather(station_id="KCEC")
print(f"Weather station: {weather.get('station', 'unknown')}")
```

## Third Example: Run Full Analysis

Execute all configured analyzers for Del Norte County.

```
```python
from geo_infer_place import PlaceInterface

pi = PlaceInterface("del_norte")

# Run all analyzers with temporal analysis
results = pi.run_full_analysis(include_temporal=True)

print(f"Location: {results['location']}")
print(f"Timestamp: {results['timestamp']}")
print(f"Analyzers run: {list(results['analyses'].keys())}")

# Check individual analyzer results
for name, analysis in results["analyses"].items():
    if isinstance(analysis, dict) and "error" not in analysis:
        print(f"  {name}: completed")
    elif isinstance(analysis, dict) and analysis.get("skipped"):
        print(f"  {name}: skipped ({analysis.get('reason')})")
    else:
        print(f"  {name}: error")

# Check temporal analysis
if results.get("temporal_analysis"):
    print(f"Temporal analyses: {list(results['temporal_analysis'].keys())}")

# Check data quality
for name, quality in results.get("data_quality", {}).items():
    print(f"  {name} quality: {quality}")
```

## Fourth Example: Work with H3 Cells

GEO-INFER-PLACE re-exports H3 v4 utility functions for convenience.

```
```python
from geo_infer_place import (
    latlng_to_cell,
    cell_to_latlng,
    grid_disk,
    cell_area,
    cells_to_geodataframe,
)

# Convert a point to an H3 cell
cell = latlng_to_cell(41.75, -124.2, 8)
print(f"H3 cell: {cell}")

# Get cell center
center = cell_to_latlng(cell)
print(f"Cell center: {center}")

# Get neighbors (k-ring)
neighbors = grid_disk(cell, 1)
print(f"Neighbors (k=1): {len(neighbors)} cells")

# Cell area
area = cell_area(cell, unit="km^2")
print(f"Cell area: {area:.4f} km2")

# Convert to GeoDataFrame for mapping
gdf = cells_to_geodataframe(list(neighbors))
print(f"GeoDataFrame shape: {gdf.shape}")
```

## Fifth Example: Cascadia Bioregion

Initialize a Cascadia analysis with specific counties.

```
```python
from geo_infer_place import PlaceInterface

pi = PlaceInterface(
    "cascadia",
    counties=["CA:Del Norte", "OR:Josephine", "OR:Curry"],
)

print(f"Location: {pi.location_name}")
print(f"Counties: {pi.counties}")

status = pi.status()
print(f"Available analyzers: {status['available_analyzers']}")
```

## Available Factory Functions

GEO-INFER-PLACE provides several convenience functions:

```
```python
from geo_infer_place import get_supported_locations, create_analyzer, create_place_interface

# List supported locations
locations = get_supported_locations()
print(f"Supported: {locations}")
# ['del_norte', 'cascadia']

# Create analyzer for a location
pi = create_analyzer("del_norte")

# Alternative factory with output directory
pi = create_place_interface(location="cascadia", output_dir="/tmp/cascadia_output")
```

## Next Steps

- Read the [API Reference](api_reference.md) for the full method catalog.
- Try the [Place Characterization Example](examples/basic_example.md) for multi-layer analysis.
- See the [Bioregional Health Example](examples/advanced_example.md) for Cascadia-style composite assessment.
