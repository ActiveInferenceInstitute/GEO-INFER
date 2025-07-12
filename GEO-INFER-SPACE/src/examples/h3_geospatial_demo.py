#!/usr/bin/env python3
"""
H3 Geospatial Overlay Demonstration Script

This script demonstrates interactive H3-based geospatial overlays using the OSC
(OS Climate) repositories integrated with GEO-INFER-SPACE. It:

1. Uses osc-geo-h3grid-srv for H3 grid operations (fork from docxology)
2. Uses osc-geo-h3loader-cli for data loading  (fork from docxology)
3. Generates interactive visualizations with Folium
4. Creates sample geospatial datasets for demonstration
5. Spins up a web server to display results

Usage:
    python h3_geospatial_demo.py [--port 8080] [--resolution 8] [--samples 1000]
"""

import sys
import os
import json
import logging
import argparse
import webbrowser
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir.resolve()))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("h3_geospatial_demo")

# Import our modules
try:
    from geo_infer_space.osc_geo.utils.h3_utils import h3_to_geojson, geojson_to_h3
    from geo_infer_space.osc_geo.utils.visualization import OSCVisualizationEngine
    from geo_infer_space.osc_geo.utils.osc_simple_status import check_repo_status
except ImportError as e:
    logger.error(f"Error importing GEO-INFER modules: {e}")
    sys.exit(1)

# Try to import optional dependencies
try:
    import h3
    import folium
    import numpy as np
    import pandas as pd
    import geopandas as gpd
    from folium.plugins import MarkerCluster, HeatMap
    from shapely.geometry import Point, Polygon
    HAS_GEO_DEPS = True
except ImportError as e:
    logger.error(f"Missing geospatial dependencies: {e}")
    logger.error("Please install: pip install folium h3 geopandas shapely")
    HAS_GEO_DEPS = False


