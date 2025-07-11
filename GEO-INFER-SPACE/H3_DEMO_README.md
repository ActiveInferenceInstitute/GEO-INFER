# H3 Geospatial Overlay Demonstration

## 🌟 Overview

This script demonstrates interactive H3-based geospatial overlays using the OSC (OS Climate) repositories integrated with GEO-INFER-SPACE. It showcases the power of H3 hexagonal indexing for geospatial analysis and visualization.

## 🚀 Features

### ✅ **What This Demo Does:**

1. **🔍 OSC Repository Integration**: Uses `osc-geo-h3grid-srv` and `osc-geo-h3loader-cli` for standardized H3 grid operations
2. **🌍 Sample Data Generation**: Creates realistic geospatial datasets with properties like temperature, humidity, elevation, and population
3. **🔷 H3 Cell Conversion**: Converts point data to H3 hexagonal cells at configurable resolutions  
4. **🗺️ Interactive Visualization**: Generates rich Folium maps with multiple overlay layers
5. **🌐 Web Server**: Spins up a local web server to serve the interactive visualizations
6. **📊 Multiple Data Formats**: Exports data in JSON, GeoJSON, and CSV formats

### 🎯 **Key Capabilities:**

- **H3 Hexagonal Grids**: Uses Uber's H3 system for efficient spatial indexing
- **Multiple Resolution Levels**: Supports H3 resolutions 0-15 for different zoom levels
- **Interactive Maps**: Folium-based maps with layer controls and popups
- **Color-Coded Overlays**: Temperature and density-based visualizations
- **Clustered Points**: Sample points grouped with marker clustering
- **Real-time Web Serving**: Built-in HTTP server for immediate viewing

## 📋 Usage

### **Basic Usage:**
```bash
python h3_geospatial_demo.py
```

### **Advanced Options:**
```bash
python h3_geospatial_demo.py \
  --resolution 8 \
  --samples 500 \
  --center 40.7128 -74.0060 \
  --serve \
  --port 8080
```

### **Command Line Arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--resolution` | 8 | H3 resolution level (0-15) |
| `--samples` | 1000 | Number of sample points to generate |
| `--center` | NYC | Center coordinates [lat lon] |
| `--port` | 8080 | Web server port |
| `--serve` | False | Start web server |
| `--no-browser` | False | Don't auto-open browser |

## 🔧 H3 Resolution Guide

| Resolution | Cell Area | Best For |
|------------|-----------|----------|
| 0-2 | Continental | Global analysis |
| 3-5 | Regional | Country/state level |
| 6-8 | City | Urban planning |
| 9-11 | Neighborhood | Local analysis |
| 12-15 | Building | High-precision |

## 📁 Output Structure

```
demo_outputs/
├── maps/
│   └── h3_overlay_demo_YYYYMMDD_HHMMSS.html    # Interactive map
├── data/
│   ├── sample_data_YYYYMMDD_HHMMSS.json        # Raw sample data
│   ├── h3_data_YYYYMMDD_HHMMSS.json            # H3 cell data
│   ├── h3_cells_YYYYMMDD_HHMMSS.geojson        # GeoJSON format
│   └── h3_analysis_YYYYMMDD_HHMMSS.csv         # CSV for analysis
└── visualizations/
    └── [various subdirectories with charts]
```

## 🗺️ Interactive Map Features

### **Layer Controls:**
- **H3 - Temperature**: Hexagonal cells colored by average temperature
- **H3 - Density**: Hexagonal cells colored by point density
- **Sample Points**: Clustered markers showing individual data points

### **Map Interactions:**
- **Zoom & Pan**: Standard map navigation
- **Layer Toggle**: Switch between different overlays
- **Popup Details**: Click cells/points for detailed information
- **Multiple Basemaps**: OpenStreetMap, CartoDB Positron

### **Cell Information:**
Each H3 cell popup shows:
- H3 cell identifier
- Number of aggregated points
- Average temperature, humidity, elevation
- Total population
- Density score
- Cell area in km²

