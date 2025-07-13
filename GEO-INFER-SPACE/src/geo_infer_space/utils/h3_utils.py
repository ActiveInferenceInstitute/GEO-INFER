"""
H3 utility functions for OSC-GEO.

This module provides utility functions for working with H3 grid data.
All functions are updated for H3 4.x API compatibility.
"""

import logging
import json
from typing import Dict, List, Union, Any, Optional, Tuple

logger = logging.getLogger(__name__)


def geo_to_h3(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude to H3 cell index (H3 4.x API).
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for geo_to_h3")
    return h3.latlng_to_cell(lat, lng, resolution)


def h3_to_geo(h3_index: str) -> Tuple[float, float]:
    """
    Get the center coordinates (lat, lng) of an H3 cell (H3 4.x API).
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for h3_to_geo")
    return h3.cell_to_latlng(h3_index)


def h3_to_geo_boundary(h3_index: str) -> List[Tuple[float, float]]:
    """
    Get the boundary of an H3 cell as a list of (lat, lng) tuples (H3 4.x API).
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for h3_to_geo_boundary")
    return list(h3.cell_to_boundary(h3_index))


def polyfill(geojson_polygon: Dict[str, Any], resolution: int) -> List[str]:
    """
    Fill a GeoJSON polygon with H3 cells at the given resolution (H3 4.x API).
    """
    try:
        import h3
    except ImportError:
        logger.error("h3-py package not found. Please install it with 'pip install h3'")
        raise ImportError("h3-py package required for polyfill")
    return list(h3.polygon_to_cells(geojson_polygon, resolution))


def h3_to_geojson(
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