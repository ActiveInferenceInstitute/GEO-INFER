# OSC Integration Comprehensive Guide

**OS Climate Integration for GEO-INFER-SPACE with Advanced Visualization and Reporting**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Repository Management](#repository-management)
5. [Enhanced Reporting & Visualizations](#enhanced-reporting--visualizations)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)
8. [Integration Examples](#integration-examples)
9. [Best Practices](#best-practices)
10. [Advanced Configuration](#advanced-configuration)

---

## 🎯 Overview

The OSC (OS Climate) integration in GEO-INFER-SPACE provides seamless access to OS Climate's geospatial tools while maintaining clean separation between codebases. This integration features:

### ✨ **Key Features**

- **Non-invasive Integration**: Clone and use OSC repositories without modifications
- **Automated Setup**: One-command setup with comprehensive testing
- **Rich Visualizations**: Interactive dashboards and static charts for monitoring
- **Enhanced Reporting**: HTML dashboards, JSON reports, and performance analytics
- **H3 Grid Integration**: Direct access to H3 hierarchical spatial indexing
- **Comprehensive Testing**: Automated validation of all components

### 🏗️ **Architecture Overview**

```
GEO-INFER-SPACE/
├── src/geo_infer_space/osc_geo/     # Integration modules
│   ├── utils/                       # Core utilities
│   │   ├── osc_setup_all.py        # Main setup script
│   │   ├── osc_simple_status.py    # Status checking
│   │   ├── visualization.py        # Visualization engine
│   │   └── enhanced_reporting.py   # Advanced reporting
│   └── core/                        # Core functionality
├── ext/os-climate/                  # External OSC repositories
│   ├── osc-geo-h3grid-srv/         # H3 grid service
│   └── osc-geo-h3loader-cli/       # Data loader CLI
└── reports/                         # Generated reports & visualizations
    ├── visualizations/              # Charts and graphs
    │   ├── status/                  # Repository status plots
    │   ├── tests/                   # Test analysis charts
    │   └── interactive/             # Interactive maps
    └── *.html                       # Interactive dashboards
```

---

## 🚀 Quick Start

### **1-Minute Setup**

```bash
# Clone the main repository
cd GEO-INFER-SPACE

# Install dependencies (including visualization libraries)
pip install -e .

# Run the complete setup with enhanced reporting
python3 osc_setup_all.py --force-clone

# Check status with visualizations
python3 osc_status.py

# View interactive dashboard
open reports/status_dashboard_*.html
```

### **Key Commands**

| Command | Description | Output |
|---------|-------------|---------|
| `python3 osc_setup_all.py` | Full setup with test suite | JSON report + HTML dashboard |
| `python3 osc_status.py` | Check repository status | Console output + JSON report |
| `python3 osc_wrapper.py` | Wrapper for common operations | Varies by operation |

---

## 📦 Installation & Setup

### **Prerequisites**

```bash
# System requirements
python >= 3.9
git
pkg-config (for some dependencies)
gfortran (for scientific packages)
GDAL libraries (for geospatial functionality)
```

### **Python Dependencies**

The setup automatically installs all required dependencies:

```bash
# Core dependencies
numpy>=1.20.0
geopandas>=0.10.0
h3>=3.7.0

# Visualization dependencies
matplotlib>=3.5.0
seaborn>=0.11.0
folium>=0.12.0
plotly>=5.0.0

# API dependencies
fastapi>=0.68.0
uvicorn>=0.15.0
```

### **Installation Options**

#### **Option 1: Standard Installation**
```bash
cd GEO-INFER-SPACE
pip install -e .
python3 osc_setup_all.py
```

#### **Option 2: Development Installation**
```bash
cd GEO-INFER-SPACE
pip install -e ".[dev]"
python3 osc_setup_all.py --force-clone
```

#### **Option 3: Minimal Installation (no visualizations)**
```bash
cd GEO-INFER-SPACE
pip install -e . --no-deps
pip install numpy pandas geopandas h3
python3 osc_setup_all.py --skip-tests
```

---

## 🔧 Repository Management

### **OSC Repositories**

The integration manages two key OS Climate repositories:

#### **1. osc-geo-h3grid-srv**
- **Purpose**: H3 grid service for geospatial applications
- **Features**: RESTful API for H3 grid operations
- **Path**: `ext/os-climate/osc-geo-h3grid-srv/`

#### **2. osc-geo-h3loader-cli**
- **Purpose**: Command-line tool for H3 data loading
- **Features**: Batch processing, visualization
- **Path**: `ext/os-climate/osc-geo-h3loader-cli/`

### **Repository Operations**

#### **Setup & Cloning**
```bash
# Force fresh clone of all repositories
python3 osc_setup_all.py --force-clone

# Clone to custom directory
python3 osc_setup_all.py --output-dir /custom/path

# Skip automated testing
python3 osc_setup_all.py --skip-tests
```

#### **Status Checking**
```bash
# Comprehensive status check
python3 osc_status.py

# Save status to file
python3 osc_status.py --output-file status_report.json

# Quiet mode (minimal output)
python3 osc_status.py --quiet
```

#### **Repository Health Monitoring**
```python
from geo_infer_space.osc_geo.utils import check_repo_status, generate_summary

# Get detailed status
status = check_repo_status()
print(generate_summary(status))

# Check specific aspects
for repo_name, repo_data in status['repositories'].items():
    print(f"{repo_name}:")
    print(f"  Exists: {repo_data['exists']}")
    print(f"  Git Repo: {repo_data['is_git_repo']}")
    print(f"  Has VEnv: {repo_data['has_venv']}")
    print(f"  Branch: {repo_data['current_branch']}")
```

---

## 📊 Enhanced Reporting & Visualizations

### **Automatic Report Generation**

The enhanced reporting system automatically generates:

1. **JSON Reports**: Machine-readable status and test results
2. **HTML Dashboards**: Interactive web-based reports
3. **Static Visualizations**: PNG charts for documentation
4. **Performance Analytics**: Timing and bottleneck analysis

### **Visualization Types**

#### **1. Repository Health Dashboard**
```python
from geo_infer_space.osc_geo.utils import generate_enhanced_status_report

# Generate comprehensive status report with visualizations
report = generate_enhanced_status_report()

# View generated files
print(f"HTML Dashboard: {report['html_dashboard']}")
print(f"Visualizations: {report['visualizations']}")
```

**Includes:**
- Repository existence status (pie chart)
- Git repository validation (bar chart)
- Virtual environment status (matrix)
- Overall health score (gauge)

#### **2. Test Execution Analysis**
```python
from geo_infer_space.osc_geo.utils import generate_enhanced_test_analysis

# Analyze test results with visualizations
analysis = generate_enhanced_test_analysis("reports/osc_setup_report_*.json")

# View analysis results
print(f"Test Summary: {analysis['test_summary']}")
print(f"Dependencies: {analysis['dependency_analysis']}")
```

**Includes:**
- Test execution timeline (Gantt chart)
- Dependency installation analysis
- Performance bottleneck identification
- Success/failure distribution

#### **3. Interactive H3 Maps**
```python
from geo_infer_space.osc_geo.utils.visualization import OSCVisualizationEngine

# Create interactive H3 visualization
viz_engine = OSCVisualizationEngine()
h3_cells = ["8928308280fffff", "8928308280bffff", "892830828083fff"]
map_obj = viz_engine.create_interactive_h3_map(h3_cells, 
                                              title="Sample H3 Grid")
map_obj.save("h3_visualization.html")
```

### **Report Structure**

```
reports/
├── comprehensive_report_YYYYMMDD_HHMMSS.html    # Full interactive report
├── status_dashboard_YYYYMMDD_HHMMSS.html        # Status-only dashboard
├── enhanced_status_report_YYYYMMDD_HHMMSS.json  # Status data
├── test_analysis_YYYYMMDD_HHMMSS.json           # Test analysis data
└── visualizations/
    ├── status/
    │   ├── repository_health_YYYYMMDD_HHMMSS.png
    │   ├── git_timeline_YYYYMMDD_HHMMSS.png
    │   └── environment_status_YYYYMMDD_HHMMSS.png
    ├── tests/
    │   ├── test_summary_YYYYMMDD_HHMMSS.png
    │   ├── dependency_analysis_YYYYMMDD_HHMMSS.png
    │   └── test_timeline_YYYYMMDD_HHMMSS.png
    └── interactive/
        └── h3_maps/
```

---

## 🛠️ API Reference

### **Core Functions**

#### **Status Checking**
```python
from geo_infer_space.osc_geo.utils import check_repo_status, generate_summary

def check_repo_status() -> Dict[str, Any]:
    """
    Check the status of all OSC repositories.
    
    Returns:
        Dict containing repository status information
    """

def generate_summary(status_data: Dict[str, Any]) -> str:
    """
    Generate human-readable summary of repository status.
    
    Args:
        status_data: Output from check_repo_status()
        
    Returns:
        Formatted summary string
    """
```

#### **Enhanced Reporting**
```python
from geo_infer_space.osc_geo.utils.enhanced_reporting import EnhancedOSCReporter

class EnhancedOSCReporter:
    def __init__(self, output_dir: str = "reports", enable_visualizations: bool = True):
        """Initialize enhanced reporter."""
        
    def generate_enhanced_status_report(self, 
                                      include_visualizations: bool = True,
                                      save_json: bool = True,
                                      save_html: bool = True) -> Dict[str, Any]:
        """Generate comprehensive status report."""
        
    def analyze_test_results(self, 
                           test_report_path: str,
                           include_visualizations: bool = True) -> Dict[str, Any]:
        """Analyze test execution results."""
        
    def generate_comprehensive_report(self, 
                                   test_report_path: str = None) -> Dict[str, Any]:
        """Generate combined status and test analysis report."""
```

#### **Visualization Engine**
```python
from geo_infer_space.osc_geo.utils.visualization import OSCVisualizationEngine

class OSCVisualizationEngine:
    def __init__(self, output_dir: str = "reports/visualizations"):
        """Initialize visualization engine."""
        
    def generate_status_dashboard(self, 
                                 status_data: Dict[str, Any],
                                 save_plots: bool = True) -> Dict[str, Figure]:
        """Generate status visualization dashboard."""
        
    def generate_test_results_analysis(self, 
                                     test_report_path: str,
                                     save_plots: bool = True) -> Dict[str, Figure]:
        """Generate test results analysis visualizations."""
        
    @staticmethod
    def create_interactive_h3_map(h3_cells: List[str], 
                                 values: List[float] = None,
                                 center: Tuple[float, float] = None,
                                 zoom: int = 8,
                                 title: str = "H3 Visualization") -> folium.Map:
        """Create interactive H3 cells visualization."""
```

### **Convenience Functions**

```python
# Quick status visualization
from geo_infer_space.osc_geo.utils import quick_status_visualization
figures = quick_status_visualization(status_data)

# Quick test analysis
from geo_infer_space.osc_geo.utils import quick_test_visualization
figures = quick_test_visualization("test_report.json")

# Comprehensive reporting
from geo_infer_space.osc_geo.utils import generate_comprehensive_osc_report
report = generate_comprehensive_osc_report("test_report.json")
```

---

## 🐛 Troubleshooting

### **Common Issues**

#### **1. Repository Clone Failures**
```bash
# Issue: Network connectivity or GitHub access
# Solution:
git config --global http.proxy http://proxy:port  # If behind proxy
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"  # Generate SSH key
```

#### **2. Dependency Installation Failures**
```bash
# Issue: Missing system dependencies
# Solution (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install build-essential gfortran pkg-config
sudo apt-get install libgdal-dev gdal-bin

# Solution (macOS):
brew install gcc pkg-config gdal

# Solution (Windows):
# Use conda or install pre-compiled wheels
conda install -c conda-forge geopandas rasterio
```

#### **3. Visualization Dependencies**
```bash
# Issue: matplotlib/seaborn not available
# Solution:
pip install matplotlib seaborn plotly folium

# For headless servers:
export MPLBACKEND=Agg
```

#### **4. Virtual Environment Issues**
```bash
# Issue: Virtual environment creation fails
# Solution:
python3 -m venv venv_name
source venv_name/bin/activate  # Linux/macOS
venv_name\Scripts\activate     # Windows
pip install --upgrade pip setuptools wheel
```

### **Debugging Tools**

#### **Diagnostic Commands**
```python
from geo_infer_space.osc_geo.utils import run_diagnostics

# Run comprehensive diagnostics
diagnostics = run_diagnostics()
print(diagnostics)
```

#### **Log Analysis**
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Run setup with detailed logging
python3 osc_setup_all.py --force-clone
```

#### **Manual Testing**
```bash
# Test individual repositories
cd ext/os-climate/osc-geo-h3grid-srv
python3 -m venv venv
source venv/bin/activate
pip install -e .
python3 -m pytest tests/ -v

cd ../osc-geo-h3loader-cli
python3 -m venv venv
source venv/bin/activate
pip install -e .
python3 -m pytest tests/ -v
```

---

## 💡 Integration Examples

### **Example 1: Basic Status Monitoring**
```python
#!/usr/bin/env python3
"""
Basic OSC status monitoring script.
"""

from geo_infer_space.osc_geo.utils import check_repo_status, generate_summary
import json

def monitor_osc_health():
    """Monitor OSC repository health."""
    status = check_repo_status()
    summary = generate_summary(status)
    
    print("=== OSC Health Report ===")
    print(summary)
    
    # Save detailed status
    with open("osc_health.json", "w") as f:
        json.dump(status, f, indent=2)
    
    return status

if __name__ == "__main__":
    monitor_osc_health()
```

### **Example 2: Automated Reporting with Notifications**
```python
#!/usr/bin/env python3
"""
Automated OSC reporting with email notifications.
"""

from geo_infer_space.osc_geo.utils.enhanced_reporting import EnhancedOSCReporter
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_and_notify():
    """Generate OSC report and send notifications."""
    reporter = EnhancedOSCReporter()
    
    # Generate comprehensive report
    report = reporter.generate_enhanced_status_report()
    
    # Check for issues
    status_data = report['status_data']
    issues = []
    
    for repo_name, repo_data in status_data['repositories'].items():
        if not repo_data.get('exists', False):
            issues.append(f"Repository {repo_name} does not exist")
        if not repo_data.get('is_git_repo', False):
            issues.append(f"Repository {repo_name} is not a valid Git repository")
        if not repo_data.get('has_venv', False):
            issues.append(f"Repository {repo_name} missing virtual environment")
    
    # Send notification if issues found
    if issues:
        send_notification(issues, report.get('html_dashboard'))
    
    return report

def send_notification(issues, dashboard_path=None):
    """Send email notification about issues."""
    # Email configuration (customize as needed)
    smtp_server = "your-smtp-server.com"
    smtp_port = 587
    email_user = "your-email@example.com"
    email_password = "your-password"
    recipient = "admin@example.com"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient
    msg['Subject'] = "OSC Integration Issues Detected"
    
    body = "OSC Integration Issues:\n\n"
    for issue in issues:
        body += f"- {issue}\n"
    
    if dashboard_path:
        body += f"\nDetailed dashboard: {dashboard_path}"
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, recipient, text)
        server.quit()
        print("Notification sent successfully")
    except Exception as e:
        print(f"Failed to send notification: {e}")

if __name__ == "__main__":
    generate_and_notify()
```

### **Example 3: H3 Grid Processing Pipeline**
```python
#!/usr/bin/env python3
"""
H3 grid processing pipeline using OSC integration.
"""

import h3
import geopandas as gpd
from geo_infer_space.osc_geo.utils.visualization import OSCVisualizationEngine
from shapely.geometry import Point, Polygon

def process_geospatial_data_with_h3():
    """Process geospatial data using H3 grids."""
    
    # 1. Generate sample data
    sample_points = [
        (40.7128, -74.0060),  # New York
        (34.0522, -118.2437), # Los Angeles
        (41.8781, -87.6298),  # Chicago
        (29.7604, -95.3698),  # Houston
    ]
    
    # 2. Convert to H3 cells
    h3_resolution = 7
    h3_cells = []
    for lat, lon in sample_points:
        h3_cell = h3.latlng_to_cell(lat, lon, h3_resolution)
        h3_cells.append(h3_cell)
    
    # 3. Get neighboring cells
    all_cells = set(h3_cells)
    for cell in h3_cells:
        neighbors = h3.grid_disk(cell, 1)
        all_cells.update(neighbors)
    
    all_cells = list(all_cells)
    
    # 4. Create sample values
    values = [len(h3.grid_disk(cell, 1)) for cell in all_cells]  # Number of neighbors
    
    # 5. Create interactive visualization
    viz_engine = OSCVisualizationEngine()
    
    # Calculate center point
    center_lat = sum(lat for lat, lon in sample_points) / len(sample_points)
    center_lon = sum(lon for lat, lon in sample_points) / len(sample_points)
    
    interactive_map = viz_engine.create_interactive_h3_map(
        h3_cells=all_cells,
        values=values,
        center=(center_lat, center_lon),
        zoom=5,
        title="H3 Grid Analysis - Major US Cities"
    )
    
    # 6. Save interactive map
    if interactive_map:
        interactive_map.save("reports/h3_cities_analysis.html")
        print("Interactive H3 map saved to: reports/h3_cities_analysis.html")
    
    # 7. Create GeoDataFrame for further analysis
    geometries = []
    for cell in all_cells:
        boundary = h3.cell_to_boundary(cell)
        polygon = Polygon([(lon, lat) for lat, lon in boundary])
        geometries.append(polygon)
    
    gdf = gpd.GeoDataFrame({
        'h3_cell': all_cells,
        'value': values[:len(all_cells)],
        'geometry': geometries
    }, crs='EPSG:4326')
    
    # 8. Save to file
    gdf.to_file("reports/h3_analysis.geojson", driver="GeoJSON")
    print("H3 analysis saved to: reports/h3_analysis.geojson")
    
    return gdf, interactive_map

if __name__ == "__main__":
    gdf, map_obj = process_geospatial_data_with_h3()
    print(f"Processed {len(gdf)} H3 cells")
    print(gdf.head())
```

---

## 🎯 Best Practices

### **Development Workflow**

1. **Regular Health Checks**
   ```bash
   # Daily automated check
   python3 osc_status.py --output-file daily_status.json
   ```

2. **Version Control Integration**
   ```bash
   # Add to .gitignore
   echo "ext/os-climate/" >> .gitignore
   echo "reports/*.html" >> .gitignore
   echo "reports/visualizations/" >> .gitignore
   ```

3. **Continuous Integration**
   ```yaml
   # .github/workflows/osc-integration.yml
   name: OSC Integration Test
   on: [push, pull_request]
   jobs:
     test-osc:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Setup Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.9'
         - name: Install dependencies
           run: |
             sudo apt-get update
             sudo apt-get install gfortran libgdal-dev
             pip install -e .
         - name: Run OSC setup
           run: python3 osc_setup_all.py --skip-tests
         - name: Check status
           run: python3 osc_status.py
   ```

### **Performance Optimization**

1. **Caching Strategies**
   ```python
   # Cache repository status for faster checks
   import pickle
   from datetime import datetime, timedelta
   
   def cached_status_check(cache_duration_minutes=30):
       cache_file = "osc_status_cache.pkl"
       
       try:
           with open(cache_file, 'rb') as f:
               cached_data, timestamp = pickle.load(f)
               
           if datetime.now() - timestamp < timedelta(minutes=cache_duration_minutes):
               return cached_data
       except (FileNotFoundError, pickle.PickleError):
           pass
       
       # Perform fresh status check
       status = check_repo_status()
       
       with open(cache_file, 'wb') as f:
           pickle.dump((status, datetime.now()), f)
       
       return status
   ```

2. **Parallel Processing**
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def parallel_repo_check():
       """Check multiple repositories in parallel."""
       from geo_infer_space.osc_geo.utils.osc_simple_status import check_single_repo
       
       repos = ["osc-geo-h3grid-srv", "osc-geo-h3loader-cli"]
       
       with ThreadPoolExecutor(max_workers=2) as executor:
           futures = {executor.submit(check_single_repo, repo): repo for repo in repos}
           results = {}
           
           for future in futures:
               repo = futures[future]
               try:
                   results[repo] = future.result()
               except Exception as e:
                   results[repo] = {"error": str(e)}
       
       return results
   ```

### **Security Considerations**

1. **Repository Verification**
   ```python
   import hashlib
   
   def verify_repository_integrity(repo_path):
       """Verify repository integrity using checksums."""
       # Implementation would check known file hashes
       pass
   ```

2. **Sandboxed Execution**
   ```python
   import subprocess
   import tempfile
   
   def run_in_sandbox(command, repo_path):
       """Run commands in sandboxed environment."""
       with tempfile.TemporaryDirectory() as temp_dir:
           # Copy repository to temporary location
           # Run command in isolated environment
           pass
   ```

---

## ⚙️ Advanced Configuration

### **Custom Repository Sources**

```python
# config/custom_repos.yaml
repositories:
  - name: "custom-h3-extension"
    url: "https://github.com/your-org/custom-h3-extension.git"
    branch: "main"
    setup_script: "setup.py"
    test_command: "python -m pytest"
  
  - name: "spatial-analytics-tools" 
    url: "https://github.com/your-org/spatial-analytics.git"
    branch: "develop"
    setup_script: "requirements.txt"
    test_command: "python -m unittest"
```

### **Environment Configuration**

```python
# config/osc_config.py
import os
from pathlib import Path

class OSCConfig:
    """Configuration for OSC integration."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    EXT_DIR = BASE_DIR / "ext" / "os-climate"
    REPORTS_DIR = BASE_DIR / "reports"
    
    # Repository configuration
    REPOS = [
        {
            "name": "osc-geo-h3grid-srv",
            "url": "https://github.com/docxology/osc-geo-h3grid-srv.git",  # Fork of https://github.com/os-climate/osc-geo-h3grid-srv
        },
        {
            "name": "osc-geo-h3loader-cli", 
            "url": "https://github.com/docxology/osc-geo-h3loader-cli.git",  # Fork of https://github.com/os-climate/osc-geo-h3loader-cli
        }
    ]
    
    # Visualization settings
    VISUALIZATION_DPI = 300
    FIGURE_SIZE = (12, 8)
    COLOR_PALETTE = "husl"
    
    # Performance settings
    PARALLEL_WORKERS = 2
    CACHE_DURATION_MINUTES = 30
    
    # Reporting settings
    ENABLE_HTML_REPORTS = True
    ENABLE_VISUALIZATIONS = True
    AUTO_OPEN_DASHBOARD = False
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Override with environment variables
        config.EXT_DIR = Path(os.getenv("OSC_EXT_DIR", config.EXT_DIR))
        config.REPORTS_DIR = Path(os.getenv("OSC_REPORTS_DIR", config.REPORTS_DIR))
        config.ENABLE_VISUALIZATIONS = os.getenv("OSC_ENABLE_VIZ", "true").lower() == "true"
        
        return config
```

### **Plugin System**

```python
# plugins/custom_visualizer.py
from geo_infer_space.osc_geo.utils.visualization import OSCVisualizationEngine

class CustomOSCVisualizer(OSCVisualizationEngine):
    """Custom visualizer with additional features."""
    
    def create_3d_repository_health(self, status_data):
        """Create 3D visualization of repository health."""
        # Custom 3D visualization implementation
        pass
    
    def generate_time_series_analysis(self, historical_reports):
        """Generate time-series analysis of repository health."""
        # Time-series analysis implementation
        pass

# Register plugin
from geo_infer_space.osc_geo.utils import register_visualizer_plugin
register_visualizer_plugin("custom", CustomOSCVisualizer)
```

---

## 📚 References

- [OS Climate GitHub Organization](https://github.com/docxology) (original source, we use forks at github.com/docxology)
- [H3 Hierarchical Hexagonal Geospatial Indexing](https://h3geo.org/)
- [GEO-INFER Framework Documentation](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Folium Documentation](https://python-visualization.github.io/folium/)

---

## 🤝 Contributing

Contributions to the OSC integration are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Add tests** for new functionality
3. **Update documentation** for any API changes
4. **Follow the existing code style** and conventions
5. **Submit a pull request** with a clear description

### **Development Setup**

```bash
# Clone for development
git clone https://github.com/your-fork/GEO-INFER.git
cd GEO-INFER/GEO-INFER-SPACE

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Run OSC integration tests
python3 osc_setup_all.py --force-clone
```

---

## 📄 License

This module is part of the GEO-INFER framework and is licensed under the Creative Commons Attribution-NoDerivatives-ShareAlike 4.0 International License (CC BY-ND-SA 4.0).

---

*Last updated: June 18, 2025*
*Version: 1.0.0* 