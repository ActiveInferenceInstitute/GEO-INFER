# Basic Integration Demo 🚀

**Your First GEO-INFER Cross-Module Experience**

## Learning Objectives 🎯

After completing this example, you will:
- Understand how GEO-INFER modules work together
- See the power of spatial-temporal data integration
- Learn basic patterns for cross-module communication
- Gain confidence to explore more complex examples
- Experience the standardized GEO-INFER workflow

## Modules Used 🔧

### Primary Modules
- **GEO-INFER-SPACE**: Spatial data processing and coordinate transformations
- **GEO-INFER-TIME**: Temporal data handling and time-series operations
- **GEO-INFER-DATA**: Data ingestion, validation, and management

### Supporting Modules
- **GEO-INFER-API**: Standardized data access interfaces
- **GEO-INFER-OPS**: Orchestration and logging

### Integration Points
- **SPACE ↔ DATA**: Spatial data validation and transformation
- **TIME ↔ DATA**: Temporal indexing and synchronization
- **SPACE ↔ TIME**: Spatio-temporal alignment and analysis
- **API**: Unified access to all module capabilities

## Prerequisites ✅

### Required Modules
```bash
# Core modules needed for this example
pip install -e ../../../GEO-INFER-DATA
pip install -e ../../../GEO-INFER-SPACE  
pip install -e ../../../GEO-INFER-TIME
pip install -e ../../../GEO-INFER-API
```

### Sample Data
- GPS tracking data (included in `data/input/`)
- Weather station readings (synthetic data generated)
- Administrative boundaries (OpenStreetMap data)

### System Requirements
- Python 3.9+
- 2GB RAM minimum
- 500MB disk space

## Quick Start ⚡

### 3-Step Execution
```bash
# 1. Navigate to the example directory
cd GEO-INFER-EXAMPLES/examples/getting_started/basic_integration_demo

# 2. Run the example
python scripts/run_example.py

# 3. View results
ls data/output/
```

### Expected Runtime
- **Processing Time**: ~2 minutes
- **Data Size**: ~50MB input, ~20MB output

### Key Outputs to Observe
- `spatial_analysis_results.geojson`: Processed spatial features
- `temporal_patterns.json`: Time-series analysis results  
- `integrated_visualization.html`: Interactive map showing spatio-temporal patterns
- `execution_report.md`: Summary of module interactions and performance

## Detailed Walkthrough 📚

### Step 1: Data Ingestion (GEO-INFER-DATA)
```python
from geo_infer_data import DataManager

# Initialize data manager
data_mgr = DataManager()

# Load and validate GPS tracks
gps_data = data_mgr.load_spatial_data("data/input/gps_tracks.geojson")
print(f"Loaded {len(gps_data)} GPS points")

# Load temporal weather data
weather_data = data_mgr.load_temporal_data("data/input/weather_stations.csv")
print(f"Loaded weather data spanning {weather_data.time_range}")
```

**Module Integration**: DATA module validates formats and ensures consistency across spatial and temporal datasets.

### Step 2: Spatial Processing (GEO-INFER-SPACE)
```python
from geo_infer_space import SpatialProcessor

# Initialize spatial processor with data from Step 1
spatial_proc = SpatialProcessor(data_mgr.get_spatial_context())

# Transform GPS coordinates to consistent projection
standardized_gps = spatial_proc.transform_coordinates(
    gps_data, 
    target_crs="EPSG:4326"
)

# Create spatial index for efficient queries
spatial_index = spatial_proc.create_spatial_index(standardized_gps)
print(f"Created spatial index with {len(spatial_index)} features")
```

**Module Integration**: SPACE module receives validated data from DATA and prepares it for temporal alignment.

### Step 3: Temporal Analysis (GEO-INFER-TIME)
```python
from geo_infer_time import TemporalProcessor

# Initialize temporal processor
temporal_proc = TemporalProcessor()

# Align GPS tracks with weather measurements
aligned_data = temporal_proc.temporal_join(
    standardized_gps,  # From SPACE module
    weather_data,      # From DATA module
    time_tolerance="15min"
)

# Identify temporal patterns
patterns = temporal_proc.find_patterns(aligned_data)
print(f"Discovered {len(patterns)} temporal patterns")
```

**Module Integration**: TIME module works with both DATA (weather) and SPACE (GPS) outputs to create spatio-temporal alignment.