class H3GeospatialDemo:
    """
    Comprehensive H3 geospatial overlay demonstration using OSC repositories.
    """
    
    def __init__(self, output_dir: str = "demo_outputs", h3_resolution: int = 8):
        """
        Initialize the H3 Geospatial Demo.
        
        Args:
            output_dir: Directory for saving demo outputs
            h3_resolution: H3 grid resolution (0-15)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.h3_resolution = h3_resolution
        
        # Create subdirectories
        (self.output_dir / "data").mkdir(exist_ok=True)
        (self.output_dir / "maps").mkdir(exist_ok=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        
        # Initialize visualization engine
        self.viz_engine = OSCVisualizationEngine(self.output_dir / "visualizations")
        
        logger.info(f"H3 Geospatial Demo initialized with output directory: {self.output_dir}")
        logger.info(f"H3 Resolution: {h3_resolution}")
    
    def check_osc_repositories(self) -> Dict[str, Any]:
        """Check the status of OSC repositories."""
        logger.info("🔍 Checking OSC repository status...")
        
        try:
            status = check_repo_status()
            logger.info("✅ OSC repository status check completed")
            return status
        except Exception as e:
            logger.error(f"❌ Error checking OSC repositories: {e}")
            return {"error": str(e)}
    
    def generate_sample_geospatial_data(self, 
                                      center: Tuple[float, float] = (40.7128, -74.0060),
                                      num_samples: int = 1000,
                                      radius_km: float = 50) -> Dict[str, Any]:
        """
        Generate sample geospatial data for demonstration.
        
        Args:
            center: Center coordinates (lat, lon) - defaults to NYC
            num_samples: Number of sample points to generate
            radius_km: Radius in kilometers for sample distribution
            
        Returns:
            Dictionary containing sample data and metadata
        """
        logger.info(f"🌍 Generating {num_samples} sample geospatial points around {center}")
        
        if not HAS_GEO_DEPS:
            logger.error("❌ Geospatial dependencies not available")
            return {}
        
        # Generate random points within radius
        np.random.seed(42)  # For reproducible results
        
        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.0  # 1 degree ≈ 111 km
        
        # Generate random points in a circle
        angles = np.random.uniform(0, 2*np.pi, num_samples)
        distances = np.random.uniform(0, radius_deg, num_samples)
        
        # Convert to lat/lon
        lats = center[0] + distances * np.cos(angles)
        lons = center[1] + distances * np.sin(angles)
        
        # Create sample data with various properties
        data = {
            "points": [],
            "properties": {}
        }
        
        for i, (lat, lon) in enumerate(zip(lats, lons)):
            point_id = f"point_{i:04d}"
            
            # Generate sample properties
            temperature = np.random.normal(20, 10)  # Temperature in Celsius
            humidity = np.random.uniform(30, 90)    # Humidity percentage
            elevation = np.random.exponential(50)   # Elevation in meters
            population = np.random.poisson(1000)    # Population density
            
            data["points"].append({
                "id": point_id,
                "lat": float(lat),
                "lon": float(lon),
                "properties": {
                    "temperature": round(temperature, 2),
                    "humidity": round(humidity, 2),
                    "elevation": round(elevation, 2),
                    "population": int(population)
                }
            })
        
        # Add metadata
        data["metadata"] = {
            "center": center,
            "num_samples": num_samples,
            "radius_km": radius_km,
            "generated_at": datetime.now().isoformat(),
            "h3_resolution": self.h3_resolution
        }
        
        logger.info(f"✅ Generated {len(data['points'])} sample points")
        return data
    
    def convert_points_to_h3(self, sample_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert sample points to H3 cells using the h3_utils module.
        
        Args:
            sample_data: Sample geospatial data from generate_sample_geospatial_data
            
        Returns:
            Dictionary containing H3 cells and aggregated data
        """
        logger.info(f"🔷 Converting points to H3 cells at resolution {self.h3_resolution}")
        
        if not HAS_GEO_DEPS or not sample_data:
            logger.error("❌ Cannot convert points - missing dependencies or data")
            return {}
        
        h3_data = {
            "h3_cells": {},
            "aggregated_data": {},
            "statistics": {}
        }
        
        # Group points by H3 cell
        for point in sample_data["points"]:
            lat, lon = point["lat"], point["lon"]
            
            # Convert to H3 cell
            h3_cell = h3.latlng_to_cell(lat, lon, self.h3_resolution)
            
            if h3_cell not in h3_data["h3_cells"]:
                center_coords = h3.cell_to_latlng(h3_cell)
                boundary_coords = h3.cell_to_boundary(h3_cell)
                h3_data["h3_cells"][h3_cell] = {
                    "points": [],
                    "count": 0,
                    "center": center_coords,
                    "boundary": boundary_coords
                }
            
            h3_data["h3_cells"][h3_cell]["points"].append(point)
            h3_data["h3_cells"][h3_cell]["count"] += 1
        
        # Aggregate data by H3 cell
        for h3_cell, cell_data in h3_data["h3_cells"].items():
            points = cell_data["points"]
            
            if not points:
                continue
            
            # Calculate aggregated statistics
            temperatures = [p["properties"]["temperature"] for p in points]
            humidities = [p["properties"]["humidity"] for p in points]
            elevations = [p["properties"]["elevation"] for p in points]
            populations = [p["properties"]["population"] for p in points]
            
            h3_data["aggregated_data"][h3_cell] = {
                "point_count": len(points),
                "avg_temperature": round(np.mean(temperatures), 2),
                "avg_humidity": round(np.mean(humidities), 2),
                "avg_elevation": round(np.mean(elevations), 2),
                "total_population": int(np.sum(populations)),
                "temperature_std": round(np.std(temperatures), 2),
                "density_score": len(points) / h3.cell_area(h3_cell, unit='km^2')
            }
        
        # Calculate overall statistics
        all_cells = list(h3_data["h3_cells"].keys())
        cell_counts = [data["count"] for data in h3_data["h3_cells"].values()]
        
        h3_data["statistics"] = {
            "total_h3_cells": len(all_cells),
            "total_points": sum(cell_counts),
            "avg_points_per_cell": round(np.mean(cell_counts), 2) if cell_counts else 0,
            "max_points_per_cell": max(cell_counts) if cell_counts else 0,
            "min_points_per_cell": min(cell_counts) if cell_counts else 0,
            "h3_resolution": self.h3_resolution,
            "cell_area_km2": 0.737327598  # Approximate area for H3 res 8 in km^2
        }
        
        logger.info(f"✅ Converted to {len(all_cells)} H3 cells")
        logger.info(f"📊 Average points per cell: {h3_data['statistics']['avg_points_per_cell']}")
        
        return h3_data
    
    def create_interactive_h3_map(self, 
                                 h3_data: Dict[str, Any],
                                 sample_data: Dict[str, Any]) -> str:
        """
        Create an interactive Folium map with H3 overlays.
        
        Args:
            h3_data: H3 cell data from convert_points_to_h3
            sample_data: Original sample data
            
        Returns:
            Path to the generated HTML map file
        """
        logger.info("🗺️  Creating interactive H3 overlay map...")
        
        if not HAS_GEO_DEPS or not h3_data:
            logger.error("❌ Cannot create map - missing dependencies or data")
            return ""
        
        # Get center from metadata or use default
        center = sample_data.get("metadata", {}).get("center", [40.7128, -74.0060])
        
        # Create base map
        m = folium.Map(
            location=center,
            zoom_start=10,
            tiles='OpenStreetMap'
        )
        
        # Add tile layers
        folium.TileLayer('cartodbpositron', name='CartoDB Positron').add_to(m)
        
        # Color schemes for different metrics
        import folium.plugins as plugins
        from folium import plugins as folium_plugins
        
        # Simple color mapping functions
        def get_temp_color(temp, min_temp, max_temp):
            normalized = (temp - min_temp) / (max_temp - min_temp) if max_temp != min_temp else 0
            # Blue to Red gradient
            if normalized < 0.5:
                return f"rgb({int(255*normalized*2)}, {int(255*normalized*2)}, 255)"
            else:
                return f"rgb(255, {int(255*(2-normalized*2))}, {int(255*(2-normalized*2))})"
        
        def get_density_color(density, min_density, max_density):
            normalized = (density - min_density) / (max_density - min_density) if max_density != min_density else 0
            # Yellow to Red gradient  
            return f"rgb(255, {int(255*(1-normalized))}, 0)"
        
        # Get value ranges
        temp_values = [data["avg_temperature"] for data in h3_data["aggregated_data"].values()]
        density_values = [data["density_score"] for data in h3_data["aggregated_data"].values()]
        
        min_temp, max_temp = min(temp_values), max(temp_values)
        min_density, max_density = min(density_values), max(density_values)
        
        # Create feature groups for different overlays
        h3_temp_group = folium.FeatureGroup(name="H3 - Temperature")
        h3_density_group = folium.FeatureGroup(name="H3 - Density")
        points_group = folium.FeatureGroup(name="Sample Points")
        
        # Add H3 cells with temperature coloring
        for h3_cell, agg_data in h3_data["aggregated_data"].items():
            cell_boundary = h3_data["h3_cells"][h3_cell]["boundary"]
            
            # Create polygon for H3 cell
            polygon_coords = [[lat, lon] for lon, lat in cell_boundary]
            
            # Temperature-based coloring
            temp_color = get_temp_color(agg_data["avg_temperature"], min_temp, max_temp)
            
            folium.Polygon(
                locations=polygon_coords,
                color='black',
                weight=1,
                fillColor=temp_color,
                fillOpacity=0.7,
                popup=folium.Popup(
                    f"""
                    <b>H3 Cell:</b> {h3_cell}<br>
                    <b>Points:</b> {agg_data['point_count']}<br>
                    <b>Avg Temperature:</b> {agg_data['avg_temperature']}°C<br>
                    <b>Avg Humidity:</b> {agg_data['avg_humidity']}%<br>
                    <b>Avg Elevation:</b> {agg_data['avg_elevation']}m<br>
                    <b>Population:</b> {agg_data['total_population']}<br>
                    <b>Density Score:</b> {agg_data['density_score']:.2f}
                    """,
                    max_width=300
                ),
                tooltip=f"H3: {h3_cell[:8]}... | Temp: {agg_data['avg_temperature']}°C"
            ).add_to(h3_temp_group)
        
        # Add H3 cells with density coloring
        for h3_cell, agg_data in h3_data["aggregated_data"].items():
            cell_boundary = h3_data["h3_cells"][h3_cell]["boundary"]
            
            # Create polygon for H3 cell
            polygon_coords = [[lat, lon] for lon, lat in cell_boundary]
            
            # Density-based coloring
            density_color = get_density_color(agg_data["density_score"], min_density, max_density)
            
            folium.Polygon(
                locations=polygon_coords,
                color='black',
                weight=1,
                fillColor=density_color,
                fillOpacity=0.7,
                popup=folium.Popup(
                    f"""
                    <b>H3 Cell:</b> {h3_cell}<br>
                    <b>Points:</b> {agg_data['point_count']}<br>
                    <b>Density Score:</b> {agg_data['density_score']:.2f}<br>
                    <b>Cell Area:</b> {h3.cell_area(h3_cell, unit='km^2'):.2f} km²<br>
                    <b>Population Density:</b> {agg_data['total_population']/h3.cell_area(h3_cell, unit='km^2'):.0f}/km²
                    """,
                    max_width=300
                ),
                tooltip=f"H3: {h3_cell[:8]}... | Density: {agg_data['density_score']:.2f}"
            ).add_to(h3_density_group)
        
        # Add sample points
        marker_cluster = MarkerCluster().add_to(points_group)
        
        for point in sample_data["points"][:100]:  # Limit to first 100 for performance
            folium.Marker(
                [point["lat"], point["lon"]],
                popup=folium.Popup(
                    f"""
                    <b>Point ID:</b> {point['id']}<br>
                    <b>Location:</b> {point['lat']:.4f}, {point['lon']:.4f}<br>
                    <b>Temperature:</b> {point['properties']['temperature']}°C<br>
                    <b>Humidity:</b> {point['properties']['humidity']}%<br>
                    <b>Elevation:</b> {point['properties']['elevation']}m<br>
                    <b>Population:</b> {point['properties']['population']}
                    """,
                    max_width=250
                ),
                tooltip=f"Point: {point['id']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(marker_cluster)
        
        # Add feature groups to map
        h3_temp_group.add_to(m)
        h3_density_group.add_to(m)
        points_group.add_to(m)
        
        # Add legend (simplified for now)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Add title
        title_html = '''
                     <h3 align="center" style="font-size:20px"><b>H3 Geospatial Overlay Demo</b></h3>
                     <p align="center">Interactive H3 hexagonal grid overlays with sample geospatial data</p>
                     '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        map_path = self.output_dir / "maps" / f"h3_overlay_demo_{timestamp}.html"
        m.save(str(map_path))
        
        logger.info(f"✅ Interactive map saved to: {map_path}")
        return str(map_path)
    
    def run_full_demo(self, 
                     center: Tuple[float, float] = (40.7128, -74.0060),
                     num_samples: int = 1000,
                     open_browser: bool = True) -> Dict[str, Any]:
        """
        Run the complete H3 geospatial overlay demonstration.
        
        Args:
            center: Center coordinates for sample data generation
            num_samples: Number of sample points to generate
            open_browser: Whether to open the results in a web browser
            
        Returns:
            Dictionary containing all generated outputs and paths
        """
        logger.info("🚀 Starting H3 Geospatial Overlay Demo")
        logger.info("=" * 60)
        
        demo_results = {
            "timestamp": datetime.now().isoformat(),
            "parameters": {
                "center": center,
                "num_samples": num_samples,
                "h3_resolution": self.h3_resolution
            }
        }
        
        # Step 1: Check OSC repositories
        logger.info("Step 1: Checking OSC repositories...")
        osc_status = self.check_osc_repositories()
        demo_results["osc_status"] = osc_status
        
        # Step 2: Generate sample data
        logger.info("Step 2: Generating sample geospatial data...")
        sample_data = self.generate_sample_geospatial_data(center, num_samples)
        demo_results["sample_data_summary"] = {
            "points_generated": len(sample_data.get("points", [])),
            "center": center,
            "num_samples": num_samples
        }
        
        # Step 3: Convert to H3
        logger.info("Step 3: Converting points to H3 cells...")
        h3_data = self.convert_points_to_h3(sample_data)
        demo_results["h3_conversion"] = h3_data.get("statistics", {})
        
        # Step 4: Create interactive map
        logger.info("Step 4: Creating interactive H3 overlay map...")
        map_path = self.create_interactive_h3_map(h3_data, sample_data)
        demo_results["map_path"] = map_path
        
        # Summary
        logger.info("=" * 60)
        logger.info("🎉 H3 Geospatial Overlay Demo Complete!")
        logger.info(f"📁 Output directory: {self.output_dir}")
        logger.info(f"🌍 Interactive map: {map_path}")
        
        # Open in browser if requested
        if open_browser and map_path:
            logger.info("🌐 Opening map in web browser...")
            webbrowser.open(f"file://{Path(map_path).absolute()}")
        
        return demo_results


class SimpleWebServer:
    """Simple web server for serving demo files."""
    
    def __init__(self, directory: str, port: int = 8080):
        self.directory = Path(directory)
        self.port = port
        self.httpd = None
        
    def start_server(self):
        """Start the web server in a separate thread."""
        os.chdir(self.directory)
        
        handler = SimpleHTTPRequestHandler
        self.httpd = HTTPServer(("", self.port), handler)
        
        def serve_forever():
            logger.info(f"🌐 Starting web server at http://localhost:{self.port}")
            logger.info(f"📁 Serving files from: {self.directory}")
            self.httpd.serve_forever()
        
        server_thread = threading.Thread(target=serve_forever, daemon=True)
        server_thread.start()
        
        return f"http://localhost:{self.port}"
    
    def stop_server(self):
        """Stop the web server."""
        if self.httpd:
            self.httpd.shutdown()
            logger.info("🛑 Web server stopped")


def main():
    """Main function for the H3 geospatial demo."""
    parser = argparse.ArgumentParser(
        description="H3 Geospatial Overlay Demonstration using OSC repositories"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="Port for web server (default: 8080)"
    )
    parser.add_argument(
        "--resolution", 
        type=int, 
        default=8,
        help="H3 resolution level 0-15 (default: 8)"
    )
    parser.add_argument(
        "--samples", 
        type=int, 
        default=1000,
        help="Number of sample points to generate (default: 1000)"
    )
    parser.add_argument(
        "--center", 
        nargs=2, 
        type=float,
        default=[40.7128, -74.0060],
        help="Center coordinates [lat lon] (default: NYC)"
    )
    parser.add_argument(
        "--no-browser", 
        action="store_true",
        help="Don't open browser automatically"
    )
    parser.add_argument(
        "--serve", 
        action="store_true",
        help="Start web server to serve files"
    )
    
    args = parser.parse_args()
    
    if not HAS_GEO_DEPS:
        logger.error("❌ Missing required geospatial dependencies")
        logger.error("Please install: pip install folium h3 geopandas shapely matplotlib seaborn")
        return False
    
    # Initialize demo
    demo = H3GeospatialDemo(h3_resolution=args.resolution)
    
    # Run full demonstration
    results = demo.run_full_demo(
        center=tuple(args.center),
        num_samples=args.samples,
        open_browser=not args.no_browser
    )
    
    # Start web server if requested
    if args.serve:
        server = SimpleWebServer(demo.output_dir, args.port)
        server_url = server.start_server()
        
        logger.info(f"🌐 Demo available at: {server_url}")
        logger.info("📄 Access the dashboard and interactive maps through the web interface")
        logger.info("⌨️  Press Ctrl+C to stop the server")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down web server...")
            server.stop_server()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)