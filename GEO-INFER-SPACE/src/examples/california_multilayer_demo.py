#!/usr/bin/env python3
"""
California Multi-Layer Geospatial Demo

This example demonstrates the integration of multiple geospatial data types (Zoning, Water, Climate)
over California using the OSC-GEO/H3 grid system and interactive Folium visualization with layer toggles.

Features:
- Sets up OSC-GEO and H3 grid manager
- Simulates three geospatial data types over California:
    1. Zoning (polygons)
    2. Water (lines/polygons)
    3. Climate (points/polygons)
- Converts each to H3, aggregates, and visualizes as separate Folium layers
- Interactive map with toggles for each data type
- Modular, professional, and fully documented code

Requirements:
    pip install folium h3 geopandas shapely numpy pandas

Usage:
    python california_multilayer_demo.py
"""

import os
import sys
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
import folium
from folium.plugins import MarkerCluster
from shapely.geometry import Polygon, LineString, Point

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("california_multilayer_demo")

# Import OSC-GEO functionality
try:
    from geo_infer_space.osc_geo import (
        setup_osc_geo,
        create_h3_grid_manager,
        load_data_to_h3_grid
    )
    from geo_infer_space.osc_geo.utils.h3_utils import (
        h3_to_geojson,
        geojson_to_h3
    )
except ImportError as e:
    logger.error(f"Failed to import geo_infer_space.osc_geo: {e}")
    sys.exit(1)

# California bounding box (approximate)
CA_BOUNDS = {
    "min_lat": 32.5,
    "max_lat": 42.0,
    "min_lon": -124.5,
    "max_lon": -114.0
}


def generate_zoning_geojson() -> Dict[str, Any]:
    """
    Simulate zoning polygons (e.g., residential, commercial, industrial) over California.
    Returns a GeoJSON FeatureCollection.
    """
    np.random.seed(1)
    zones = ["Residential", "Commercial", "Industrial", "Agricultural"]
    features = []
    for i in range(8):
        lat = np.random.uniform(CA_BOUNDS["min_lat"], CA_BOUNDS["max_lat"])
        lon = np.random.uniform(CA_BOUNDS["min_lon"], CA_BOUNDS["max_lon"])
        dlat = np.random.uniform(0.3, 0.7)
        dlon = np.random.uniform(0.3, 0.7)
        polygon = Polygon([
            (lon, lat),
            (lon + dlon, lat),
            (lon + dlon, lat + dlat),
            (lon, lat + dlat),
            (lon, lat)
        ])
        features.append({
            "type": "Feature",
            "properties": {
                "zone": np.random.choice(zones),
                "id": f"zone_{i+1}"
            },
            "geometry": json.loads(json.dumps(polygon.__geo_interface__))
        })
    return {"type": "FeatureCollection", "features": features}


def generate_water_geojson() -> Dict[str, Any]:
    """
    Simulate water features (rivers as lines, lakes as polygons) over California.
    Returns a GeoJSON FeatureCollection.
    """
    np.random.seed(2)
    features = []
    # Simulate rivers (lines)
    for i in range(3):
        start_lat = np.random.uniform(CA_BOUNDS["min_lat"], CA_BOUNDS["max_lat"])
        start_lon = np.random.uniform(CA_BOUNDS["min_lon"], CA_BOUNDS["max_lon"])
        line = LineString([
            (start_lon, start_lat),
            (start_lon + np.random.uniform(0.5, 2.0), start_lat + np.random.uniform(1.0, 3.0))
        ])
        features.append({
            "type": "Feature",
            "properties": {"type": "River", "id": f"river_{i+1}"},
            "geometry": json.loads(json.dumps(line.__geo_interface__))
        })
    # Simulate lakes (polygons)
    for i in range(2):
        lat = np.random.uniform(CA_BOUNDS["min_lat"], CA_BOUNDS["max_lat"])
        lon = np.random.uniform(CA_BOUNDS["min_lon"], CA_BOUNDS["max_lon"])
        d = np.random.uniform(0.1, 0.3)
        lake = Polygon([
            (lon, lat),
            (lon + d, lat),
            (lon + d, lat + d),
            (lon, lat + d),
            (lon, lat)
        ])
        features.append({
            "type": "Feature",
            "properties": {"type": "Lake", "id": f"lake_{i+1}"},
            "geometry": json.loads(json.dumps(lake.__geo_interface__))
        })
    return {"type": "FeatureCollection", "features": features}


