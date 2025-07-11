"""
Shared H3 utility functions for Cascadian modules.

This module provides a simplified and robust interface to the OSC H3 utilities,
ensuring consistent H3 operations across the Cascadian analysis framework.
"""

import logging
from typing import Tuple, Any, List, Dict

# Import the OSC H3 utilities directly.
# This requires GEO-INFER-SPACE/src to be in the python path.
from geo_infer_space.osc_geo.utils.h3_utils import h3_to_geojson as osc_h3_to_geojson
from geo_infer_space.osc_geo.utils.h3_utils import geojson_to_h3 as osc_geojson_to_h3
HAS_OSC_UTILS = True

# Direct imports from h3-py for basic conversions
try:
    import h3
except ImportError:
    logging.critical("h3-py package not found. Please ensure it is installed.")
    raise

logger = logging.getLogger(__name__)

def geo_to_h3(lat: float, lng: float, resolution: int) -> str:
    """
    Safely convert latitude/longitude to an H3 index.
    """
    try:
        return h3.latlng_to_cell(lat, lng, resolution)
    except AttributeError:
        return h3.geo_to_h3(lat, lng, resolution)
    except Exception as e:
        logger.error(f"Failed to convert geo to h3: {e}")
        raise

def h3_to_geo(h3_index: str) -> Tuple[float, float]:
    """
    Safely convert an H3 index to a (latitude, longitude) tuple.
    """
    try:
        return h3.cell_to_latlng(h3_index)
    except AttributeError:
        return h3.h3_to_geo(h3_index)
    except Exception as e:
        logger.error(f"Failed to convert h3 to geo: {e}")
        raise

def h3_to_geo_boundary(h3_index: str, geo_json: bool = False) -> List[Tuple[float, float]]:
    """
    Safely get the boundary of an H3 cell. Handles different h3 library versions.
    """
    try:
        # For h3-py v4+, which doesn't use geo_json parameter in this function
        return h3.cell_to_boundary(h3_index)
    except TypeError:
        # Fallback for h3-py v3.x which expects geo_json
        try:
            return h3.h3_to_geo_boundary(h3_index, geo_json=geo_json)
        except Exception as e:
             logger.error(f"Failed to get h3 boundary with fallback: {e}")
             raise
    except Exception as e:
        logger.error(f"Failed to get h3 boundary: {e}")
        raise

def polyfill(geojson_polygon: Dict[str, Any], resolution: int) -> List[str]:
    """
    Polyfills a GeoJSON-like polygon, returning a set of H3 indices.
    """
    try:
        return list(h3.polygon_to_cells(geojson_polygon, resolution))
    except AttributeError:
        return list(h3.polyfill(geojson_polygon, resolution, geo_json_conformant=True))
    except Exception as e:
        logger.error(f"H3 polyfill operation failed: {e}")
        raise

if __name__ == "__main__":
    # Simple test cases to validate the wrapper functions
    logger.setLevel(logging.INFO)
    logging.basicConfig()

    test_lat, test_lng = 40.7128, -74.0060  # New York City
    test_res = 8
    
    try:
        # 1. geo_to_h3
        h3_index = geo_to_h3(test_lat, test_lng, test_res)
        logger.info(f"geo_to_h3({test_lat}, {test_lng}, {test_res}) -> {h3_index}")

        # 2. h3_to_geo
        lat_lng = h3_to_geo(h3_index)
        logger.info(f"h3_to_geo('{h3_index}') -> {lat_lng}")

        # 3. h3_to_geo_boundary
        boundary = h3_to_geo_boundary(h3_index)
        logger.info(f"h3_to_geo_boundary('{h3_index}') -> {len(boundary)} vertices")

        # 4. polyfill
        polygon = {
            "type": "Polygon",
            "coordinates": [
                [
                    [-74.01, 40.71], [-74.01, 40.72],
                    [-74.00, 40.72], [-74.00, 40.71],
                    [-74.01, 40.71]
                ]
            ]
        }
        filled_indices = polyfill(polygon, test_res)
        logger.info(f"polyfill() -> Found {len(filled_indices)} indices")

        logger.info("All H3 utility wrapper functions executed successfully.")
        
    except Exception as e:
        logger.error(f"An error occurred during testing: {e}") 