# Agent
: dashboard

## Scope
 This directory contains dashboard components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### ClimateAnalyzer
 Climate analysis and visualization tools.

**Methods**:
- `generate_climate_projections() -> Dict[str, Any]`: Generate climate projection visualizations.
- `calculate_climate_risks() -> Dict[str, float]`: Calculate climate risk indicators.

### ZoningAnalyzer
 Zoning and land use analysis tools.

**Methods**:
- `generate_zoning_analysis() -> Dict[str, Any]`: Generate zoning and land use analysis.

### AgroEconomicAnalyzer
 Agricultural and economic analysis tools.

**Methods**:
- `generate_economic_analysis() -> Dict[str, Any]`: Generate economic analysis.

### LayerConfig
 Configuration for map layers.

### AdvancedDashboard
 Geospatial Intelligence Dashboard for Del Norte County.

**Methods**:
- `fetch_real_time_data() -> Dict[str, Any]`: Fetch real-time data from all configured sources using the shared integrator.
- `load_cached_data() -> None`: Load most recent cached datasets from output_dir into dashboard_data.
- `generate_analysis_panels() -> Dict[str, str]`: Generate HTML panels for different analysis components.
- `create_comprehensive_map() -> folium.Map`: Create interactive map with all layers and controls.
- `generate_dashboard_html(fetch_data: bool) -> str`: Generate dashboard HTML with panels and map.
- `save_dashboard(filename: str, fetch_data: bool) -> str`:

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `geo_infer_place/locations/del_norte_county/dashboard`
- **Type**: Directory Node
