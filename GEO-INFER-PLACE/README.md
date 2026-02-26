---
title: "GEO-INFER-PLACE: Place-Based Geospatial Analysis"
description: "Location-specific geospatial analysis for Del Norte County and the Cascadia Bioregion"
purpose: "Multi-domain environmental and hazard analysis for real geographic locations"
module_type: "Domain Application"
status: "Alpha"
last_updated: "2026-02-25"
dependencies: ["DATA", "TIME", "SPACE (optional)"]
compatibility: ["GEO-INFER-DATA", "GEO-INFER-TIME", "GEO-INFER-SPACE"]
tags: ["place", "geospatial", "del-norte", "cascadia", "forest", "seismic", "coastal", "fire"]
difficulty: "Intermediate"
estimated_time: "30"
---

<div align="center">
  <h3><a href="../README.md">🌍 GEO-INFER Core</a></h3>
  <a href="../AGENTS.md">🤖 Agent Architecture</a> •
  <a href="../README.md#-module-overview">📦 Module Index</a> •
  <a href="./docs/">📚 Documentation</a> •
  <a href="./SKILL.md">🧠 Claude Skill</a>
</div>

---

# GEO-INFER-PLACE: Place-Based Geospatial Analysis

GEO-INFER-PLACE delivers location-specific environmental and hazard analysis for named geographic
locations. Each location integrates real data from public APIs (CAL FIRE, NOAA, USGS) with
retry logic, local caching, and optional bridges to GEO-INFER-DATA and GEO-INFER-TIME.

## Supported Locations

| Code | Name | Analyzers |
|------|------|-----------|
| `del_norte` | Del Norte County, California | Forest Health, Coastal Resilience, Fire Risk, Seismic Hazard |
| `cascadia` | Cascadia Bioregion (BC, WA, OR, CA) | Seismic Hazard, Forest Health, Salmon Habitat, Volcanic Hazard |

## Quick Start

```python
from geo_infer_place import PlaceInterface

# Create an interface for Del Norte County
pi = PlaceInterface("del_norte")

# Run all configured analyzers
results = pi.run_full_analysis()

# Check component status
print(pi.status())
# {
#   "location": "del_norte",
#   "location_name": "Del Norte County, California",
#   "available_analyzers": ["forest_health", "coastal_resilience", "fire_risk", "seismic_hazard"],
#   ...
# }
```

## Factory Function

```python
from geo_infer_place import create_analyzer, get_supported_locations

# List available locations
print(get_supported_locations())  # ['del_norte', 'cascadia']

# Create a PlaceInterface via the factory
pi = create_analyzer("del_norte")
print(type(pi).__name__)  # PlaceInterface
```

## Domain Analyzers

Each analyzer runs independently and returns a dict. Access them via `get_analyzer()`:

```python
pi = PlaceInterface("del_norte")

# Forest health: canopy, mortality, fire risk indices
forest = pi.get_analyzer("forest_health")
forest_result = forest.run_analysis()

# Coastal resilience: tide gauges, erosion, storm surge risk
coastal = pi.get_analyzer("coastal_resilience")
coastal_result = coastal.run_analysis()

# Fire risk: CAL FIRE perimeters, vegetation, ignition probability
fire = pi.get_analyzer("fire_risk")
fire_result = fire.run_analysis()

# Seismic hazard: USGS earthquake catalog, Cascadia Subduction Zone
seismic = pi.get_analyzer("seismic_hazard")
seismic_result = seismic.run_analysis()
```

## Subset Analysis

Run only the analyzers you need:

```python
pi = PlaceInterface("del_norte")
results = pi.run_full_analysis(analyzers=["seismic_hazard", "fire_risk"])
assert "seismic_hazard" in results["analyses"]
assert "fire_risk" in results["analyses"]
```

## Convenience Data Methods

Direct access to data sources without running a full analysis:

```python
pi = PlaceInterface("del_norte")

# Recent earthquakes (USGS)
quakes = pi.get_earthquakes()
print(f"Events: {len(quakes.get('events', []))}")

# Cascadia Subduction Zone seismicity
csz = pi.get_cascadia_seismicity(days=30)

# Fire perimeters (CAL FIRE ArcGIS)
fires = pi.get_fire_perimeters()
print(f"Features: {len(fires.get('features', []))}")

# Weather observations (NOAA)
weather = pi.get_weather(station_id="KCEC")

# Tide gauge data (NOAA)
tides = pi.get_tide_data()
```

## Data Sources

| Source | Data | Endpoint |
|--------|------|----------|
| CAL FIRE | Fire perimeters, incidents, timber operations | ArcGIS REST API |
| NOAA | Tide gauges, weather observations | Tides and Currents API |
| USGS | Earthquake catalog, seismic hazard | Earthquake Hazards API |

All wrappers include:
- Local disk cache with configurable TTL (CAL FIRE: 24 h, NOAA: 6 h, USGS: 1 h)
- Automatic retry with exponential back-off
- Synthetic data fallback when the upstream API is unavailable

