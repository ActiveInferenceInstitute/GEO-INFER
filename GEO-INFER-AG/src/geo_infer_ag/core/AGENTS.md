# Agent
: core

## Scope
 This directory contains core components for the module. It provides 5 classes and 0 functions.

## Classes
 and Functions

### AgriculturalAnalysis
 Core class for performing agricultural analysis and modeling.

**Methods**:
- `run(field_data: gpd.GeoDataFrame, weather_data: Optional[pd.DataFrame], soil_data: Optional[gpd.GeoDataFrame], management_data: Optional[pd.DataFrame], **kwargs) -> 'AgriculturalResults'`: Run agricultural analysis using the provided data sources.

### AgriculturalResults
 Container for agricultural analysis results with visualization methods.

**Methods**:
- `get_metric(name: str) -> Union[float, np.ndarray]`: Get a specific metric from the results.
- `plot_spatial_distribution(variable: str, cmap: str, title: Optional[str], **kwargs)`: Plot spatial distribution of a result variable.
- `summary() -> Dict[str, Any]`: Generate a summary of the analysis results.

### FieldBoundaryManager
 Manages agricultural field boundaries and their properties.

**Methods**:
- `add_field(geometry: Union[Polygon, MultiPolygon], field_id: Optional[str], name: Optional[str], crop_type: Optional[str], attributes: Optional[Dict[str, Any]]) -> str`: Add a field boundary.
- `remove_field(field_id: str) -> bool`: Remove a field by its ID.
- `update_field(field_id: str, geometry: Optional[Union[Polygon, MultiPolygon]], name: Optional[str], crop_type: Optional[str], attributes: Optional[Dict[str, Any]]) -> bool`: Update a field's properties.
- `get_field(field_id: str) -> Optional[gpd.GeoSeries]`: Get a field by its ID.
- `get_fields_by_crop(crop_type: str) -> gpd.GeoDataFrame`: Get all fields with a specific crop type.
- `get_neighboring_fields(field_id: str, buffer_distance: float) -> gpd.GeoDataFrame`: Get fields that neighbor the specified field.
- `extract_fields_from_raster(raster_path: str, value_field: Optional[str], min_area: float, simplify_tolerance: Optional[float]) -> int`: Extract field boundaries from a classified raster image.
- `export_to_file(output_path: str, driver: str) -> None`: Export field boundaries to a file.

### SeasonalAnalysis
 Perform seasonal analysis for agricultural data.

**Methods**:
- `detect_growing_season(time_series: Optional[pd.Series], variable: str, method: str, threshold: float, smoothing_window: int, min_length_days: int) -> Dict[str, Any]`: Detect growing season start, peak, and end dates.
- `identify_phenological_stages(crop_type: str, time_series: Optional[pd.Series], variable: str, reference_stages: Optional[Dict[str, Tuple[float, float]]]) -> Dict[str, Any]`: Identify crop phenological stages using time series data.
- `analyze_temporal_trends(time_series: Optional[pd.Series], variable: str, period: str, detrend: bool, window_size: int) -> Dict[str, Any]`: Analyze temporal trends in agricultural data.
- `analyze_spatial_temporal_patterns(dataset: Optional[xr.Dataset], variable: str, time_dim: str, lat_dim: str, lon_dim: str) -> Dict[str, Any]`: Analyze spatial-temporal patterns in agricultural data.
- `plot_growing_season(ax, **kwargs)`: Plot the detected growing season.

### SustainabilityAssessment
 Assess sustainability aspects of agricultural practices.

**Methods**:
- `assess_carbon_sequestration(field_data: Optional[gpd.GeoDataFrame], crop_type_column: str, soil_carbon_column: Optional[str], biomass_column: Optional[str], management_practices: Optional[Dict[str, List[str]]], model: str) -> Dict[str, Any]`: Assess carbon sequestration potential of agricultural fields.
- `assess_water_usage(field_data: Optional[gpd.GeoDataFrame], water_data: Optional[pd.DataFrame], crop_type_column: str, precipitation_column: Optional[str], irrigation_column: Optional[str], evapotranspiration_column: Optional[str], reference_period: Optional[str]) -> Dict[str, Any]`: Assess water usage and efficiency of agricultural fields.
- `assess_soil_health(field_data: Optional[gpd.GeoDataFrame], soil_data: Optional[gpd.GeoDataFrame], organic_matter_column: Optional[str], ph_column: Optional[str], erosion_column: Optional[str], management_practices: Optional[Dict[str, List[str]]]) -> Dict[str, Any]`: Assess soil health of agricultural fields.
- `assess_biodiversity(field_data: Optional[gpd.GeoDataFrame], biodiversity_data: Optional[gpd.GeoDataFrame], edge_habitat_buffer: float, protected_areas: Optional[gpd.GeoDataFrame], management_practices: Optional[Dict[str, List[str]]]) -> Dict[str, Any]`: Assess biodiversity impact of agricultural fields.
- `calculate_sustainability_index(weights: Optional[Dict[str, float]]) -> Dict[str, Any]`: Calculate overall sustainability index from individual metrics.
- `plot_sustainability_metrics(ax, metric_type)`: Plot sustainability metrics on a map.

## Capabilities

- **5 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-AG/src/geo_infer_ag/core`
- **Type**: Directory Node
