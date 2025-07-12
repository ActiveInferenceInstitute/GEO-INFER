"""
H3 utility functions for OSC-GEO.

This module provides utility functions for working with H3 grid data.
"""

import logging
import json
from typing import Dict, List, Union, Any, Optional

logger = logging.getLogger(__name__)

def h3_to_geojson(
    h3_indices: List[str],
    properties: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Convert H3 indices to GeoJSON format.

    Args:
        h3_indices: List of H3 indices.
        properties: Optional dictionary mapping H3 indices to feature properties.

    Returns:
        GeoJSON FeatureCollection.
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for h3_to_geojson")

    features = []

    for h3_index in h3_indices:
        # Get the hexagon boundary as a GeoJSON polygon
        boundary = list(h3.cell_to_boundary(h3_index))

        # Add closing point to the polygon if needed
        if boundary[0] != boundary[-1]:
            boundary.append(boundary[0])

        # Create the polygon geometry
        polygon_geometry = {
            "type": "Polygon",
            "coordinates": [boundary]
        }

        # Get properties for this H3 index
        feature_properties = properties.get(h3_index, {}) if properties else {}
        feature_properties["h3_index"] = h3_index

        # Create the feature
        feature = {
            "type": "Feature",
            "geometry": polygon_geometry,
            "properties": feature_properties
        }

        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features
    }

def geojson_to_h3(
    geojson_data: Union[str, Dict[str, Any]],
    resolution: int = 8,
    feature_properties: bool = True
) -> Dict[str, Union[List[str], Dict[str, Dict[str, Any]]]]:
    """
    Convert GeoJSON to H3 indices.
    
    Args:
        geojson_data: GeoJSON data as a string or dictionary.
        resolution: H3 resolution (0-15).
        feature_properties: Whether to include feature properties in the result.
            
    Returns:
        Dictionary with H3 indices and properties.
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for geojson_to_h3")
    
    # Parse GeoJSON if it's a string
    if isinstance(geojson_data, str):
        geojson_data = json.loads(geojson_data)
    
    # Get features from GeoJSON
    if "type" in geojson_data and geojson_data["type"] == "FeatureCollection":
        features = geojson_data.get("features", [])
    elif "type" in geojson_data and geojson_data["type"] == "Feature":
        features = [geojson_data]
    else:
        features = []
    
    # Initialize result
    result = {
        "h3_indices": [],
        "properties": {}
    }
    
    for feature in features:
        geometry = feature.get("geometry", {})
        geometry_type = geometry.get("type", "")
        coordinates = geometry.get("coordinates", [])
        properties = feature.get("properties", {})
        
        h3_indices = []
        
        if geometry_type == "Point":
            # Convert point to H3
            lat, lng = coordinates[1], coordinates[0]
            h3_index = h3.latlng_to_cell(lat, lng, resolution)
            h3_indices.append(h3_index)
            
        elif geometry_type == "Polygon":
            # Convert polygon to H3
            if coordinates:
                # Assuming first ring is exterior, rest are holes
                exterior = coordinates[0]
                h3_indices = h3.polyfill(
                    {"type": "Polygon", "coordinates": [exterior]},
                    resolution,
                    geo_json_conformant=True # Use geo_json_conformant for lng/lat
                )
        
        elif geometry_type == "MultiPolygon":
            # Convert each polygon to H3
            for polygon in coordinates:
                # Assuming first ring is exterior, rest are holes
                exterior = polygon[0]
                indices = h3.polyfill(
                    {"type": "Polygon", "coordinates": [exterior]},
                    resolution,
                    geo_json_conformant=True # Use geo_json_conformant for lng/lat
                )
                h3_indices.extend(indices)
        
        # Add H3 indices to result
        result["h3_indices"].extend(h3_indices)
        
        # Add properties if requested
        if feature_properties and properties:
            for h3_index in h3_indices:
                result["properties"][h3_index] = properties
    
    # Remove duplicates
    result["h3_indices"] = list(set(result["h3_indices"]))
    
    return result 