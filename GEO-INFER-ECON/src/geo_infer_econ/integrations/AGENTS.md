# Agent
: integrations

## Scope
 This directory contains integrations components for the module. It provides 3 classes and 0 functions.

## Classes
 and Functions

### DataIntegration
 Integration adapter for GEO-INFER-DATA.

**Methods**:
- `load_dataset(dataset_id: str, spatial_bounds: Optional[List[float]], temporal_range: Optional[Tuple[str, str]], format: str) -> Optional[Union[pd.DataFrame, gpd.GeoDataFrame]]`: Load economic dataset with optional filtering.
- `list_datasets(dataset_type: Optional[str], tags: Optional[List[str]]) -> Optional[List[Dict[str, Any]]]`: List available economic datasets.
- `load_economic_data(source: Union[str, Path], source_type: str, **kwargs) -> Optional[Union[pd.DataFrame, gpd.GeoDataFrame]]`: Load economic data from various sources.
- `is_available() -> bool`: Check if GEO-INFER-DATA is available.

### SpaceIntegration
 Integration adapter for GEO-INFER-SPACE.

**Methods**:
- `latlng_to_cell(lat: float, lng: float, resolution: int) -> Optional[str]`: Convert lat/lng to spatial cell index.
- `cell_to_latlng(cell: str) -> Optional[Tuple[float, float]]`: Convert spatial cell index to lat/lng.
- `calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> Optional[float]`: Calculate distance between two points.
- `analyze_hotspots(gdf: gpd.GeoDataFrame, value_column: str, **kwargs) -> Optional[gpd.GeoDataFrame]`: Analyze spatial hotspots in economic data.
- `spatial_interpolation(points: gpd.GeoDataFrame, values: np.ndarray, target_locations: gpd.GeoDataFrame, method: str, **kwargs) -> Optional[np.ndarray]`: Perform spatial interpolation of economic values.
- `create_buffer(geometry: gpd.GeoDataFrame, distance: float, **kwargs) -> Optional[gpd.GeoDataFrame]`: Create buffer zones around geometries.
- `is_available() -> bool`: Check if GEO-INFER-SPACE is available.

### TimeIntegration
 Integration adapter for GEO-INFER-TIME.

**Methods**:
- `detect_trend(time_series: pd.Series, method: str) -> Optional[Dict[str, Any]]`: Detect trends in economic time series.
- `analyze_seasonality(time_series: pd.Series, period: Optional[int]) -> Optional[Dict[str, Any]]`: Analyze seasonality in economic time series.
- `decompose_time_series(time_series: pd.Series, model: str) -> Optional[Dict[str, pd.Series]]`: Decompose time series into trend, seasonal, and residual components.
- `forecast(time_series: pd.Series, horizon: int, method: str, **kwargs) -> Optional[Dict[str, Any]]`: Forecast economic time series.
- `align_time_series(time_series_list: List[pd.Series], method: str) -> Optional[List[pd.Series]]`: Align multiple time series to common time index.
- `is_available() -> bool`: Check if GEO-INFER-TIME is available.

## Capabilities

- **3 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-ECON/src/geo_infer_econ/integrations`
- **Type**: Directory Node