## H3 Spatial Utilities

PLACE re-exports all H3 utilities from `geo_infer_place.utils.h3_operations`:

```python
from geo_infer_place import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,
    geo_to_cells,
    polygon_to_cells,
    grid_disk,
    grid_distance,
    grid_ring,
    cell_area,
    get_resolution,
    is_valid_cell,
    are_neighbor_cells,
    cells_to_geodataframe,
    cell_to_parent,
    cell_to_children,
    compact_cells,
    uncompact_cells,
    estimate_cell_count,
)

# Example: index a coordinate
cell = latlng_to_cell(41.75, -124.2, resolution=8)
boundary = cell_to_latlng_boundary(cell)
```

## Module Bridges

GEO-INFER-PLACE integrates with other modules when they are installed:

```python
# GEO-INFER-DATA: data quality and provenance tracking
from geo_infer_place import PlaceDataManager

dm = PlaceDataManager()
quality = dm.validate_dataset(my_dataset, name="forest_health")
dm.log_provenance("forest_health", {"source": "calfire", "timestamp": "2026-02-25"})

# GEO-INFER-TIME: temporal trend detection
from geo_infer_place import PlaceTemporalAnalyzer

ta = PlaceTemporalAnalyzer()
trends = ta.analyze_tide_trends(tide_data)
rates = ta.analyze_seismic_rates(csz_data)
```

## Cascadia Agricultural Pipeline

The Cascadia location includes a separate agricultural analysis pipeline with H3-indexed
cross-border data integration (California + Oregon counties):

```bash
# Run the full Cascadia pipeline
python GEO-INFER-PLACE/locations/cascadia/cascadia_main.py
```

```python
from geo_infer_place import CascadianAgriculturalH3Backend

backend = CascadianAgriculturalH3Backend(resolution=7)
cell = backend.get_h3_cell(lat=41.75, lon=-124.2)
```

## API Clients

Low-level API clients are also exported for direct use:

```python
from geo_infer_place import (
    CaliforniaAPIManager,
    NOAAClient,
    CALFIREClient,
    USGSClient,
    USGSEarthquakeClient,
    CDECClient,
)
```

## Module Structure

```text
GEO-INFER-PLACE/
├── src/geo_infer_place/
│   ├── core/
│   │   ├── place_interface.py       # PlaceInterface — primary entry point
│   │   ├── unified_backend.py       # CascadianAgriculturalH3Backend
│   │   ├── api_clients.py           # CALFIREClient, NOAAClient, USGSClient, ...
│   │   ├── module_bridge.py         # PlaceDataManager, PlaceTemporalAnalyzer
│   │   └── visualization_engine.py  # InteractiveVisualizationEngine
│   ├── locations/
│   │   └── del_norte_county/
│   │       ├── forest_health_monitor.py
│   │       ├── coastal_resilience_analyzer.py
│   │       ├── fire_risk_assessor.py
│   │       └── seismic_hazard_analyzer.py
│   ├── utils/
│   │   ├── h3_operations.py         # H3 spatial utilities
│   │   ├── integration.py           # _CALFIREWrapper, _NOAAWrapper, _USGSWrapper
│   │   ├── caching.py               # CachedAPIWrapper
│   │   └── data_sources.py          # CaliforniaDataSources
│   └── config/
│       └── location_presets.yaml    # Location bounds + analyzer config
└── locations/
    └── cascadia/                    # Stand-alone Cascadia pipeline
        └── cascadia_main.py
```

## Testing

```bash
# All tests
python -m pytest GEO-INFER-PLACE/tests/ -v

# Unit tests only
python -m pytest GEO-INFER-PLACE/tests/unit/ -v

# Specific module
python -m pytest GEO-INFER-PLACE/tests/unit/test_place_interface.py -v
```

## Development Notes

- SPACE dependency is **optional** — all core functionality works without `geo_infer_space`
- Data fetches degrade gracefully to synthetic data when upstream APIs are unavailable
- H3 resolution 8 for Del Norte (~460 m cells), resolution 7 for Cascadia (~1.2 km cells)
- Output files written to `locations/<location>/output/` by default

## Documentation Hub

Full framework documentation, guides, and tutorials are available in the [GEO-INFER-INTRA documentation hub](../GEO-INFER-INTRA/docs/index.md).

| Resource | Description |
|----------|-------------|
| [Getting Started](../GEO-INFER-INTRA/docs/getting_started/index.md) | Installation, first steps, quick start guides |
| [Module Overview](../GEO-INFER-INTRA/docs/modules/index.md) | All 44 modules with descriptions and use cases |
| [Integration Patterns](../GEO-INFER-INTRA/docs/integration/geo_infer_modules.md) | How modules work together |
| [Testing Guide](../GEO-INFER-INTRA/docs/developer_guide/testing_guide.md) | Testing standards, fixtures, CI integration |
| [API Standards](../GEO-INFER-INTRA/docs/developer_guide/index.md) | Code conventions and contribution guidelines |
