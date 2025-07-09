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

def check_and_install_dependencies():
    """Check and install required dependencies."""
    required_packages = {
        'folium': 'folium',
        'h3': 'h3',
        'pandas': 'pandas', 
        'geopandas': 'geopandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'yaml': 'PyYAML'
    }
    
    missing_packages = []
    
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name} is available")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {module_name} is missing")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '--user'
            ] + missing_packages)
            print("✓ Successfully installed missing packages")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install packages: {e}")
            print("Please install manually:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

# Check dependencies first
print("=== Checking Dependencies ===")
if not check_and_install_dependencies():
    print("Dependencies check failed. Please install missing packages manually.")
    sys.exit(1)

# Now import the modules after ensuring dependencies are available
import folium
import h3
import pandas as pd
import numpy as np
import requests

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import with fallbacks for missing modules
try:
    from geo_infer_place.locations.del_norte_county.comprehensive_dashboard import DelNorteComprehensiveDashboard
except ImportError as e:
    print(f"Warning: Could not import comprehensive dashboard: {e}")
    print("Will use component demonstrations only.")
    DelNorteComprehensiveDashboard = None

try:
    from geo_infer_place.utils.config_loader import LocationConfigLoader
    from geo_infer_place.utils.data_sources import CaliforniaDataSources
    from geo_infer_place.core.api_clients import CaliforniaAPIManager
except ImportError as e:
    print(f"Warning: Could not import some components: {e}")
    print("Running with simplified functionality only.")
    LocationConfigLoader = CaliforniaDataSources = CaliforniaAPIManager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('del_norte_demo.log')
    ]
)

logger = logging.getLogger(__name__)

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
    
    if CaliforniaAPIManager is None:
        logger.warning("CaliforniaAPIManager not available - using mock demonstration")
        logger.info("Mock API connections would test:")
        logger.info("  ✓ CAL FIRE API: Fire perimeter data (Mock: 150ms)")
        logger.info("  ✓ NOAA API: Weather data (Mock: 250ms)")
        logger.info("  ✓ USGS API: Water/seismic data (Mock: 180ms)")
        logger.info("  ✓ CDEC API: Environmental monitoring (Mock: 300ms)")
        return {'mock': True, 'connections': 4}
    
    api_manager = CaliforniaAPIManager(api_keys)
    
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
            h3_cell = h3.geo_to_h3(center_lat, center_lon, resolution)
        
        try:
            cell_area = h3.cell_area(h3_cell, unit='km^2')
        except:
            cell_area = h3.hex_area(resolution, unit='km^2')
        
        # Get neighboring cells
        try:
            neighbors = h3.grid_ring(h3_cell, 1)
        except AttributeError:
            neighbors = h3.hex_ring(h3_cell, 1)
        
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
                cell = h3.geo_to_h3(lat, lon, 8)
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
                h3_boundary = h3.cell_to_boundary(h3_cell, geo_json=True)
            except AttributeError:
                h3_cell = h3.geo_to_h3(lat, lon, 8)
                h3_boundary = h3.h3_to_geo_boundary(h3_cell, geo_json=True)
            
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
        <h3 align="center" style="font-size:20px"><b>Del Norte County Demo Map</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        map_path = output_path / f"del_norte_demo_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        m.save(str(map_path))
        
        logger.info(f"Demo map saved: {map_path}")
        
        # Open in browser
        import webbrowser
        webbrowser.open(f'file://{map_path.absolute()}')
        
        logger.info("Demo map opened in browser")
        
        return {
            'success': True,
            'map_path': str(map_path),
            'message': 'Simplified demo completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Simplified demo failed: {e}")
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
    
    # Run comprehensive demo
    logger.info("Running comprehensive dashboard demonstration...")
    result = run_comprehensive_demo(
        config_path=args.config,
        output_dir=args.output,
        api_keys=api_keys
    )
    
    if result.get('success', False):
        logger.info("=== DEMO COMPLETED SUCCESSFULLY ===")
        logger.info("Generated Files:")
        
        # Handle different result types (simplified vs comprehensive)
        if 'map_path' in result:
            logger.info(f"  📊 Interactive Dashboard: {result['map_path']}")
        elif 'dashboard_path' in result:
            logger.info(f"  📊 Interactive Dashboard: {result['dashboard_path']}")
        
        if 'results_path' in result:
            logger.info(f"  📄 Analysis Results: {result['results_path']}")
            
        if 'summary_path' in result:
            logger.info(f"  📋 Summary Report: {result['summary_path']}")
            
        if 'message' in result:
            logger.info(f"  💬 Status: {result['message']}")
            
        logger.info("")
        logger.info("Next Steps:")
        logger.info("1. Open the interactive dashboard in a web browser")
        if 'results_path' in result:
            logger.info("2. Review the analysis results JSON file")
        if 'summary_path' in result:
            logger.info("3. Read the summary report for key findings")
        logger.info("4. Customize the configuration for your specific needs")
        
        # Print the summary report if available
        if 'summary_path' in result:
            logger.info("=== SUMMARY REPORT ===")
            try:
                with open(result['summary_path'], 'r') as f:
                    summary_content = f.read()
                print(summary_content)
            except Exception as e:
                logger.warning(f"Could not display summary report: {e}")
                
    else:
        logger.error("=== DEMO FAILED ===")
        logger.error(f"Error: {result.get('error', 'Unknown error')}")
        logger.error("Check the logs above for detailed error information.")
        sys.exit(1)

if __name__ == "__main__":
    main() 