"""
Shared H3 utility functions for Cascadian modules.

Provides robust geo_to_h3, h3_to_geo, and related conversions compatible with both h3-py v3 and v4+ APIs.
"""

import logging
from typing import Tuple, Any

logger = logging.getLogger(__name__)

try:
    import h3
except ImportError:
    logger.error("h3-py package not found. Please install it with 'pip install h3'.")
    raise

def geo_to_h3(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude to H3 index, supporting both h3-py v3 and v4+ APIs.

    Args:
        lat: Latitude
        lng: Longitude
        resolution: H3 resolution (0-15)
    Returns:
        H3 index as string
    """
    try:
        if hasattr(h3, 'geo_to_h3'):
            return h3.geo_to_h3(lat, lng, resolution)
        elif hasattr(h3, 'latlng_to_cell'):
            return h3.latlng_to_cell(lat, lng, resolution)
        else:
            raise AttributeError("No geo_to_h3 or latlng_to_cell in h3 module.")
    except Exception as e:
        logger.error(f"geo_to_h3 conversion failed for ({lat}, {lng}, {resolution}): {e}")
        raise

def h3_to_geo(h3_index: str) -> Tuple[float, float]:
    """
    Convert H3 index to (lat, lng) tuple, supporting both h3-py v3 and v4+ APIs.

    Args:
        h3_index: H3 index string
    Returns:
        (lat, lng) tuple
    """
    try:
        if hasattr(h3, 'h3_to_geo'):
            return h3.h3_to_geo(h3_index)
        elif hasattr(h3, 'cell_to_lat_lng'):
            return h3.cell_to_lat_lng(h3_index)
        else:
            raise AttributeError("No h3_to_geo or cell_to_lat_lng in h3 module.")
    except Exception as e:
        logger.error(f"h3_to_geo conversion failed for {h3_index}: {e}")
        raise

def h3_to_geo_boundary(h3_index: str, geo_json: bool = True) -> Any:
    """
    Get the boundary of an H3 cell as a list of (lat, lng) tuples or GeoJSON format.

    Args:
        h3_index: H3 index string
        geo_json: Return as GeoJSON (lat, lng) if True, else (lng, lat)
    Returns:
        List of coordinates
    """
    try:
        if hasattr(h3, 'h3_to_geo_boundary'):
            return h3.h3_to_geo_boundary(h3_index, geo_json=geo_json)
        elif hasattr(h3, 'cell_to_boundary'):
            return h3.cell_to_boundary(h3_index, geo_json=geo_json)
        else:
            raise AttributeError("No h3_to_geo_boundary or cell_to_boundary in h3 module.")
    except Exception as e:
        logger.error(f"h3_to_geo_boundary failed for {h3_index}: {e}")
        raise

def polyfill(geojson_polygon: Any, resolution: int, geo_json: bool = True) -> Any:
    """
    Polyfill a GeoJSON polygon to H3 indices, supporting both h3-py v3 and v4+ APIs.

    Args:
        geojson_polygon: GeoJSON-like polygon
        resolution: H3 resolution
        geo_json: Use GeoJSON coordinate order
    Returns:
        Set or list of H3 indices
    """
    try:
        if hasattr(h3, 'polyfill'):
            return h3.polyfill(geojson_polygon, resolution, geo_json_conformant=geo_json)
        elif hasattr(h3, 'polygon_to_cells'):
            return h3.polygon_to_cells(geojson_polygon, resolution, geo_json_conformant=geo_json)
        else:
            raise AttributeError("No polyfill or polygon_to_cells in h3 module.")
    except Exception as e:
        logger.error(f"polyfill failed for {geojson_polygon}: {e}")
        raise 