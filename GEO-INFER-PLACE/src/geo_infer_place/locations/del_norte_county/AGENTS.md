# Agent: del_norte_county (src)

## Scope

Production source code for Del Norte County geospatial analysis. Contains 5 analyzer
classes and 1 dashboard sub-package providing environmental monitoring, coastal
resilience, wildfire risk, seismic hazard, and interactive visualization.

## Classes

### ForestHealthMonitor

Forest health monitoring for Del Norte County's redwood, Douglas fir, and mixed conifer ecosystems.

**Key Methods**:

- `run_analysis(temporal_range)` — Full forest health assessment pipeline
- `get_monitoring_status()` — Current monitoring system status

### CoastalResilienceAnalyzer

Coastal resilience analysis for 45 miles of Pacific coastline.

**Key Methods**:

- `run_analysis(temporal_range)` — Coastal resilience assessment pipeline
- `get_monitoring_status()` — Current monitoring system status

### FireRiskAssessor

Wildfire risk assessment integrating fire weather, fuel moisture, and WUI analysis.

**Key Methods**:

- `run_analysis(temporal_range)` — Fire risk assessment pipeline
- `get_monitoring_status()` — Current monitoring system status

### SeismicHazardAnalyzer

Cascadia Subduction Zone seismic and tsunami hazard analysis using USGS data feeds.

**Key Methods**:

- `run_analysis()` — Seismic hazard assessment pipeline (earthquake data, hazard grid, tsunami risk, CSZ scenario)

### DelNorteComprehensiveDashboard

Multi-domain interactive dashboard integrating all analysis domains.

**Key Methods**:

- `run_comprehensive_analysis()` — Run all analyzers
- `generate_comprehensive_dashboard()` — Generate interactive HTML dashboard
- `export_analysis_results()` — Export to JSON

## Capabilities

- **5 analyzer classes** with full analysis pipelines
- **1 dashboard sub-package** (`dashboard/`) with `AdvancedDashboard`
- **H3 spatial indexing** at resolution 8
- **API integration**: CAL FIRE, NOAA, USGS via `DelNorteDataIntegrator`

## Integration

- **Location**: `src/geo_infer_place/locations/del_norte_county`
- **Type**: Directory Node (production source)
