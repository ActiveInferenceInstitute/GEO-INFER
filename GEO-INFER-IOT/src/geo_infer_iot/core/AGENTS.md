# Agent
: core

## Scope
 This directory contains core components for the module. It provides 9 classes and 0 functions.

## Classes
 and Functions

### SensorMeasurement
 Data class for sensor measurements with spatial context.

### SpatialInferenceConfig
 Configuration for Bayesian spatial inference.

### IoTDataIngestion
 IoT data ingestion engine with spatial indexing and Bayesian inference.

**Methods**:
- `setup_spatial_inference(config: SpatialInferenceConfig)`: Setup Bayesian spatial inference for a specific variable.
- `get_spatial_distribution(variable: str, confidence_level: float) -> Optional[Dict]`: Get current spatial distribution for a variable.
- `get_measurement_statistics() -> Dict`: Get statistics about ingested measurements.

### RadiationMonitoringSystem
 Specialized IoT system for radiation monitoring with logging and testing.

**Methods**:
- `generate_simulated_data(sensor_count: int) -> List[Dict]`: Generate simulated radiation sensor data for testing.
- `setup_spatial_inference(variable: str)`: Setup Bayesian spatial inference for radiation monitoring.
- `get_system_metrics() -> Dict`: Get system performance metrics.
- `validate_system_health() -> Dict`: Validate overall system health for testing purposes.

### GlobalMonitoringSystem
 Global-scale radiation monitoring system for demonstration.

### SensorMetadata
 Metadata for an individual sensor.

### SensorNetwork
 Represents a sensor network with spatial bounds.

### SensorRegistry
 Registry for managing IoT sensor networks and individual sensors.

**Methods**:
- `register_network(**kwargs) -> SensorNetwork`: Register a sensor network.
- `register_sensor(sensor_info: Dict) -> SensorMetadata`: Register an individual sensor.
- `get_sensors_in_h3_cell(h3_index: str) -> List[SensorMetadata]`: Get all sensors in a specific H3 cell.
- `get_sensors_by_type(sensor_type: str) -> List[SensorMetadata]`: Get all sensors of a specific type.
- `get_sensors_in_area(bounds: Dict, h3_resolution: int) -> List[SensorMetadata]`: Get sensors within geographic bounds using H3 spatial indexing.

### SpatialDataFusion
 Spatial data fusion engine for combining IoT sensor measurements.

**Methods**:
- `fuse_sensor_data(measurements: List[Dict], target_variable: str, target_location: Optional[Tuple[float, float]]) -> Dict`: Fuse sensor data using spatial interpolation and uncertainty quantification.
- `validate_spatial_consistency(measurements: List[Dict], consistency_threshold: float) -> Dict`: Validate spatial consistency of measurements using H3-based analysis.

## Capabilities

- **9 classes** for core functionality

## Integration

- **Location**: `GEO-INFER-IOT/src/geo_infer_iot/core`
- **Type**: Directory Node