## 🔬 Technical Details

### **Dependencies:**
- **Core**: h3, folium, numpy, pandas
- **Geospatial**: geopandas, shapely  
- **Visualization**: matplotlib, seaborn
- **GEO-INFER**: OSC integration modules

### **H3 Operations:**
- Point-to-cell conversion: `h3.latlng_to_cell()`
- Cell boundaries: `h3.cell_to_boundary()`
- Cell centers: `h3.cell_to_latlng()`
- Area calculations: `h3.cell_area()`

### **Data Aggregation:**
- Points grouped by H3 cell
- Statistical aggregation (mean, sum, std)
- Density calculations
- Spatial relationship analysis

## 🚀 Getting Started

### **1. Install Dependencies:**
```bash
cd GEO-INFER-SPACE
pip install folium h3 geopandas shapely matplotlib seaborn
```

### **2. Run Basic Demo:**
```bash
python h3_geospatial_demo.py --samples 300 --resolution 8
```

### **3. Start Web Server:**
```bash
python h3_geospatial_demo.py --serve --port 8080
```

### **4. View Results:**
- Interactive map opens automatically in browser
- Or navigate to `http://localhost:8080`
- Explore the demo_outputs directory for data files

## 📊 Example Outputs

### **Demo Statistics Example:**
```
🎉 H3 Geospatial Overlay Demo Complete!
📁 Output directory: demo_outputs
🌍 Interactive map: demo_outputs/maps/h3_overlay_demo_20250618_082438.html
✅ Converted to 194 H3 cells
📊 Average points per cell: 1.03
```

### **Generated Files:**
- **Interactive Map**: 863KB HTML file with full Folium visualization
- **Sample Data**: JSON with 200-1000 sample points
- **H3 Data**: Aggregated statistics for each hexagonal cell
- **GeoJSON**: Standard format for GIS applications
- **CSV**: Tabular data for analysis tools

## 🌟 Integration with OSC

This demo leverages the OS Climate (OSC) repositories via forks:
- **osc-geo-h3grid-srv**: H3 grid service for standardized operations (fork of github.com/os-climate/osc-geo-h3grid-srv)
- **osc-geo-h3loader-cli**: Data loading utilities for H3 grids (fork of github.com/os-climate/osc-geo-h3loader-cli)

The integration follows OSC best practices for:
- Standardized H3 operations
- Climate data compatibility
- Reproducible geospatial analysis

## 🎯 Use Cases

### **Urban Planning:**
- Analyze population density patterns
- Plan service coverage areas
- Optimize resource allocation

### **Climate Analysis:**
- Temperature distribution mapping
- Environmental monitoring
- Climate data aggregation

### **Business Intelligence:**
- Market analysis by geographic area
- Customer density visualization
- Location-based analytics

### **Research & Development:**
- Spatial pattern analysis
- Geospatial algorithm testing
- H3 system evaluation

## 🔧 Customization

### **Different Locations:**
```bash
# London
python h3_geospatial_demo.py --center 51.5074 -0.1278

# Tokyo  
python h3_geospatial_demo.py --center 35.6762 139.6503

# São Paulo
python h3_geospatial_demo.py --center -23.5505 -46.6333
```

### **Resolution Comparison:**
```bash
# Coarse resolution (larger cells)
python h3_geospatial_demo.py --resolution 6

# Fine resolution (smaller cells)  
python h3_geospatial_demo.py --resolution 10
```

### **Large Datasets:**
```bash
# High sample count
python h3_geospatial_demo.py --samples 5000 --no-browser
```

## 📝 Notes

- **Performance**: Higher resolutions and sample counts increase processing time
- **Memory**: Large datasets may require substantial RAM
- **Browser**: Modern browsers required for full Folium feature support
- **Network**: Web server mode requires available port (default 8080)

---

**Built with ❤️ using GEO-INFER-SPACE and OS Climate integration** 