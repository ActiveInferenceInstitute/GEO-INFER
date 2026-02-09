# Agent
: scripts

## Scope
 This directory contains scripts components for the module. It provides 3 classes and 11 functions.

## Classes
 and Functions

### InteractiveRadiationDashboard
 Create interactive H3 visualization dashboard

**Methods**:
- `add_sensor_layer(sensor_data: pd.DataFrame)`: Add sensor locations as markers
- `add_h3_prediction_layer(prediction_data: Dict)`: Add H3 cells with Bayesian posterior predictions
- `add_anomaly_layer(anomaly_data: Dict)`: Add anomaly markers
- `add_legend()`: Add legend for radiation levels
- `add_layer_control()`: Add layer control widget
- `save(output_path: str)`: Save the interactive map

### EnhancedLogger
 logging class for demonstration

**Methods**:
- `log(level: str, operation: str, data: dict, module: str)`: Log a structured message
- `info(operation: str, data: dict, module: str)`:
- `debug(operation: str, data: dict, module: str)`:
- `warning(operation: str, data: dict, module: str)`:
- `error(operation: str, data: dict, module: str)`:

### QualityController
 Quality control and testing for demonstration

**Methods**:
- `validate_sensor_data(data: pd.DataFrame) -> dict`: Validate sensor data quality
- `test_spatial_operations(h3_indices: List[str]) -> dict`: Test H3 spatial operations
- `test_bayesian_inference(posterior_results: dict) -> dict`: Test Bayesian inference quality

### create_geojson_with_features
 `create_geojson_with_features(prediction_data: Dict, output_path: str)` Create a proper GeoJSON file with H3 cell features

### generate_time_series_plot_html
 `generate_time_series_plot_html(anomaly_data: Dict, output_path: str)` Generate HTML with time series plots

### main
 `main()` Main function to create visualizations

### load_config
 `load_config(config_path: str) -> dict` Load configuration from YAML file

### generate_sample_sensor_data
 `generate_sample_sensor_data(config: dict, logger: EnhancedLogger) -> pd.DataFrame` Generate sample sensor data for demonstration

### perform_spatial_indexing
 `perform_spatial_indexing(data: pd.DataFrame, config: dict, logger: EnhancedLogger) -> dict` Perform H3 spatial indexing operations

### perform_bayesian_inference
 `perform_bayesian_inference(h3_data: pd.DataFrame, config: dict, logger: EnhancedLogger) -> dict` Perform Bayesian spatial inference

### detect_anomalies
 `detect_anomalies(data: pd.DataFrame, config: dict, logger: EnhancedLogger) -> dict` Detect radiation anomalies

### save_results
 `save_results(sensor_data: pd.DataFrame, spatial_results: dict, inference_results: dict, anomaly_results: dict, config: dict, logger: EnhancedLogger)` Save all results to output files

### run_tests
 `run_tests(sensor_data: pd.DataFrame, spatial_results: dict, inference_results: dict, config: dict, logger: EnhancedLogger) -> dict` Run tests

### main
 `main()` Main execution function

## Capabilities

- **3 classes** for core functionality
- **11 functions** for utility operations

## Integration

- **Location**: `GEO-INFER-EXAMPLES/examples/iot_radiation_monitoring/scripts`
- **Type**: Directory Node
