# Agent
: core

## Scope
 This directory contains core components for the module. It provides 9 classes and 0 functions.

## Classes
 and Functions

### ClimateDataProcessor
 Process and validate climate datasets.

**Methods**:
- `load_dataset(file_path: str, dataset_type: str, variables: Optional[List[str]]) -> xr.Dataset`: Load climate dataset from file.
- `validate_dataset(dataset: xr.Dataset) -> Dict[str, bool]`: Validate climate dataset structure and data quality.
- `preprocess_dataset(dataset: xr.Dataset, operations: Optional[List[str]]) -> xr.Dataset`: Preprocess climate dataset with common operations.
- `extract_temporal_subset(dataset: xr.Dataset, start_date: str, end_date: str) -> xr.Dataset`: Extract temporal subset of dataset.
- `extract_spatial_subset(dataset: xr.Dataset, lat_range: Tuple[float, float], lon_range: Tuple[float, float]) -> xr.Dataset`: Extract spatial subset of dataset.

### ClimateIndicesCalculator
 Calculate climate indices from climate data.

**Methods**:
- `calculate_spi(precipitation: xr.DataArray, timescale: int, distribution: str) -> xr.DataArray`: Calculate Standardized Precipitation Index (SPI).
- `calculate_heat_index(temperature: xr.DataArray, humidity: Optional[xr.DataArray]) -> xr.DataArray`: Calculate heat index (apparent temperature).
- `calculate_extreme_indices(temperature: xr.DataArray, precipitation: Optional[xr.DataArray]) -> xr.Dataset`: Calculate climate extreme indices.
- `calculate_pdsi(precipitation: xr.DataArray, temperature: xr.DataArray, awc: float) -> xr.DataArray`: Calculate Palmer Drought Severity Index (PDSI).

### DownscalingMethods
 Climate downscaling methods.

**Methods**:
- `bias_correction(model_data: xr.DataArray, observed_data: xr.DataArray, method: str) -> xr.DataArray`: Apply bias correction to climate model data.
- `statistical_downscaling(coarse_data: xr.DataArray, fine_topography: Optional[xr.DataArray], method: str) -> xr.DataArray`: Statistical downscaling to higher resolution.

### ExtremeEventType
 Types of extreme events.

### Severity
 Event severity levels.

### ExtremeEvent
 Extreme weather event.

### ExtremeEventAnalyzer
 extreme weather event analyzer.

**Methods**:
- `detect_heatwaves(temperature: xr.DataArray, threshold_percentile: float, min_duration: int) -> xr.Dataset`: Detect heatwave events.
- `detect_droughts(precipitation: xr.DataArray, threshold_percentile: float, min_duration: int) -> xr.Dataset`: Detect drought events.
- `detect_cold_spells(temperature: xr.DataArray, threshold_percentile: float, min_duration: int) -> Dict[str, Any]`: Detect cold spell events.
- `detect_floods(streamflow: xr.DataArray, threshold_percentile: float, min_duration: int) -> Dict[str, Any]`: Detect flood events from streamflow data.
- `calculate_return_period(data: xr.DataArray, value: float, method: str) -> Dict[str, Any]`: Calculate return period for an extreme value.
- `detect_compound_events(temperature: xr.DataArray, precipitation: xr.DataArray, temp_threshold_percentile: float, precip_threshold_percentile: float) -> Dict[str, Any]`: Detect compound extreme events (e.g., hot and dry).
- `calculate_climate_indices(temperature: xr.DataArray, precipitation: Optional[xr.DataArray]) -> Dict[str, Any]`: Calculate standard climate extreme indices.
- `register_event(event: ExtremeEvent) -> str`: Register an extreme event.
- `get_event_statistics() -> Dict[str, Any]`: Get statistics on registered events.

### ClimateImpactAssessor
 Assess climate change impacts on various systems.

**Methods**:
- `assess_agricultural_impact(temperature: xr.DataArray, precipitation: xr.DataArray, crop_type: str) -> xr.Dataset`: Assess climate impact on agriculture.
- `assess_water_resources(precipitation: xr.DataArray, temperature: xr.DataArray, evapotranspiration: Optional[xr.DataArray]) -> xr.Dataset`: Assess climate impact on water resources.

### ClimateProjections
 Climate change projections and scenario analysis.

**Methods**:
- `project_future_climate(historical_data: xr.DataArray, scenario: str, years: List[int]) -> xr.DataArray`: Project future climate based on historical data and scenario.

## Capabilities

- **9 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-CLIMATE/src/geo_infer_climate/core`
- **Type**: Directory Node
