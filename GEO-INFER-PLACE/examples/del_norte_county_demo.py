#!/usr/bin/env python3
"""
Del Norte County Comprehensive Dashboard Demonstration

This script demonstrates the full capabilities of the Del Norte County comprehensive
dashboard including real California data integration, H3 spatial analysis, multi-domain
analysis (forest health, coastal resilience, fire risk), and interactive visualization
generation adapted from the climate integration example.

Usage:
    python del_norte_county_demo.py [--config CONFIG_PATH] [--output OUTPUT_DIR] [--api-keys API_KEYS_FILE]

Example:
    python del_norte_county_demo.py --output ./del_norte_dashboard --api-keys api_keys.json

Required packages:
    - folium
    - h3
    - pandas
    - geopandas
    - numpy
    - requests
"""

import sys
import subprocess
import importlib
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
import traceback

# Configure basic logging early
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('del_norte_demo.log')
    ]
)

logger = logging.getLogger(__name__)

def check_and_install_dependencies():
    """Check and install required dependencies with comprehensive logging."""
    logger.info("=== Comprehensive Dependency Check ===")
    
    # Extended list of required packages for advanced dashboard
    required_packages = {
        # Core geospatial packages
        'folium': 'folium',
        'h3': 'h3',
        'pandas': 'pandas', 
        'geopandas': 'geopandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'yaml': 'PyYAML',
        
        # Advanced visualization packages
        'plotly': 'plotly',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'branca': 'branca',
        
        # Scientific computing packages
        'scipy': 'scipy',
        'sklearn': 'scikit-learn',
        
        # Additional utility packages
        'shapely': 'shapely',
        'rasterio': 'rasterio',
        'fiona': 'fiona'
    }
    
    # Optional packages that enhance functionality
    optional_packages = {
        'contextily': 'contextily',
        'cartopy': 'cartopy',
        'descartes': 'descartes',
        'pyproj': 'pyproj'
    }
    
    available_packages = []
    missing_packages = []
    optional_available = []
    optional_missing = []
    
    logger.info("Checking core required packages...")
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            available_packages.append(module_name)
            logger.info(f"✓ {module_name} is available")
        except ImportError:
            missing_packages.append(package_name)
            logger.warning(f"✗ {module_name} is missing - will install {package_name}")
    
    logger.info("Checking optional enhancement packages...")
    for module_name, package_name in optional_packages.items():
        try:
            importlib.import_module(module_name)
            optional_available.append(module_name)
            logger.info(f"✓ {module_name} (optional) is available")
        except ImportError:
            optional_missing.append(package_name)
            logger.info(f"○ {module_name} (optional) is missing")
    
    # Install missing required packages
    if missing_packages:
        logger.info(f"\nInstalling {len(missing_packages)} missing required packages: {', '.join(missing_packages)}")
        try:
            install_cmd = [sys.executable, '-m', 'pip', 'install', '--user'] + missing_packages
            logger.info(f"Running: {' '.join(install_cmd)}")
            
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✓ Successfully installed missing required packages")
                logger.info(f"Installation output: {result.stdout}")
            else:
                logger.error(f"✗ Failed to install packages: {result.stderr}")
                logger.error("Please install manually:")
                logger.error(f"pip install {' '.join(missing_packages)}")
                return False
        except Exception as e:
            logger.error(f"✗ Installation failed with exception: {e}")
            return False
    
    # Attempt to install some optional packages for enhanced functionality
    if optional_missing:
        logger.info(f"\nAttempting to install {len(optional_missing)} optional packages for enhanced functionality...")
        safe_optional = ['contextily', 'pyproj']  # Packages that usually install without issues
        safe_to_install = [pkg for pkg in optional_missing if pkg in safe_optional]
        
        if safe_to_install:
            try:
                install_cmd = [sys.executable, '-m', 'pip', 'install', '--user'] + safe_to_install
                logger.info(f"Installing optional packages: {' '.join(safe_to_install)}")
                result = subprocess.run(install_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✓ Successfully installed optional packages: {', '.join(safe_to_install)}")
                else:
                    logger.warning(f"⚠ Optional package installation had issues: {result.stderr}")
            except Exception as e:
                logger.warning(f"⚠ Optional package installation failed: {e}")
    
    # Summary
    logger.info("=== Dependency Check Summary ===")
    logger.info(f"✓ Available required packages: {len(available_packages)}/{len(required_packages)}")
    logger.info(f"✓ Available optional packages: {len(optional_available)}/{len(optional_packages)}")
    
    if available_packages:
        logger.info(f"Core packages available: {', '.join(available_packages)}")
    if optional_available:
        logger.info(f"Optional packages available: {', '.join(optional_available)}")
    
    return len(missing_packages) == 0

# Check dependencies first
print("=== Checking Dependencies ===")
if not check_and_install_dependencies():
    print("Dependencies check failed. Please install missing packages manually.")
    sys.exit(1)

# Now import the modules after ensuring dependencies are available
print("=== Importing Core Modules ===")
try:
    import folium
    print(f"✓ folium version: {folium.__version__}")
except ImportError as e:
    print(f"✗ folium import failed: {e}")

try:
    import h3
    print(f"✓ h3 version: {h3.__version__}")
except ImportError as e:
    print(f"✗ h3 import failed: {e}")

try:
    import pandas as pd
    print(f"✓ pandas version: {pd.__version__}")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    import numpy as np
    print(f"✓ numpy version: {np.__version__}")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

try:
    import requests
    print(f"✓ requests version: {requests.__version__}")
except ImportError as e:
    print(f"✗ requests import failed: {e}")

# Try to import advanced visualization packages
try:
    import plotly
    print(f"✓ plotly version: {plotly.__version__}")
except ImportError as e:
    print(f"○ plotly not available: {e}")

try:
    import matplotlib
    print(f"✓ matplotlib version: {matplotlib.__version__}")
except ImportError as e:
    print(f"○ matplotlib not available: {e}")

try:
    import seaborn
    print(f"✓ seaborn version: {seaborn.__version__}")
except ImportError as e:
    print(f"○ seaborn not available: {e}")

print("=== Core Module Import Complete ===")
print()

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import with fallbacks for missing modules
try:
    from geo_infer_place.locations.del_norte_county.comprehensive_dashboard import DelNorteComprehensiveDashboard
except ImportError as e:
    print(f"Warning: Could not import comprehensive dashboard: {e}")
    print("Will use component demonstrations only.")
    DelNorteComprehensiveDashboard = None

# Import the new advanced dashboard
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from geo_infer_place.locations.del_norte_county.advanced_dashboard import AdvancedDashboard
    print("✓ Advanced dashboard imported successfully")
except ImportError as e:
    print(f"Warning: Could not import advanced dashboard: {e}")
    print("Will create simplified dashboard instead.")
    AdvancedDashboard = None

try:
    from geo_infer_space.utils.config_loader import LocationConfigLoader
    from geo_infer_place.utils.data_sources import CaliforniaDataSources
    from geo_infer_space.core.api_clients import BaseAPIManager  # Or appropriate general class
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    print("Running with simplified functionality only.")
    LocationConfigLoader = CaliforniaDataSources = BaseAPIManager = None

# Logging already configured earlier in the file

def load_api_keys(api_keys_file: str) -> dict:
    """Load API keys from JSON file."""
    try:
        with open(api_keys_file, 'r') as f:
            api_keys = json.load(f)
        logger.info(f"Loaded API keys from {api_keys_file}")
        return api_keys
    except FileNotFoundError:
        logger.warning(f"API keys file not found: {api_keys_file}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing API keys file: {e}")
        return {}

def demonstrate_data_sources():
    """Demonstrate the California data sources catalog."""
    logger.info("=== Demonstrating California Data Sources Catalog ===")
    
    if CaliforniaDataSources is None:
        logger.warning("CaliforniaDataSources not available - using mock demonstration")
        logger.info("Mock data sources would include:")
        logger.info("  - CAL FIRE: Wildfire perimeter data, fire weather, fuel moisture")
        logger.info("  - NOAA: Weather observations, climate data, coastal monitoring")
        logger.info("  - USGS: Water data, seismic monitoring, topographic data")
        logger.info("  - CDEC: California environmental monitoring")
        logger.info("Total mock data sources: 20+")
        return {'mock': True, 'sources': 20}
    
    data_sources = CaliforniaDataSources()
    
    # Get summary of available data sources
    summary = data_sources.get_source_summary()
    logger.info(f"Total data sources available: {summary['total_sources']}")
    logger.info(f"Categories: {list(summary['categories'].keys())}")
    
    # Show fire-related data sources
    fire_sources = data_sources.get_sources_by_category('fire')
    logger.info(f"Fire-related data sources: {len(fire_sources)}")
    for source in fire_sources[:3]:  # Show first 3
        logger.info(f"  - {source.name}: {source.description[:100]}...")
    
    # Show coastal data sources
    coastal_sources = data_sources.get_sources_by_category('coastal')
    logger.info(f"Coastal data sources: {len(coastal_sources)}")
    
    # Demonstrate location-specific source discovery
    del_norte_bounds = (-124.4, 41.5, -123.5, 42.0)  # Del Norte County approximate bounds
    location_sources = data_sources.get_sources_for_location(
        location_bounds=del_norte_bounds,
        location_name="Del Norte County"
    )
    
    logger.info(f"High-priority sources for Del Norte County: {len(location_sources['high_priority'])}")
    logger.info(f"Medium-priority sources: {len(location_sources['medium_priority'])}")
    
    return data_sources

def demonstrate_api_connections(api_keys: dict):
    """Demonstrate API connections and validation."""
    logger.info("=== Demonstrating API Connections ===")
    
    if BaseAPIManager is None:
        logger.warning("CaliforniaAPIManager not available - using mock demonstration")
        logger.info("Mock API connections would test:")
        logger.info("  ✓ CAL FIRE API: Fire perimeter data (Mock: 150ms)")
        logger.info("  ✓ NOAA API: Weather data (Mock: 250ms)")
        logger.info("  ✓ USGS API: Water/seismic data (Mock: 180ms)")
        logger.info("  ✓ CDEC API: Environmental monitoring (Mock: 300ms)")
        return {'mock': True, 'connections': 4}
    
    api_manager = BaseAPIManager(api_keys)
    
    # Validate all connections
    validation_results = api_manager.validate_all_connections()
    
    for service, result in validation_results.items():
        status = "✓ Connected" if result.get('accessible', False) else "✗ Failed"
        response_time = result.get('response_time_ms', 'N/A')
        logger.info(f"{service}: {status} (Response: {response_time}ms)")
        
        if not result.get('accessible', False) and 'error' in result:
            logger.warning(f"  Error: {result['error']}")
    
    return api_manager

def run_comprehensive_demo(config_path: str = None, 
                          output_dir: str = None, 
                          api_keys: dict = None):
    """Run the comprehensive Del Norte County dashboard demonstration."""
    logger.info("=== Starting Del Norte County Comprehensive Dashboard Demo ===")
    
    if DelNorteComprehensiveDashboard is None:
        logger.warning("Comprehensive dashboard not available - running simplified demo")
        return run_simplified_demo(output_dir, api_keys)
    
    try:
        # Initialize dashboard
        logger.info("Initializing comprehensive dashboard...")
        dashboard = DelNorteComprehensiveDashboard(
            config_path=config_path,
            api_keys=api_keys or {},
            h3_resolution=8,
            output_dir=output_dir or "./del_norte_dashboard"
        )
        
        # Step 1: Load configuration
        logger.info("Step 1: Loading configuration...")
        config = dashboard.load_configuration()
        logger.info(f"Configuration loaded for location: {config.get('location_code', 'Unknown')}")
        
        if dashboard.location_bounds:
            logger.info(f"Location bounds: {dashboard.location_bounds.to_bbox()}")
            center = dashboard.location_bounds.center()
            logger.info(f"Center coordinates: {center[0]:.4f}, {center[1]:.4f}")
        
        # Step 2: Fetch real data
        logger.info("Step 2: Fetching real data from APIs...")
        real_data = dashboard.fetch_real_data()
        
        successful_fetches = sum(1 for result in real_data.values() if result.success)
        total_fetches = len(real_data)
        logger.info(f"Data fetch results: {successful_fetches}/{total_fetches} successful")
        
        for data_type, response in real_data.items():
            status = "✓" if response.success else "✗"
            logger.info(f"  {status} {data_type}: {response.error or 'Success'}")
        
        # Step 3: Run comprehensive analysis
        logger.info("Step 3: Running comprehensive analysis...")
        analysis_results = dashboard.run_comprehensive_analysis()
        
        logger.info(f"Analysis completed for {len(analysis_results)} domains:")
        for domain, results in analysis_results.items():
            logger.info(f"  ✓ {domain}")
        
        # Step 4: Generate interactive dashboard
        logger.info("Step 4: Generating interactive dashboard...")
        dashboard_path = dashboard.generate_comprehensive_dashboard()
        logger.info(f"Interactive dashboard generated: {dashboard_path}")
        
        # Step 5: Export analysis results
        logger.info("Step 5: Exporting analysis results...")
        results_path = dashboard.export_analysis_results()
        logger.info(f"Analysis results exported: {results_path}")
        
        # Step 6: Generate summary report
        logger.info("Step 6: Generating summary report...")
        summary_report = dashboard.generate_summary_report()
        
        # Save summary report
        summary_path = Path(dashboard.output_dir) / f"del_norte_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_path, 'w') as f:
            f.write(summary_report)
        
        logger.info(f"Summary report saved: {summary_path}")
        
        # Display key results
        logger.info("=== Key Analysis Results ===")
        if 'h3_aggregation' in analysis_results:
            h3_data = analysis_results['h3_aggregation']
            logger.info(f"H3 spatial analysis:")
            logger.info(f"  - Total H3 cells: {h3_data.get('total_cells', 0)}")
            logger.info(f"  - Coverage area: {h3_data.get('coverage_area_km2', 0):.2f} km²")
            logger.info(f"  - Resolution: {h3_data.get('resolution', 'Unknown')}")
        
        if 'integration' in analysis_results:
            integration = analysis_results['integration']
            logger.info(f"Cross-domain integration:")
            logger.info(f"  - Climate vulnerability index: {dashboard._calculate_climate_vulnerability_index():.2f}")
            logger.info(f"  - Integrated risk score: {dashboard._calculate_integrated_risk_score():.2f}")
        
        # Success summary
        logger.info("=== Demo Completed Successfully ===")
        logger.info(f"Dashboard: {dashboard_path}")
        logger.info(f"Results: {results_path}")
        logger.info(f"Summary: {summary_path}")
        
        return {
            'success': True,
            'dashboard_path': dashboard_path,
            'results_path': results_path,
            'summary_path': str(summary_path),
            'analysis_results': analysis_results
        }
        
    except Exception as e:
        logger.error(f"Demo failed with error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}

def demonstrate_h3_spatial_analysis():
    """Demonstrate H3 spatial analysis capabilities."""
    logger.info("=== Demonstrating H3 Spatial Analysis ===")
    
    import h3
    import numpy as np
    
    # Del Norte County center
    center_lat, center_lon = 41.75, -124.0
    
    # Generate H3 cells at different resolutions
    resolutions = [6, 7, 8, 9]
    for resolution in resolutions:
        # Use correct H3 function name based on version
        try:
            h3_cell = h3.latlng_to_cell(center_lat, center_lon, resolution)
        except AttributeError:
            h3_cell = h3.latlng_to_cell(center_lat, center_lon, resolution)
        
        try:
            cell_area = h3.cell_area(h3_cell, unit='km^2')
        except:
            cell_area = h3.hex_area(resolution, unit='km^2')
        
        # Get neighboring cells
        try:
            neighbors = h3.grid_ring(h3_cell, 1)
        except AttributeError:
            neighbors = h3.grid_ring_unsafe(h3_cell, 1)
        
        logger.info(f"Resolution {resolution}:")
        logger.info(f"  - Cell: {h3_cell}")
        logger.info(f"  - Area: {cell_area:.2f} km²")
        logger.info(f"  - Neighbors: {len(neighbors)}")
    
    # Generate a small H3 grid for Del Norte County
    logger.info("Generating H3 grid for Del Norte County...")
    
    # Approximate Del Norte County bounds
    north, south = 42.0, 41.5
    east, west = -123.5, -124.4
    
    # Generate grid of points
    lat_points = np.linspace(south, north, 10)
    lon_points = np.linspace(west, east, 10)
    
    h3_cells = set()
    for lat in lat_points:
        for lon in lon_points:
            try:
                cell = h3.latlng_to_cell(lat, lon, 8)
            except AttributeError:
                cell = h3.latlng_to_cell(lat, lon, 8)
            h3_cells.add(cell)
    
    try:
        total_area = sum(h3.cell_area(cell, unit='km^2') for cell in h3_cells)
    except:
        total_area = len(h3_cells) * h3.hex_area(8, unit='km^2')
    
    logger.info(f"Generated {len(h3_cells)} H3 cells covering {total_area:.2f} km²")
    
    return h3_cells

def run_simplified_demo(output_dir: str = None, api_keys: dict = None):
    """Run a simplified demo with basic functionality."""
    logger.info("=== Running Simplified Del Norte County Demo ===")
    
    output_path = Path(output_dir or "./del_norte_dashboard")
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create a basic folium map for Del Norte County
        center_lat, center_lon = 41.75, -124.0  # Del Norte County center
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add some sample markers for Del Norte County
        locations = [
            {"name": "Crescent City", "lat": 41.7558, "lon": -124.2026, "type": "City"},
            {"name": "Redwood National Park", "lat": 41.2133, "lon": -124.0046, "type": "Park"},
            {"name": "Smith River", "lat": 41.9278, "lon": -124.1473, "type": "River"},
            {"name": "Klamath", "lat": 41.5254, "lon": -124.0373, "type": "Community"}
        ]
        
        # Add markers
        for loc in locations:
            folium.Marker(
                location=[loc['lat'], loc['lon']],
                popup=f"<b>{loc['name']}</b><br>Type: {loc['type']}",
                tooltip=loc['name']
            ).add_to(m)
            
        # Add H3 demonstration
        logger.info("Adding H3 spatial demonstration...")
        
        # Generate some H3 cells
        for i in range(10):
            lat = center_lat + np.random.uniform(-0.2, 0.2)
            lon = center_lon + np.random.uniform(-0.3, 0.3)
            
            # Use correct H3 function name based on version
            try:
                h3_cell = h3.latlng_to_cell(lat, lon, 8)
                h3_boundary = h3.cell_to_boundary(h3_cell)
            except AttributeError:
                h3_cell = h3.latlng_to_cell(lat, lon, 8)
                h3_boundary = h3.cell_to_latlng_boundary(h3_cell, geo_json=True)
            
            folium.Polygon(
                locations=[[lat, lon] for lon, lat in h3_boundary],
                popup=f"H3 Cell: {h3_cell}<br>Resolution: 8",
                color='blue',
                weight=2,
                fill=True,
                fillColor='lightblue',
                fillOpacity=0.3
            ).add_to(m)
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>Del Norte County Simple Demo Map</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        map_path = output_path / f"del_norte_simple_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(str(map_path))
        
        logger.info(f"Simple dashboard saved: {map_path}")
        
        return {
            'success': True,
            'map_path': str(map_path),
            'message': 'Simplified demo completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Simplified demo failed: {e}")
        return {'success': False, 'error': str(e)}

def run_advanced_demo(output_dir: str = None, api_keys: dict = None):
    """Run the advanced geospatial intelligence dashboard demo."""
    logger.info("=== Running Advanced Geospatial Intelligence Dashboard Demo ===")
    
    if AdvancedDashboard is None:
        logger.warning("Advanced dashboard not available - missing imports")
        return {'success': False, 'error': 'Advanced dashboard class not available'}
    
    try:
        # Initialize advanced dashboard
        logger.info("Initializing advanced dashboard with real-time data integration...")
        advanced_dashboard = AdvancedDashboard(
            output_dir=output_dir or "./del_norte_dashboard",
            api_keys=api_keys or {}
        )
        
        # Fetch real-time data
        logger.info("Fetching real-time California data...")
        real_time_data = advanced_dashboard.fetch_real_time_data()
        
        # Log data fetch results
        for data_type, response in real_time_data.items():
            if data_type == 'fetch_timestamp':
                continue
            status = "✓" if response.get('success', False) else "✗"
            logger.info(f"  {status} {data_type}: {response.get('error', 'Success')}")
        
        # Generate comprehensive dashboard
        logger.info("Generating comprehensive intelligence dashboard...")
        dashboard_path = advanced_dashboard.save_dashboard()
        
        # Generate policy report
        logger.info("Generating policy support report...")
        policy_report = advanced_dashboard.generate_policy_report()
        
        # Save policy report
        report_path = Path(advanced_dashboard.output_dir) / f"policy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(policy_report, f, indent=2, default=str)
        
        logger.info(f"Policy report saved: {report_path}")
        
        # Log key insights
        logger.info("=== Advanced Dashboard Key Features ===")
        logger.info("✓ Multi-panel layout with specialized analysis windows")
        logger.info("✓ Real-time California dataset integration")
        logger.info("✓ Interactive layer toggles and controls")
        logger.info("✓ Climate, zoning, and agro-economic analysis")
        logger.info("✓ H3 spatial indexing and forest health analysis")
        logger.info("✓ Policy scenario modeling capabilities")
        logger.info("✓ Advanced visualization and reporting")
        
        return {
            'success': True,
            'dashboard_path': dashboard_path,
            'policy_report_path': str(report_path),
            'real_time_data': real_time_data,
            'message': 'Advanced dashboard generated successfully'
        }
        
    except Exception as e:
        logger.error(f"Advanced dashboard demo failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)}

def main():
    """Main demonstration function."""
    parser = argparse.ArgumentParser(
        description="Del Norte County Comprehensive Dashboard Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python del_norte_county_demo.py
  python del_norte_county_demo.py --output ./dashboard_output
  python del_norte_county_demo.py --api-keys api_keys.json --output ./results
  python del_norte_county_demo.py --config custom_config.yaml --output ./custom_dashboard

API Keys File Format (JSON):
{
  "noaa": "your_noaa_api_key",
  "calfire": "your_calfire_api_key",
  "usgs": "your_usgs_api_key",
  "cdec": "your_cdec_api_key"
}
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='./del_norte_dashboard',
        help='Output directory for generated files (default: ./del_norte_dashboard)'
    )
    
    parser.add_argument(
        '--api-keys',
        type=str,
        help='Path to JSON file containing API keys'
    )
    
    parser.add_argument(
        '--demo-only',
        action='store_true',
        help='Run component demonstrations only (no full dashboard generation)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=== Del Norte County Comprehensive Dashboard Demo ===")
    logger.info(f"Arguments: {vars(args)}")
    
    # Load API keys if provided
    api_keys = {}
    if args.api_keys:
        api_keys = load_api_keys(args.api_keys)
    
    # Run component demonstrations
    logger.info("Running component demonstrations...")
    
    # Demonstrate data sources catalog
    data_sources = demonstrate_data_sources()
    
    # Demonstrate API connections
    api_manager = demonstrate_api_connections(api_keys)
    
    # Demonstrate H3 spatial analysis
    h3_cells = demonstrate_h3_spatial_analysis()
    
    if args.demo_only:
        logger.info("Demo-only mode completed.")
        return
    
    # Run both simple and advanced dashboards
    logger.info("=== Running Dual Dashboard Generation ===")
    
    # Generate simple dashboard
    logger.info("Step 1: Generating simple dashboard...")
    simple_result = run_simplified_demo(
        output_dir=args.output,
        api_keys=api_keys
    )
    
    # Generate advanced dashboard
    logger.info("Step 2: Generating advanced geospatial intelligence dashboard...")
    advanced_result = run_advanced_demo(
        output_dir=args.output,
        api_keys=api_keys
    )
    
    # Try comprehensive demo if available
    comprehensive_result = None
    if DelNorteComprehensiveDashboard is not None:
        logger.info("Step 3: Attempting comprehensive dashboard (if available)...")
        comprehensive_result = run_comprehensive_demo(
            config_path=args.config,
            output_dir=args.output,
            api_keys=api_keys
        )
    
    # Open dashboards in browser
    import webbrowser
    dashboard_paths = []
    
    if simple_result.get('success', False):
        simple_path = simple_result['map_path']
        dashboard_paths.append(('Simple Dashboard', simple_path))
        logger.info(f"Opening simple dashboard: {simple_path}")
        webbrowser.open(f'file://{Path(simple_path).absolute()}')
    
    if advanced_result.get('success', False):
        advanced_path = advanced_result['dashboard_path']
        dashboard_paths.append(('Advanced Intelligence Dashboard', advanced_path))
        logger.info(f"Opening advanced dashboard: {advanced_path}")
        # Open advanced dashboard in a new tab after a small delay
        import threading
        import time
        def open_advanced():
            time.sleep(2)  # 2 second delay
            webbrowser.open(f'file://{Path(advanced_path).absolute()}')
        threading.Thread(target=open_advanced).start()
    
    if comprehensive_result and comprehensive_result.get('success', False):
        comp_path = comprehensive_result.get('dashboard_path') or comprehensive_result.get('map_path')
        if comp_path:
            dashboard_paths.append(('Comprehensive Dashboard', comp_path))
            logger.info(f"Opening comprehensive dashboard: {comp_path}")
            # Open comprehensive dashboard with additional delay
            def open_comprehensive():
                time.sleep(4)  # 4 second delay
                webbrowser.open(f'file://{Path(comp_path).absolute()}')
            threading.Thread(target=open_comprehensive).start()
    
    # Results summary
    success_count = sum([
        simple_result.get('success', False),
        advanced_result.get('success', False),
        comprehensive_result.get('success', False) if comprehensive_result else False
    ])
    
    if success_count > 0:
        logger.info("=== DEMO COMPLETED SUCCESSFULLY ===")
        logger.info(f"Generated {success_count} dashboard(s):")
        
        if simple_result.get('success', False):
            logger.info(f"  📍 Simple Dashboard: {simple_result['map_path']}")
            
        if advanced_result.get('success', False):
            logger.info(f"  🗺️ Advanced Intelligence Dashboard: {advanced_result['dashboard_path']}")
            if 'policy_report_path' in advanced_result:
                logger.info(f"  📄 Policy Report: {advanced_result['policy_report_path']}")
            
        if comprehensive_result and comprehensive_result.get('success', False):
            if 'dashboard_path' in comprehensive_result:
                logger.info(f"  🔬 Comprehensive Dashboard: {comprehensive_result['dashboard_path']}")
            if 'results_path' in comprehensive_result:
                logger.info(f"  📊 Analysis Results: {comprehensive_result['results_path']}")
            if 'summary_path' in comprehensive_result:
                logger.info(f"  📋 Summary Report: {comprehensive_result['summary_path']}")
        
        logger.info("")
        logger.info("=== Dashboard Features Comparison ===")
        logger.info("Simple Dashboard:")
        logger.info("  • Basic geospatial visualization")
        logger.info("  • Sample locations and H3 cells")
        logger.info("  • Quick overview functionality")
        
        if advanced_result.get('success', False):
            logger.info("Advanced Intelligence Dashboard:")
            logger.info("  • Multi-panel layout with specialized analysis")
            logger.info("  • Real-time California data integration")
            logger.info("  • Climate, zoning, and economic analysis")
            logger.info("  • Interactive layer controls and tools")
            logger.info("  • Policy support and scenario modeling")
            logger.info("  • H3 spatial indexing and analytics")
        
        logger.info("")
        logger.info("Next Steps:")
        logger.info("1. Compare the different dashboard approaches")
        logger.info("2. Explore interactive features in each dashboard")
        logger.info("3. Review the policy report for insights")
        logger.info("4. Customize configuration for specific needs")
        logger.info("5. Integrate with additional data sources")
                
    else:
        logger.error("=== ALL DEMOS FAILED ===")
        logger.error("Check the logs above for detailed error information.")
        
        if not simple_result.get('success', False):
            logger.error(f"Simple dashboard error: {simple_result.get('error', 'Unknown')}")
        if not advanced_result.get('success', False):
            logger.error(f"Advanced dashboard error: {advanced_result.get('error', 'Unknown')}")
        if comprehensive_result and not comprehensive_result.get('success', False):
            logger.error(f"Comprehensive dashboard error: {comprehensive_result.get('error', 'Unknown')}")
        
        sys.exit(1)

if __name__ == "__main__":
    main() 