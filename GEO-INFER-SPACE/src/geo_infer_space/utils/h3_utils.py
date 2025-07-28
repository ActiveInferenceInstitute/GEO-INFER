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
    Convert lat/lng to H3 cell index using H3 v4 API.
    
    Args:
        lat: Latitude
        lng: Longitude
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 cell index
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for latlng_to_cell")
    
    return h3.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(h3_index: str) -> Tuple[float, float]:
    """
    Convert H3 cell index to lat/lng using H3 v4 API.
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        (lat, lng) tuple
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for cell_to_latlng")
    
    return h3.cell_to_latlng(h3_index)


def cell_to_latlng_boundary(h3_index: str) -> List[Tuple[float, float]]:
    """
    Get H3 cell boundary as list of lat/lng pairs using H3 v4 API.
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        List of (lat, lng) tuples representing the boundary
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
        # For GeoJSON Feature or FeatureCollection
        if polygon.get('type') == 'Feature':
            return list(h3.geo_to_cells(polygon['geometry'], resolution))
        # For GeoJSON Geometry objects
        elif polygon.get('type') in ('Polygon', 'MultiPolygon'):
            # Ensure coordinates are properly nested for H3 v4
            if polygon.get('type') == 'Polygon' and polygon.get('coordinates'):
                if not isinstance(polygon['coordinates'][0][0], (list, tuple)):
                    polygon['coordinates'] = [polygon['coordinates']]
            return list(h3.geo_to_cells(polygon, resolution))
        # For GeoJSON FeatureCollection
        elif polygon.get('type') == 'FeatureCollection':
            all_cells = set()
            for feature in polygon.get('features', []):
                if 'geometry' in feature:
                    cells = h3.geo_to_cells(feature['geometry'], resolution)
                    all_cells.update(cells)
            return list(all_cells)
        else:
            raise ValueError(f"Unsupported GeoJSON type: {polygon.get('type')}")
    elif isinstance(polygon, list):
        # For coordinate lists, create a proper GeoJSON structure
        if polygon and isinstance(polygon[0], (list, tuple)) and len(polygon[0]) >= 2:
            # Create a GeoJSON polygon
            geojson = {
                "type": "Polygon",
                "coordinates": [polygon]  # Wrap in an array as GeoJSON requires
            }
            return list(h3.geo_to_cells(geojson, resolution))
        else:
            raise ValueError(f"Invalid coordinate list format: {polygon}")
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
        # Assume it's a geometry object
        features = [{"type": "Feature", "geometry": geojson_data, "properties": {}}]
    
    h3_indices = []
    properties_dict = {}
    
    for feature in features:
        geometry = feature.get("geometry", {})
        props = feature.get("properties", {})
        
        # Skip features without geometry
        if not geometry:
            continue
        
        # Convert geometry to H3 indices
        try:
            cells = h3.geo_to_cells(geometry, resolution)
            
            # Add to results
            for cell in cells:
                h3_indices.append(cell)
                if feature_properties:
                    properties_dict[cell] = props
        except Exception as e:
            logger.error(f"Failed to convert geometry to H3: {e}")
    
    result = {"h3_indices": h3_indices}
    if feature_properties:
        result["properties"] = properties_dict
    
    return result

# Additional H3 v4 utility functions

def geo_to_cells(geojson: Dict[str, Any], resolution: int) -> List[str]:
    """Convert GeoJSON to H3 cells using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for geo_to_cells")
    
    return list(h3.geo_to_cells(geojson, resolution))

def grid_disk(h3_index: str, k: int) -> List[str]:
    """Get k-ring around H3 index using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for grid_disk")
    
    return list(h3.grid_disk(h3_index, k))

def grid_distance(h3_index1: str, h3_index2: str) -> int:
    """Get grid distance between two H3 indices using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for grid_distance")
    
    return h3.grid_distance(h3_index1, h3_index2)

def compact_cells(h3_indices: List[str]) -> List[str]:
    """Compact H3 cells using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for compact_cells")
    
    return list(h3.compact_cells(h3_indices))

def uncompact_cells(h3_indices: List[str], resolution: int) -> List[str]:
    """Uncompact H3 cells using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for uncompact_cells")
    
    return list(h3.uncompact_cells(h3_indices, resolution))

def cell_area(h3_index: str, unit: str = 'km^2') -> float:
    """Get area of H3 cell using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for cell_area")
    
    return h3.cell_area(h3_index, unit)

def get_resolution(h3_index: str) -> int:
    """Get resolution of H3 index using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for get_resolution")
    
    return h3.get_resolution(h3_index)

def is_valid_cell(h3_index: str) -> bool:
    """Check if H3 index is valid using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for is_valid_cell")
    
    return h3.is_valid_cell(h3_index)

def are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool:
    """Check if two H3 indices are neighbors using H3 v4 API."""
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for are_neighbor_cells")
    
    return h3.are_neighbor_cells(h3_index1, h3_index2) 