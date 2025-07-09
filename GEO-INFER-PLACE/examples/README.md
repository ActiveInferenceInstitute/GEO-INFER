# Del Norte County Comprehensive Dashboard Examples

This directory contains examples and demonstrations of the comprehensive Del Norte County geospatial analysis dashboard built with the GEO-INFER framework.

## 🌟 Overview

The Del Norte County Comprehensive Dashboard integrates multiple analysis domains with real California data sources to provide sophisticated geospatial intelligence for this rural coastal county. The system demonstrates Active Inference principles applied to place-based analysis with professional-grade visualizations adapted from the climate integration example.

## 🏗️ System Architecture

### Core Components

1. **🗃️ Data Sources Management** (`utils/data_sources.py`)
   - Catalog of 20+ California and federal data sources
   - Automated source discovery and validation
   - Location-specific source prioritization

2. **🔌 API Clients** (`core/api_clients.py`)
   - Real-time data integration with CAL FIRE, NOAA, USGS, CDEC
   - Rate limiting, error handling, and data standardization
   - Comprehensive API validation and health monitoring

3. **🔷 H3 Spatial Analysis** (Integrated throughout)
   - Hexagonal spatial indexing for multi-scale analysis
   - Efficient aggregation and cross-domain integration
   - Optimized for place-based analysis workflows

4. **🎯 Specialized Analyzers**
   - `forest_health_monitor.py`: Forest ecosystem health assessment
   - `coastal_resilience_analyzer.py`: Coastal vulnerability and adaptation
   - `fire_risk_assessor.py`: Wildfire risk modeling and management

5. **📊 Interactive Dashboard** (`comprehensive_dashboard.py`)
   - Multi-layer folium visualizations with toggle controls
   - Real-time data integration and display
   - Professional styling with comprehensive control panels

## 🚀 Quick Start

### Prerequisites

```bash
# Required packages
pip install folium h3 pandas geopandas numpy requests PyYAML
```

### Basic Usage

```bash
# Run the comprehensive demonstration
python del_norte_county_demo.py

# With custom output directory
python del_norte_county_demo.py --output ./my_dashboard

# With API keys for enhanced data access
python del_norte_county_demo.py --api-keys api_keys.json
```

### API Keys Configuration

Create an `api_keys.json` file for enhanced data access:

```json
{
  "noaa": "your_noaa_api_key",
  "calfire": "your_calfire_api_key", 
  "usgs": "your_usgs_api_key",
  "cdec": "your_cdec_api_key"
}
```

## 📋 Example Workflows

### 1. Component Demonstration

```bash
# Run component demos only (no full dashboard)
python del_norte_county_demo.py --demo-only --verbose
```

This demonstrates:
- California data sources catalog (20+ sources)
- API connection validation
- H3 spatial analysis capabilities
- Data source prioritization for Del Norte County

### 2. Full Dashboard Generation

```bash
# Generate comprehensive interactive dashboard
python del_norte_county_demo.py --output ./del_norte_results
```

Generated outputs:
- 📊 **Interactive Dashboard**: HTML file with multi-layer map
- 📄 **Analysis Results**: JSON file with comprehensive data
- 📋 **Summary Report**: Text summary of key findings

### 3. Custom Configuration

```bash
# Use custom configuration file
python del_norte_county_demo.py --config custom_config.yaml --output ./custom_dashboard
```

## 🔍 Analysis Domains

### Forest Health Monitoring 🌲

- **NDVI Analysis**: Vegetation health indices from satellite data
- **Canopy Cover Assessment**: Forest structure monitoring
- **Fire Impact Analysis**: Post-fire recovery assessment
- **Carbon Sequestration**: Forest carbon storage estimates

**Data Sources**: CAL FIRE forest inventory, Landsat/Sentinel imagery, USFS monitoring stations

### Coastal Resilience Analysis 🌊

- **Sea Level Rise Projections**: NOAA tide gauge integration
- **Erosion Rate Analysis**: Coastal change monitoring
- **Storm Surge Modeling**: Extreme weather vulnerability
- **Infrastructure Risk**: Critical facility exposure assessment

**Data Sources**: NOAA tides & currents, coastal monitoring stations, LiDAR elevation data

### Fire Risk Assessment 🔥

- **Weather Station Integration**: Real-time fire weather monitoring
- **Fuel Load Assessment**: Vegetation density and moisture
- **Historical Fire Analysis**: Fire perimeter and frequency data
- **WUI Risk Mapping**: Wildland-urban interface vulnerability

**Data Sources**: CAL FIRE RAWS stations, fire perimeter database, weather monitoring networks

### Cross-Domain Integration 🔗

- **Multi-Risk Assessment**: Combined vulnerability scoring
- **Spatial Hotspot Analysis**: H3-based risk aggregation
- **Climate Vulnerability Index**: Integrated climate impacts
- **Infrastructure Exposure**: Cross-domain infrastructure analysis

## 🗺️ Interactive Visualization Features

### Map Layers

1. **🔷 H3 Spatial Analysis**: Hexagonal risk aggregation
2. **🌲 Forest Health**: Monitoring sites and health indices
3. **🌊 Coastal Resilience**: Tide gauges and vulnerability zones
4. **🔥 Fire Risk**: Weather stations and fire history
5. **📊 Real-Time Data**: API connection status and data freshness
6. **🔗 Integration**: Cross-domain hotspots and combined risks

### Interactive Controls

- **Layer Toggle System**: Show/hide analysis domains
- **Professional Styling**: Custom color schemes and popups
- **Real-Time Updates**: Data freshness indicators
- **Comprehensive Metadata**: Analysis parameters and timestamps

