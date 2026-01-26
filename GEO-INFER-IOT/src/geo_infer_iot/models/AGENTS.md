# Agent
: models ## Scope
 This directory contains models components for the module. It provides 19 classes and 1 functions. ## Classes
 and Functions ### MeasurementQualit
y
 Quality metadata for sensor measurements. **Methods**: - `add_flag(flag: str)`: Add a quality flag. - `is_valid() -> bool`: Check if measurement meets quality standards. ### Measuremen
t
 Individual sensor measurement data model. **Methods**: - `validate_h3_index(cls, v, values)`: Validate H3 index format. - `update_location(latitude: float, longitude: float, h3_resolution: int)`: Update measurement location and recalculate H3 index. - `apply_calibration(calibration_params: Dict)`: Apply calibration to the measurement value. - `get_location_info() -> Dict`: Get location information. - `get_temporal_info() -> Dict`: Get temporal information about the measurement. ### MeasurementBatc
h
 Batch of sensor measurements for efficient processing. **Methods**: - `validate_measurements(cls, v)`: Validate measurements in batch. - `add_measurement(measurement: Measurement)`: Add a measurement to the batch. - `filter_by_quality(min_quality_score: float) -> 'MeasurementBatch'`: Filter batch to measurements meeting quality threshold. - `filter_by_variable(variable: str) -> 'MeasurementBatch'`: Filter batch to specific variable. - `filter_by_sensor(sensor_id: str) -> 'MeasurementBatch'`: Filter batch to specific sensor. - `get_statistics() -> Dict[str, Any]`: Get statistical summary of the batch. ### MeasurementStrea
m
 Real-time measurement stream configuration. **Methods**: - `add_sensor(sensor_id: str)`: Add a sensor to the stream. - `remove_sensor(sensor_id: str)`: Remove a sensor from the stream. - `add_variable(variable: str)`: Add a variable to the stream. - `remove_variable(variable: str)`: Remove a variable from the stream. ### MeasurementValidatio
n
 Measurement validation rules and constraints. **Methods**: - `validate_action(cls, v)`: Validate action on failure. - `validate_measurement(measurement: Measurement) -> bool`: Validate a measurement against these rules. ### NetworkTopologyTyp
e
 Network topology types. ### CommunicationProtoco
l
 Communication protocol types. ### NetworkNod
e
 Network node representing a sensor or gateway. **Methods**: - `add_connection(node_id: str)`: Add a connection to another node. - `remove_connection(node_id: str)`: Remove a connection to another node. - `get_health_score() -> float`: Calculate node health score based on various metrics. ### NetworkLin
k
 Network link between two nodes. **Methods**: - `get_performance_score() -> float`: Calculate link performance score. ### NetworkTopolog
y
 network topology model. **Methods**: - `add_node(node: NetworkNode)`: Add a node to the network. - `remove_node(node_id: str)`: Remove a node from the network. - `add_link(link: NetworkLink)`: Add a link to the network. - `remove_link(link_id: str)`: Remove a link from the network. - `get_connected_components() -> List[List[str]]`: Get connected components in the network. - `get_network_diameter() -> Optional[int]`: Calculate network diameter (longest shortest path). - `get_sensor_coverage() -> Dict[str, Any]`: Get sensor coverage analysis. ### NetworkEven
t
 Network event for monitoring and debugging. **Methods**: - `validate_severity(cls, v)`: Validate event severity. ### NetworkConfiguratio
n
 Network configuration and deployment settings. **Methods**: - `validate_deployment_mode(cls, v)`: Validate deployment mode. ### NetworkPerformanc
e
 Network performance metrics and analysis. **Methods**: - `add_metric(metric_name: str, value: float, node_id: Optional[str], link_id: Optional[str])`: Add a performance metric. - `calculate_performance_score() -> float`: Calculate overall performance score. - `identify_bottlenecks() -> List[Dict[str, Any]]`: Identify network bottlenecks. ### Locatio
n
 Geographic location model. **Methods**: - `validate_h3_index(cls, v, values)`: Validate H3 index format. ### SensorCapabilitie
s
 Sensor measurement capabilities. ### SensorCalibratio
n
 Sensor calibration information. ### Senso
r
 sensor data model. **Methods**: - `validate_status(cls, v)`: Validate sensor status. - `update_location(latitude: float, longitude: float, **kwargs)`: Update sensor location and related fields. - `add_capability(variable: str, **kwargs)`: Add a measurement capability to the sensor. - `update_calibration(calibration_data: Dict)`: Update sensor calibration information. - `get_health_score() -> float`: Calculate overall sensor health score. ### SensorNetwor
k
 Sensor network data model. **Methods**: - `validate_protocol(cls, v)`: Validate communication protocol. - `validate_topology(cls, v)`: Validate network topology. - `validate_spatial_bounds(cls, v)`: Validate spatial bounds. - `get_coverage_area() -> float`: Calculate approximate coverage area in square kilometers. - `is_location_covered(latitude: float, longitude: float) -> bool`: Check if a location is within the network's spatial bounds. - `get_h3_cells() -> List[str]`: Get H3 cells covering the network's spatial bounds. ### SensorDeploymen
t
 Sensor deployment and installation information. **Methods**: - `validate_deployment_method(cls, v)`: Validate deployment method. - `validate_power_source(cls, v)`: Validate power source. ### df
s
 `dfs(node_id: str, component: List[str])` ## Capabilities
 - **19 classes** for core functionality - **1 functions** for utility operations ## Integration
 - **Location**: `GEO-INFER-IOT/src/geo_infer_iot/models` - **Type**: Directory Node 