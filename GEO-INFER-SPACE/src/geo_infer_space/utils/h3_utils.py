import logging
from typing import Tuple, Any, List, Dict
import h3

logger = logging.getLogger(__name__)

def geo_to_h3(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude to an H3 index.

    Args:
        lat: Latitude.
        lng: Longitude.
        resolution: H3 resolution level.

    Returns:
        H3 cell identifier.

    Raises:
        ValueError: If conversion fails.
    """
    try:
        return h3.latlng_to_cell(lat, lng, resolution)
    except AttributeError:
        return h3.geo_to_h3(lat, lng, resolution)
    except Exception as e:
        raise ValueError(f"Failed to convert geo to h3: {e}")

def h3_to_geo(h3_index: str) -> Tuple[float, float]:
    """
    Convert an H3 index to (latitude, longitude).

    Args:
        h3_index: H3 cell identifier.

    Returns:
        Tuple of (latitude, longitude).

    Raises:
        ValueError: If conversion fails.
    """
    try:
        return h3.cell_to_latlng(h3_index)
    except AttributeError:
        return h3.h3_to_geo(h3_index)
    except Exception as e:
        raise ValueError(f"Failed to convert h3 to geo: {e}")

def h3_to_geo_boundary(h3_index: str, geo_json: bool = False) -> List[Tuple[float, float]]:
    """
    Get the boundary of an H3 cell.

    Args:
        h3_index: H3 cell identifier.
        geo_json: Whether to return in GeoJSON format.

    Returns:
        List of (lat, lng) tuples representing the boundary.

    Raises:
        ValueError: If operation fails.
    """
    try:
        return h3.cell_to_boundary(h3_index)
    except TypeError:
        try:
            return h3.h3_to_geo_boundary(h3_index, geo_json=geo_json)
        except Exception as e:
            raise ValueError(f"Failed to get h3 boundary: {e}")
    except Exception as e:
        raise ValueError(f"Failed to get h3 boundary: {e}")

def polyfill(geojson_polygon: Dict[str, Any], resolution: int) -> List[str]:
    """
    Polyfill a GeoJSON polygon with H3 cells.

    Args:
        geojson_polygon: GeoJSON polygon dictionary.
        resolution: H3 resolution level.

    Returns:
        List of H3 cell identifiers covering the polygon.

    Raises:
        ValueError: If polyfill fails.
    """
    try:
        return list(h3.polygon_to_cells(geojson_polygon, resolution))
    except AttributeError:
        return list(h3.polyfill(geojson_polygon, resolution, geo_json_conformant=True))
    except Exception as e:
        raise ValueError(f"H3 polyfill operation failed: {e}") 