### Advanced Features

- **H3 Hover Effects**: Interactive hexagon highlighting
- **Marker Clustering**: Efficient point data visualization
- **Multi-Scale Analysis**: Zoom-appropriate detail levels
- **Export Capabilities**: Dashboard and data export options

## 📊 Generated Outputs

### Interactive Dashboard

**File**: `del_norte_comprehensive_dashboard_YYYYMMDD_HHMMSS.html`

Features:
- Multi-layer interactive map with professional styling
- Toggle controls for different analysis domains
- Real-time data integration indicators
- Comprehensive popups with detailed information
- H3 spatial analysis visualization with risk scoring

### Analysis Results

**File**: `del_norte_analysis_results_YYYYMMDD_HHMMSS.json`

Contents:
- Metadata: Analysis parameters and data sources
- Configuration: Location bounds and system settings
- Data fetch results: API success/failure status
- Analysis results: Complete results from all analyzers
- H3 aggregation: Spatial analysis data and metrics

### Summary Report

**File**: `del_norte_summary_YYYYMMDD_HHMMSS.txt`

Contents:
- Analysis overview and key findings
- Data integration status and source connectivity
- Spatial analysis metrics (H3 cells, coverage area)
- Risk assessment summaries for each domain
- Climate vulnerability and integrated risk scores

## 🛠️ Customization

### Configuration Files

Customize analysis parameters by modifying:
- `GEO-INFER-PLACE/locations/del_norte_county/config/analysis_config.yaml`
- Location bounds, H3 resolution, analysis thresholds
- Data source preferences and API endpoints

### Adding New Analysis Domains

1. Create new analyzer class following existing patterns
2. Integrate with `comprehensive_dashboard.py`
3. Add visualization layers and controls
4. Update configuration schema

### Extending to Other Locations

1. Create new location directory under `locations/`
2. Adapt configuration for new geographic area
3. Update data sources for regional relevance
4. Customize analysis parameters for local conditions

## 🔧 Advanced Usage

### Programmatic API

```python
from geo_infer_place.locations.del_norte_county.comprehensive_dashboard import DelNorteComprehensiveDashboard

# Initialize dashboard
dashboard = DelNorteComprehensiveDashboard(
    api_keys={'noaa': 'your_key'},
    h3_resolution=8,
    output_dir='./results'
)

# Run analysis workflow
dashboard.load_configuration()
dashboard.fetch_real_data()
dashboard.run_comprehensive_analysis()

# Generate outputs
dashboard_path = dashboard.generate_comprehensive_dashboard()
results_path = dashboard.export_analysis_results()
```

### Custom Analysis Integration

```python
# Access individual analyzers
forest_results = dashboard.forest_analyzer.analyze_forest_health(
    satellite_data=your_data,
    fire_data=fire_perimeters,
    weather_data=weather_stations
)

# Custom H3 analysis
h3_results = dashboard._generate_h3_spatial_analysis()
```

## 📈 Performance Characteristics

### Data Processing

- **H3 Cell Generation**: ~225 cells for Del Norte County at resolution 8
- **API Response Times**: 100-2000ms per service
- **Dashboard Generation**: 5-15 seconds for full analysis
- **File Sizes**: 2-10MB for complete dashboard

### Scalability

- **Spatial Resolution**: Configurable H3 resolution (6-12 recommended)
- **Temporal Range**: 1 day to 10+ years of historical data
- **Geographic Scope**: County to multi-county regions
- **Data Volume**: Handles 10K+ spatial features efficiently

## ⚠️ Known Limitations

1. **API Dependencies**: Requires internet connectivity for real-time data
2. **Rate Limiting**: Some APIs have usage restrictions
3. **Data Availability**: Not all sources cover all geographic areas
4. **Processing Time**: Complex analysis may take several minutes
5. **Browser Performance**: Large datasets may require modern browsers

## 🆘 Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**API Connection Failures**:
- Check internet connectivity
- Verify API keys are valid
- Review rate limiting status

**Dashboard Generation Errors**:
- Ensure output directory is writable
- Check available disk space
- Verify folium/h3 compatibility

**H3 Analysis Issues**:
- Confirm location bounds are valid
- Check H3 resolution is appropriate (6-12)
- Verify spatial data formats

### Debug Mode

```bash
# Enable verbose logging
python del_norte_county_demo.py --verbose

# Check component demos only
python del_norte_county_demo.py --demo-only --verbose
```

## 🔮 Future Enhancements

### Planned Features

1. **Real-Time Streaming**: Live data updates and alerts
2. **Machine Learning Integration**: Predictive risk modeling
3. **Mobile Optimization**: Responsive dashboard design
4. **API Extensions**: Additional data source integrations
5. **Collaborative Features**: Multi-user analysis and sharing

### Research Applications

- **Climate Adaptation Planning**: Long-term resilience strategies
- **Natural Resource Management**: Integrated ecosystem analysis
- **Emergency Response**: Real-time hazard monitoring
- **Community Engagement**: Public-facing dashboard versions

## 📚 Related Documentation

- [GEO-INFER Framework Documentation](../../README.md)
- [H3 Spatial Analysis Guide](../../docs/h3_integration.md)
- [API Integration Patterns](../../docs/api_clients.md)
- [Active Inference Methodology](../../docs/active_inference.md)

## 🤝 Contributing

This implementation demonstrates production-quality geospatial analysis with real data integration. Contributions welcome for:

- Additional data source integrations
- Enhanced visualization features
- New analysis domain modules
- Performance optimizations
- Documentation improvements

---

**Built with the GEO-INFER Framework** | **Powered by Active Inference** | **California Real Data Integration** 