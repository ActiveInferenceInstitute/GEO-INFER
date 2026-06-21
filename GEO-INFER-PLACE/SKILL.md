---
name: geo-infer-place
description: Place-based analysis with H3 hexagonal indexing. Use when performing place identification, catchment area analysis, county/region geometry loading, or H3-based place-shedding and geographic boundary operations.
prerequisites:
  required:
    - geo-infer-space
    - geo-infer-data
  recommended:
    - geo-infer-bio
    - geo-infer-econ
    - geo-infer-transport
difficulty: intermediate
estimated_time: 45min
examples_dir: ../GEO-INFER-EXAMPLES/examples/
---

# GEO-INFER-PLACE

## Instructions

### Core Capabilities

- **Place identification**: Named place resolution and geocoding
- **Catchment analysis**: Service area and accessibility modeling
- **H3 place-shedding**: Hexagonal tessellation of administrative boundaries
- **Boundary operations**: County/region geometry loading and manipulation
- **Unified backend**: Multi-source geographic data integration

### Key Imports

```python
from geo_infer_place.core.unified_backend import UnifiedPlaceBackend
from geo_infer_place.core.catchment import CatchmentAnalyzer
from geo_infer_place.core.geocoding import PlaceGeocoder
```

## Examples

```python
from geo_infer_place.core.unified_backend import UnifiedPlaceBackend

backend = UnifiedPlaceBackend()
place = backend.resolve("Portland, OR")
print(f"Resolved: {place.name}, Center: ({place.lat}, {place.lng})")
boundary = backend.get_boundary(place.id)
print(f"Boundary: {boundary.area_km2:.1f} km²")
```

```python
from geo_infer_place.core.catchment import CatchmentAnalyzer

analyzer = CatchmentAnalyzer(mode="drive_time")
catchment = analyzer.compute(
    facility_location=(45.5, -122.6),
    max_time_minutes=15
)
print(f"15-min catchment: {catchment.area_km2:.1f} km²")
print(f"Population covered: {catchment.population:,}")
```

## Guidelines

- Uses H3 v4 API exclusively
- Fallback synthetic geometries are used when county data is unavailable
- Test: `uv run python -m pytest GEO-INFER-PLACE/tests/ -v`

### Integrations

- **SPACE** → H3 tessellation of place boundaries
- **DATA** → Boundary geometry data sources
- **CIV** → Community place identification
- **HEALTH** → Health district boundary resolution
- **TRANSPORT** → Accessible catchment areas
