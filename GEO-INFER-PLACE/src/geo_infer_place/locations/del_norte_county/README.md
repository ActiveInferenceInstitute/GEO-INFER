# Del Norte County — Source Modules

## Overview

Production analysis modules for Del Norte County, California. Contains 5 Python modules
and 1 dashboard sub-package covering forest health, coastal resilience, fire risk,
seismic hazard, and comprehensive visualization.

## Components

### [forest_health_monitor.py](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/forest_health_monitor.py)

Forest health monitoring and analysis for old-growth redwood, Douglas fir, and mixed
conifer ecosystems. 15 methods covering NDVI/EVI analysis, tree mortality detection,
climate vulnerability assessment, and CAL FIRE integration.

**Class**: `ForestHealthMonitor`

### [coastal_resilience_analyzer.py](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/coastal_resilience_analyzer.py)

Coastal resilience analysis for 45 miles of Pacific coastline. Sea level rise
vulnerability, coastal erosion tracking, storm surge modeling, tsunami risk, and
habitat connectivity assessment via NOAA tide gauge data.

**Class**: `CoastalResilienceAnalyzer`

### [fire_risk_assessor.py](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/fire_risk_assessor.py)

Wildfire risk assessment integrating fire weather, fuel moisture, historical fire
patterns, and wildland-urban interface analysis using CAL FIRE data.

**Class**: `FireRiskAssessor`

### [seismic_hazard_analyzer.py](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/seismic_hazard_analyzer.py)

Cascadia Subduction Zone seismic and tsunami hazard analysis using real USGS
earthquake data feeds. Includes H3-indexed hazard scoring, liquefaction risk,
and full-rupture CSZ scenario assessment.

**Class**: `SeismicHazardAnalyzer`

### [comprehensive_dashboard.py](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/comprehensive_dashboard.py)

Multi-domain interactive dashboard integrating all analysis domains with cross-domain
interaction analysis and H3 spatial fusion.

**Class**: `DelNorteComprehensiveDashboard`

### [dashboard/](file:///Users/4d/Documents/GitHub/GEO-INFER/GEO-INFER-PLACE/src/geo_infer_place/locations/del_norte_county/dashboard/)

Lightweight dashboard package with climate, zoning, and agro-economic analyzers.

**Class**: `AdvancedDashboard` (via `dashboard.core`)

## Integration

- Imports: `geo_infer_place.utils.integration.DelNorteDataIntegrator`
- Spatial: H3 hexagonal indexing at resolution 8
- APIs: CAL FIRE, NOAA Tides & Weather, USGS Earthquake Hazards