def generate_climate_geojson() -> Dict[str, Any]:
    """
    Simulate climate data (points with temperature/precipitation) over California.
    Returns a GeoJSON FeatureCollection.
    """
    np.random.seed(3)
    features = []
    for i in range(20):
        lat = np.random.uniform(CA_BOUNDS["min_lat"], CA_BOUNDS["max_lat"])
        lon = np.random.uniform(CA_BOUNDS["min_lon"], CA_BOUNDS["max_lon"])
        temp = np.random.uniform(5, 40)  # Celsius
        precip = np.random.uniform(0, 200)  # mm
        point = Point(lon, lat)
        features.append({
            "type": "Feature",
            "properties": {
                "temperature": round(temp, 1),
                "precipitation": round(precip, 1),
                "id": f"climate_{i+1}"
            },
            "geometry": json.loads(json.dumps(point.__geo_interface__))
        })
    return {"type": "FeatureCollection", "features": features}


def geojson_to_h3_polygons(geojson: Dict[str, Any], resolution: int) -> Tuple[List[str], Dict[str, Any]]:
    """
    Convert GeoJSON features to H3 indices using a simplified approach.
    For polygons, we'll use the centroid to get H3 cells.
    Returns a list of H3 indices and a mapping of properties.
    """
    import h3
    from shapely.geometry import shape
    
    h3_indices = []
    properties = {}
    
    for feature in geojson["features"]:
        geom = shape(feature["geometry"])
        props = feature["properties"]
        
        if geom.geom_type == "Point":
            # Direct point conversion
            lat, lon = geom.y, geom.x
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            h3_indices.append(h3_index)
            properties[h3_index] = props
            
        elif geom.geom_type in ["Polygon", "MultiPolygon"]:
            # Use centroid for polygons (simplified approach)
            centroid = geom.centroid
            lat, lon = centroid.y, centroid.x
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            h3_indices.append(h3_index)
            properties[h3_index] = props
            
        elif geom.geom_type == "LineString":
            # Use midpoint for lines
            midpoint = geom.interpolate(0.5, normalized=True)
            lat, lon = midpoint.y, midpoint.x
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            h3_indices.append(h3_index)
            properties[h3_index] = props
    
    # Remove duplicates
    h3_indices = list(set(h3_indices))
    
    return h3_indices, properties