### Step 4: Integrated Analysis
```python
# Combine all module outputs for comprehensive analysis
from geo_infer_api import AnalysisAPI

api = AnalysisAPI()

# Perform integrated spatio-temporal analysis
results = api.analyze_spatiotemporal(
    spatial_data=standardized_gps,    # From SPACE
    temporal_data=aligned_data,       # From TIME  
    patterns=patterns,               # From TIME
    spatial_index=spatial_index      # From SPACE
)

# Generate visualization combining all module insights
visualization = api.create_integrated_visualization(results)
```

**Module Integration**: API module orchestrates all previous outputs into a cohesive analysis.

## Key Integration Patterns 🔄

### 1. **Data Flow Pattern**
```
Raw Data → [DATA validation] → [SPACE processing] → [TIME alignment] → [API integration] → Results
```

### 2. **Module Communication**
- **Standardized Formats**: All modules use consistent GeoJSON/temporal formats
- **Context Sharing**: Spatial context flows from DATA → SPACE → TIME
- **Error Handling**: Each module validates inputs from previous modules
- **Metadata Preservation**: Processing history tracked across module boundaries

### 3. **Best Practices Demonstrated**
- **Explicit Dependencies**: Clear import statements show module relationships
- **Data Validation**: Each module validates inputs from other modules
- **Error Propagation**: Failures in one module are handled gracefully by others
- **Resource Management**: Efficient memory usage across module boundaries

## Extensions & Variations 🚀

### Add AI/ML Capabilities
```python
# Extend with GEO-INFER-AI for predictive analysis
from geo_infer_ai import PredictiveAnalyzer

ai_analyzer = PredictiveAnalyzer()
predictions = ai_analyzer.predict_movement_patterns(results)
```

### Include Risk Assessment
```python
# Add GEO-INFER-RISK for risk modeling
from geo_infer_risk import RiskAssessment

risk_model = RiskAssessment()
risk_zones = risk_model.assess_spatial_risk(results)
```

### Scaling Considerations
- **Larger Datasets**: Use DATA module's streaming capabilities
- **Real-time Processing**: Leverage TIME module's streaming analysis
- **Distributed Processing**: Use OPS module for multi-node deployment

## Troubleshooting 🛠️

### Common Issues

**Module Import Errors**
```bash
# Ensure all required modules are installed
pip list | grep geo-infer
```

**Data Format Issues**
```python
# Use DATA module's validation utilities
from geo_infer_data import validate_spatial_data
validation_report = validate_spatial_data("your_file.geojson")
```

**Coordinate System Problems**
```python
# Check and fix coordinate reference systems
from geo_infer_space import check_crs
crs_info = check_crs(your_spatial_data)
```

**Memory Issues with Large Files**
```python
# Use streaming processing for large datasets
from geo_infer_data import StreamingDataManager
stream_mgr = StreamingDataManager(chunk_size=1000)
```

### Getting Help
- **Module Documentation**: Each module has comprehensive docs
- **Community Support**: [Discord](https://discord.activeinference.institute/)
- **Issue Reporting**: [GitHub Issues](https://github.com/activeinference/GEO-INFER/issues)

## Performance Metrics 📊

### Expected Performance
- **Processing Speed**: ~25,000 GPS points/minute
- **Memory Usage**: ~200MB peak for sample dataset
- **Output Generation**: ~30 seconds for visualization

### Monitoring Integration
```python
# Built-in performance monitoring via OPS module
from geo_infer_ops import PerformanceMonitor

monitor = PerformanceMonitor()
with monitor.track_execution("basic_integration_demo"):
    # Your analysis code here
    results = api.analyze_spatiotemporal(...)

# View performance report
print(monitor.get_performance_report())
```

## What's Next? 🌟

### Recommended Follow-up Examples
1. **First Analysis Workflow**: More complex analytical patterns
2. **Health Integration Examples**: See domain-specific module integration
3. **Urban Planning Examples**: Experience community-focused modules

### Module Exploration Paths
- **For Spatial Focus**: Explore GEO-INFER-SPACE advanced capabilities
- **For AI/ML Interest**: Try GEO-INFER-AI integration examples
- **For Active Inference**: Progress to GEO-INFER-ACT examples

---

**🎯 Success Indicator**: You should now understand how GEO-INFER modules work together and feel confident exploring more complex cross-module examples!

**⚡ Remember**: This example demonstrates **orchestration**, not novel functionality. The power comes from combining existing module capabilities effectively. 