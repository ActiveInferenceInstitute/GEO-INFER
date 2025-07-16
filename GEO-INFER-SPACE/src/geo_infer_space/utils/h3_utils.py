"""
H3 utility functions for OSC-GEO.

This module provides utility functions for working with H3 grid data.
All functions use H3 4.x API directly.
"""

import logging
import json
from typing import Dict, List, Union, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def latlng_to_cell(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude to H3 cell index.
    
    Args:
        lat: Latitude in degrees
        lng: Longitude in degrees  
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 cell index as string
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for latlng_to_cell")
    
    return h3.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(h3_index: str) -> Tuple[float, float]:
    """
    Convert H3 cell index to latitude/longitude center point.
    
    Args:
        h3_index: H3 cell index as string
        
    Returns:
        Tuple of (latitude, longitude) in degrees
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for cell_to_latlng")
    
    return h3.cell_to_latlng(h3_index)


def cell_to_latlng_boundary(h3_index: str) -> List[Tuple[float, float]]:
    """
    Convert H3 cell index to boundary coordinates.
    
    Args:
        h3_index: H3 cell index as string
        
    Returns:
        List of (latitude, longitude) tuples forming the hexagon boundary
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for cell_to_latlng_boundary")
    
    return h3.cell_to_boundary(h3_index)


def polygon_to_cells(polygon: Union[Dict[str, Any], List[List[float]]], resolution: int) -> List[str]:
    """
    Convert polygon to H3 cell indices using h3 v4 API.
    
    Args:
        polygon: Either a GeoJSON-like dict or list of [lng, lat] coordinate pairs
        resolution: H3 resolution (0-15)
        
    Returns:
        List of H3 cell indices covering the polygon
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for polygon_to_cells")
    
    # Handle different input formats
    if isinstance(polygon, dict):
        # GeoJSON-like dictionary - use geo_to_cells for h3 v4
        return list(h3.geo_to_cells(polygon, resolution))
    elif isinstance(polygon, list):
        # List of coordinates - convert to LatLngPoly for h3 v4
        # Assume coordinates are in [lng, lat] format, convert to (lat, lng) for LatLngPoly
        lat_lng_coords = [(coord[1], coord[0]) for coord in polygon]
        h3_poly = h3.LatLngPoly(lat_lng_coords)
        return list(h3.polygon_to_cells(h3_poly, resolution))
    else:
        raise ValueError(f"Unsupported polygon format: {type(polygon)}")


def cell_to_latlngjson(
    h3_indices: List[str],
    properties: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Convert H3 indices to GeoJSON format (H3 4.x API).
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for cell_to_latlngjson")

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
    Convert GeoJSON to H3 indices (H3 4.x API).

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
                h3_indices = h3.polygon_to_cells(exterior, resolution)
        
        elif geometry_type == "MultiPolygon":
            # Convert each polygon to H3
            for polygon in coordinates:
                # Assuming first ring is exterior, rest are holes
                exterior = polygon[0]
                indices = h3.polygon_to_cells(exterior, resolution)
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