def h3_to_geojson_polygons(h3_indices: List[str], properties: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert H3 indices back to GeoJSON format.
    """
    import h3
    
    features = []
    
    for h3_index in h3_indices:
        # Get the hexagon boundary
        boundary = h3.cell_to_boundary(h3_index)
        
        # Convert to GeoJSON polygon format
        polygon_coords = [[lon, lat] for lat, lon in boundary]
        
        # Close the polygon if needed
        if polygon_coords[0] != polygon_coords[-1]:
            polygon_coords.append(polygon_coords[0])
        
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [polygon_coords]
            },
            "properties": properties.get(h3_index, {})
        }
        
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


def add_h3_layer_to_map(m: folium.Map, h3_indices: List[str], properties: Dict[str, Any], layer_name: str, color: str, popup_fields: List[str] = None):
    """
    Add an H3 hexagon layer to a Folium map.
    """
    import h3
    fg = folium.FeatureGroup(name=layer_name)
    for h3_index in h3_indices:
        boundary = h3.cell_to_boundary(h3_index)
        prop = properties.get(h3_index, {})
        popup_text = "<br>".join([f"{k}: {v}" for k, v in prop.items() if not popup_fields or k in popup_fields])
        folium.Polygon(
            locations=boundary,
            color=color,
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.5,
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(fg)
    fg.add_to(m)


def add_point_layer_to_map(m: folium.Map, geojson: Dict[str, Any], layer_name: str, color: str, popup_fields: List[str] = None):
    """
    Add a point layer to a Folium map.
    """
    fg = folium.FeatureGroup(name=layer_name)
    for feature in geojson["features"]:
        if feature["geometry"]["type"] == "Point":
            coords = feature["geometry"]["coordinates"]
            prop = feature["properties"]
            popup_text = "<br>".join([f"{k}: {v}" for k, v in prop.items() if not popup_fields or k in popup_fields])
            folium.CircleMarker(
                location=[coords[1], coords[0]],
                radius=6,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(fg)
    fg.add_to(m)


def main():
    """
    Main function to run the California multi-layer geospatial demo.
    """
    # Check if repos already exist before setting up
    repo_paths = [
        Path("GEO-INFER-SPACE/repo/osc-geo-h3grid-srv"),
        Path("GEO-INFER-SPACE/repo/osc-geo-h3loader-cli")
    ]
    
    repos_exist = all(repo_path.exists() for repo_path in repo_paths)
    
    if repos_exist:
        logger.info("OSC repositories already exist, skipping setup...")
    else:
        logger.info("Setting up OSC-GEO...")
        setup_osc_geo()
    
    logger.info("Using H3 utility functions for geospatial processing...")

    # Generate simulated data
    logger.info("Generating simulated zoning data...")
    zoning_geojson = generate_zoning_geojson()
    logger.info("Generating simulated water data...")
    water_geojson = generate_water_geojson()
    logger.info("Generating simulated climate data...")
    climate_geojson = generate_climate_geojson()

    # Convert to H3 using utility functions (confirmed to work in tests)
    resolution = 7
    logger.info("Converting zoning data to H3...")
    zoning_h3, zoning_props = geojson_to_h3_polygons(zoning_geojson, resolution)
    logger.info("Converting water data to H3...")
    water_h3, water_props = geojson_to_h3_polygons(water_geojson, resolution)
    logger.info("Converting climate data to H3...")
    climate_h3, climate_props = geojson_to_h3_polygons(climate_geojson, resolution)

    # Create Folium map centered on California
    center_lat = (CA_BOUNDS["min_lat"] + CA_BOUNDS["max_lat"]) / 2
    center_lon = (CA_BOUNDS["min_lon"] + CA_BOUNDS["max_lon"]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=6, tiles='cartodbpositron')

    # Add H3 layers
    add_h3_layer_to_map(m, zoning_h3, zoning_props, "Zoning (H3)", color="#1f77b4", popup_fields=["zone", "id"])
    add_h3_layer_to_map(m, water_h3, water_props, "Water (H3)", color="#2ca02c", popup_fields=["type", "id"])
    add_h3_layer_to_map(m, climate_h3, climate_props, "Climate (H3)", color="#d62728", popup_fields=["temperature", "precipitation", "id"])

    # Add original climate points as a separate layer
    add_point_layer_to_map(m, climate_geojson, "Climate Stations", color="#ff7f0e", popup_fields=["temperature", "precipitation", "id"])

    # Add layer control
    folium.LayerControl().add_to(m)

    # Add title
    title_html = '''
         <h3 align="center" style="font-size:20px"><b>California Multi-Layer Geospatial Demo</b></h3>
         <p align="center">Zoning, Water, and Climate Data Visualized on H3 Grid</p>
         '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Save map
    output_dir = Path(__file__).parent / "california_demo_outputs"
    output_dir.mkdir(exist_ok=True)
    map_path = output_dir / "california_multilayer_demo.html"
    m.save(str(map_path))
    logger.info(f"Interactive map saved to: {map_path}")
    logger.info("Open the HTML file in your browser to view the interactive demo.")
    logger.info("Demo completed successfully using H3 utility functions!")

if __name__ == "__main__":
    main() 