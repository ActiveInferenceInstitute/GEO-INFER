# IoT Radiation Monitoring Example 🌐☢️

[![Example Status](https://img.shields.io/badge/status-active-brightgreen.svg)]()
[![Integration Level](https://img.shields.io/badge/integration-advanced-orange.svg)]()
[![Modules Used](https://img.shields.io/badge/modules-5+-blue.svg)]()

**Global-scale radiation monitoring using IoT sensor networks with Bayesian spatial inference**

## Learning Objectives 🎯

By completing this example, users will learn how to:

- **Integrate IoT sensor networks** with GEO-INFER for real-time environmental monitoring
- **Apply Bayesian spatial inference** to convert point measurements into continuous radiation maps
- **Use H3 spatial indexing** for efficient global-scale data organization
- **Implement quality control** and anomaly detection for sensor networks
- **Create interactive visualizations** of spatial-temporal radiation patterns
- **Set up logging and testing** for production IoT systems

## Modules Used 🔧

### Primary Modules
- **GEO-INFER-IOT**: IoT sensor network integration and real-time data ingestion
- **GEO-INFER-BAYES**: Bayesian spatial inference and uncertainty quantification
- **GEO-INFER-SPACE**: H3 spatial indexing and geospatial operations
- **GEO-INFER-LOG**: Comprehensive logging and monitoring
- **GEO-INFER-TEST**: Quality assurance and validation

### Supporting Modules
- **GEO-INFER-DATA**: Sensor data storage and management
- **GEO-INFER-TIME**: Temporal analysis and time-series processing
- **GEO-INFER-API**: Web services for external integration
- **GEO-INFER-APP**: Interactive dashboards and visualization

### Integration Points
- **IoT → SPACE**: Automatic H3 indexing of sensor locations
- **IoT → BAYES**: Real-time Bayesian inference on sensor streams
- **BAYES → SPACE**: Spatial interpolation using H3 grid systems
- **LOG → ALL**: Comprehensive logging across all components
- **TEST → ALL**: Validation and quality assurance

## Prerequisites ⚙️

### Required Modules
```bash
# Core dependencies
pip install -e ./GEO-INFER-SPACE
pip install -e ./GEO-INFER-BAYES
pip install -e ./GEO-INFER-IOT
pip install -e ./GEO-INFER-LOG
pip install -e ./GEO-INFER-TEST

# Supporting modules
pip install -e ./GEO-INFER-DATA
pip install -e ./GEO-INFER-TIME
pip install -e ./GEO-INFER-API
```

### System Requirements
- Python 3.9+
- 8GB+ RAM (for global-scale processing)
- Internet connection (for simulated data feeds)
- Optional: MQTT broker for real-time testing

### Sample Data
- Simulated global radiation sensor networks
- Historical background radiation data
- Reference monitoring stations (Safecast, EURDEP, CTBTO)

## Quick Start 🚀

```bash
# 1. Navigate to example directory
cd GEO-INFER-EXAMPLES/examples/iot_radiation_monitoring

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the complete example
python scripts/run_example.py --config config/example_config.yaml
```

**Expected Runtime**: 3-5 minutes  
**Key Outputs**: 
- Global radiation map (GeoJSON)
- Anomaly detection results  
- Interactive dashboard  
- Comprehensive logs

## Detailed Walkthrough 📖

### Step 1: IoT Network Setup
The example begins by setting up simulated global radiation monitoring networks:

```python
from geo_infer_iot import IoTSystem, GlobalMonitoringSystem
from geo_infer_space.osc_geo.utils.h3_utils import h3_to_geojson

# Initialize IoT system with H3 spatial indexing
iot_system = IoTSystem(config={
    "spatial": {"h3_resolution": 5},
    "protocols": ["simulation", "mqtt"],
    "networks": ["safecast", "eurdep", "ctbto"]
})
```

### Step 2: Spatial Indexing Integration
Sensors are automatically indexed using H3 for efficient spatial operations:

```python
# Each sensor gets H3 spatial context
sensor_data = {
    "sensor_id": "safecast_001",
    "latitude": 35.6762, "longitude": 139.6503,  # Tokyo
    "radiation_level": 0.15,  # μSv/h
    "h3_index": "auto-computed",  # H3 index for spatial queries
    "neighbors": "auto-computed"  # Neighboring cells
}
```

### Step 3: Bayesian Spatial Inference
Point measurements are converted to continuous surfaces using Gaussian Processes:

```python
from geo_infer_bayes import BayesianSpatialInference

# Configure spatial inference
inference = BayesianSpatialInference(
    variable="gamma_radiation",
    spatial_resolution=5,  # H3 resolution
    covariance_function="matern_52",
    prior_mean=0.1,  # Background radiation μSv/h
    length_scale=50000,  # 50km spatial correlation
    noise_variance=0.01
)

# Perform inference
posterior_map = inference.infer_global_distribution(
    sensor_measurements=recent_data,
    confidence_levels=[0.68, 0.95, 0.99]
)
```

### Step 4: Quality Control and Logging
Comprehensive logging and validation ensure data quality:

```python
from geo_infer_log import EnhancedLogger
from geo_infer_test import QualityController

logger = EnhancedLogger("radiation_monitoring")
qc = QualityController(radiation_monitoring_rules)

# Log all operations with context
logger.log_sensor_ingestion(sensor_data, qc_result)
logger.log_spatial_inference(inference_params, performance_metrics)
logger.log_anomaly_detection(anomalies_found)
```

### Step 5: Real-time Anomaly Detection
Advanced anomaly detection identifies unusual radiation patterns:

```python
# Multi-scale anomaly detection
anomalies = surveillance.detect_anomalies(
    methods=["statistical", "spatial", "temporal"],
    thresholds={"mild": 2.0, "severe": 3.0, "critical": 5.0},
    spatial_context=True  # Consider neighboring measurements
)

# Alert classification
for anomaly in anomalies:
    alert_level = classify_alert(anomaly.score, location_context)
    logger.log_alert(anomaly, alert_level)
```

### Step 6: Interactive Visualization
Results are presented through interactive maps and dashboards:

```python
from geo_infer_app import RadiationDashboard

dashboard = RadiationDashboard()
dashboard.add_sensor_layer(sensor_locations)
dashboard.add_interpolation_layer(posterior_map)
dashboard.add_anomaly_layer(detected_anomalies)
dashboard.add_h3_grid_overlay(resolution=5)

dashboard.save("output/radiation_dashboard.html")
```

## Key Integration Patterns 🔗

### 1. **Real-time Data Flow**
```
IoT Sensors → MQTT/HTTP → IoT Module → H3 Indexing → Spatial Database
                                    ↓
Quality Control ← LOG Module ← BAYES Inference ← Spatial Processing
                                    ↓
Web Dashboard ← API Module ← Results Storage ← Anomaly Detection
```

### 2. **H3 Spatial Integration**
- **Sensor Registration**: Automatic H3 indexing during sensor onboarding
- **Spatial Queries**: Efficient neighbor finding and regional aggregation
- **Multi-resolution Analysis**: Seamless zoom between global and local scales
- **Grid-based Inference**: Bayesian inference on H3 cell centroids

### 3. **Bayesian Model Integration**
- **Prior Specification**: Domain knowledge about background radiation
- **Spatial Covariance**: Matérn functions for realistic spatial correlation
- **Uncertainty Propagation**: Full posterior distributions with confidence intervals
- **Online Learning**: Continuous model updates as new data arrives

### 4. **Logging and Monitoring**
- **Structured Logging**: JSON-formatted logs with spatial context
- **Performance Metrics**: Inference timing, memory usage, data throughput
- **Quality Metrics**: Data validation results, anomaly detection rates
- **Alert Management**: Configurable alerting for different threat levels

## Module Communication Details 📡

### IoT ↔ SPACE Integration
```python
# Automatic H3 indexing in IoT module
sensor_measurement.h3_index = h3.geo_to_h3(lat, lon, resolution)
spatial_neighbors = get_h3_neighbors(sensor_measurement.h3_index)

# Efficient spatial queries using SPACE module
nearby_sensors = space_module.query_h3_region(
    center_cell=sensor_measurement.h3_index,
    ring_size=2
)
```

### BAYES ↔ SPACE Integration
```python
# Bayesian inference on H3 grid
h3_grid = space_module.generate_h3_grid(bounds, resolution=5)
grid_coordinates = [h3.h3_to_geo(cell) for cell in h3_grid]

# Spatial covariance using H3 distances
spatial_distances = space_module.h3_distance_matrix(h3_grid)
covariance_matrix = matern_52_covariance(spatial_distances, length_scale)
```

### LOG Integration Across All Modules
```python
# Centralized logging with module context
logger.info("sensor_ingestion", {
    "module": "IOT",
    "sensor_id": sensor_id,
    "h3_index": h3_index,
    "quality_score": qc_score,
    "processing_time_ms": elapsed_time
})

logger.info("bayesian_inference", {
    "module": "BAYES", 
    "variable": "radiation",
    "data_points": len(measurements),
    "convergence": inference_stats,
    "uncertainty_mean": posterior_uncertainty.mean()
})
```

## Configuration Details ⚙️

### Main Configuration (`config/example_config.yaml`)
```yaml
radiation_monitoring:
  # Global settings
  project_name: "Global Radiation Surveillance"
  spatial_resolution: 5  # H3 resolution
  temporal_window: "1h"
  
  # IoT network configuration
  sensor_networks:
    safecast:
      protocol: "simulation"  # or "http" for real API
      update_frequency: "5min"
      quality_control: true
    eurdep:
      protocol: "simulation"
      coverage_region: "europe"
      update_frequency: "1h"
    ctbto:
      protocol: "simulation"
      coverage_region: "global"
      update_frequency: "1d"
  
  # Bayesian inference settings
  bayesian_inference:
    prior_mean: 0.1  # μSv/h background
    covariance_function: "matern_52"
    length_scale: 50000  # meters
    noise_variance: 0.01
    confidence_levels: [0.68, 0.95, 0.99]
  
  # Anomaly detection
  anomaly_detection:
    methods: ["statistical", "spatial", "temporal"]
    thresholds:
      mild: 2.0      # 2 sigma
      severe: 3.0    # 3 sigma  
      critical: 5.0  # 5 sigma
  
  # Logging configuration
  logging:
    level: "INFO"
    format: "json"
    outputs: ["console", "file", "database"]
    metrics_collection: true
```

## Expected Outputs 📊

### 1. Global Radiation Map (`output/global_radiation_map.geojson`)
GeoJSON file with H3 cells containing:
- Mean radiation levels
- Uncertainty bounds (confidence intervals)
- Sensor counts per cell
- Anomaly flags

### 2. Anomaly Report (`output/anomaly_report.json`)
```json
{
  "detection_timestamp": "2024-06-20T08:00:00Z",
  "total_anomalies": 12,
  "by_severity": {
    "mild": 8,
    "severe": 3,
    "critical": 1
  },
  "anomalies": [
    {
      "id": "anomaly_001",
      "location": {"lat": 51.25, "lon": 30.18},
      "h3_index": "851fb467fffffff",
      "radiation_level": 1.25,
      "anomaly_score": 5.2,
      "alert_level": "critical",
      "nearest_city": "Chernobyl, Ukraine"
    }
  ]
}
```

### 3. Interactive Dashboard (`output/radiation_dashboard.html`)
Interactive HTML dashboard featuring:
- Real-time sensor locations
- Interpolated radiation surface
- H3 grid overlay
- Anomaly highlights
- Time-series plots
- Control panels for filtering

### 4. Performance Logs (`logs/performance_metrics.jsonl`)
```json
{"timestamp": "2024-06-20T08:00:00Z", "module": "IOT", "operation": "sensor_ingestion", "duration_ms": 15, "sensors_processed": 1250}
{"timestamp": "2024-06-20T08:00:30Z", "module": "BAYES", "operation": "spatial_inference", "duration_ms": 2340, "grid_cells": 10000, "convergence": true}
{"timestamp": "2024-06-20T08:01:00Z", "module": "TEST", "operation": "quality_validation", "duration_ms": 156, "validation_passed": true}
```

## Troubleshooting 🔧

### Common Issues

**Issue 1: Memory errors during global inference**
```bash
# Solution: Reduce spatial resolution or process in chunks
python scripts/run_example.py --h3-resolution 4 --chunk-size 1000
```

**Issue 2: Missing spatial dependencies**
```bash
# Solution: Install H3 and geospatial libraries
pip install h3 geopandas pyproj
```

**Issue 3: Slow Bayesian inference**
```bash
# Solution: Use variational inference instead of MCMC
# Edit config: bayesian_inference.method = "variational"
```

### Validation Steps
1. Check sensor data quality: `python scripts/validate_data.py`
2. Verify H3 indexing: `python scripts/test_spatial_ops.py`
3. Test Bayesian inference: `python scripts/test_inference.py`
4. Validate outputs: `python scripts/validate_outputs.py`

## Extensions & Variations 🚀

### 1. **Real API Integration**
Replace simulation with actual radiation monitoring APIs:
```python
# Connect to Safecast API
safecast_client = SafecastAPI(api_key=os.getenv("SAFECAST_API_KEY"))
real_measurements = safecast_client.get_recent_measurements()
```

### 2. **Multi-variable Analysis**
Extend to monitor multiple radiation types:
```python
variables = ["gamma_radiation", "beta_radiation", "alpha_radiation"]
for var in variables:
    inference_models[var] = setup_bayesian_inference(var)
```

### 3. **Real-time Alerting**
Add immediate notifications for critical anomalies:
```python
from geo_infer_comms import AlertManager
alert_manager.send_critical_alert(anomaly, channels=["email", "sms", "slack"])
```

### 4. **Historical Trend Analysis**
Analyze long-term radiation trends:
```python
from geo_infer_time import TrendAnalysis
trends = TrendAnalysis().detect_long_term_changes(
    historical_data, temporal_window="5y"
)
```

### 5. **Mobile Sensor Integration**
Include mobile and crowdsourced sensors:
```python
mobile_sensors = iot_system.register_mobile_network(
    protocol="http", update_frequency="real-time"
)
```

## Performance Benchmarks 📈

**Typical Performance** (on 8-core, 16GB RAM system):
- **Sensor Ingestion**: 1000+ sensors/second
- **H3 Indexing**: Sub-millisecond per sensor
- **Bayesian Inference**: 2-5 seconds for 10,000 grid cells
- **Anomaly Detection**: 500+ evaluations/second
- **Visualization Generation**: 10-30 seconds

**Scaling Guidelines**:
- **< 1K sensors**: Single-threaded processing adequate
- **1K-10K sensors**: Multi-threaded ingestion recommended
- **10K+ sensors**: Distributed processing with message queues
- **Global scale**: Use hierarchical H3 processing

## Learning Resources 📚

### Technical Papers
- "Bayesian Spatial Modeling for Environmental Monitoring" 
- "H3: Uber's Hexagonal Hierarchical Spatial Index"
- "IoT Sensor Networks for Environmental Surveillance"

### Related Examples
- `health_integration/environmental_health_assessment/`
- `climate_integration/ecosystem_monitoring/`
- `urban_integration/environmental_justice/`

### Documentation Links
- [GEO-INFER-IOT Documentation](../../GEO-INFER-IOT/README.md)
- [GEO-INFER-BAYES Guide](../../GEO-INFER-BAYES/README.md)
- [H3 Spatial Indexing](../../GEO-INFER-SPACE/docs/h3_guide.md)

---

**Next Steps**: After completing this example, explore how radiation monitoring integrates with health assessment (`health_integration/`) or disaster response (`climate_integration/disaster_response_coordination/`). 