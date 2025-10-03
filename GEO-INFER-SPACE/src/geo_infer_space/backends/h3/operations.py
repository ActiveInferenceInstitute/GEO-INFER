"""
H3 Operations module providing comprehensive hexagonal grid operations.

This module implements all H3 v4 API operations with enhanced functionality,
error handling, and real-world spatial analysis capabilities.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union, Set
import json

logger = logging.getLogger(__name__)

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    H3_AVAILABLE = False
    logger.warning("h3-py package not available. Install with 'pip install h3'")


# Additional utility functions for comprehensive H3 operations

def get_resolution_info(resolution: int) -> Dict[str, Any]:
    """
    Get detailed information about an H3 resolution level.
    
    Based on H3 resolution table from:
    https://h3geo.org/docs/core-library/restable/
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        Dictionary containing resolution information
        
    Example:
        >>> info = get_resolution_info(9)
        >>> print(f"Resolution 9 average area: {info['avg_area_km2']:.6f} km²")
    """
    if not 0 <= resolution <= 15:
        raise ValueError("Resolution must be between 0 and 15")
    
    # H3 resolution information (approximate values)
    resolution_data = {
        0: {'avg_edge_length_km': 1107.712, 'avg_area_km2': 4250546.848},
        1: {'avg_edge_length_km': 418.676, 'avg_area_km2': 607220.982},
        2: {'avg_edge_length_km': 158.244, 'avg_area_km2': 86745.854},
        3: {'avg_edge_length_km': 59.810, 'avg_area_km2': 12392.264},
        4: {'avg_edge_length_km': 22.606, 'avg_area_km2': 1770.323},
        5: {'avg_edge_length_km': 8.544, 'avg_area_km2': 252.903},
        6: {'avg_edge_length_km': 3.229, 'avg_area_km2': 36.129},
        7: {'avg_edge_length_km': 1.220, 'avg_area_km2': 5.161},
        8: {'avg_edge_length_km': 0.461, 'avg_area_km2': 0.737},
        9: {'avg_edge_length_km': 0.174, 'avg_area_km2': 0.105},
        10: {'avg_edge_length_km': 0.065, 'avg_area_km2': 0.015},
        11: {'avg_edge_length_km': 0.025, 'avg_area_km2': 0.002},
        12: {'avg_edge_length_km': 0.009, 'avg_area_km2': 0.0003},
        13: {'avg_edge_length_km': 0.003, 'avg_area_km2': 0.00004},
        14: {'avg_edge_length_km': 0.001, 'avg_area_km2': 0.000007},
        15: {'avg_edge_length_km': 0.0005, 'avg_area_km2': 0.000001}
    }
    
    data = resolution_data[resolution]
    
    return {
        'resolution': resolution,
        'avg_edge_length_km': data['avg_edge_length_km'],
        'avg_edge_length_m': data['avg_edge_length_km'] * 1000,
        'avg_area_km2': data['avg_area_km2'],
        'avg_area_m2': data['avg_area_km2'] * 1000000,
        'description': f"Resolution {resolution}: ~{data['avg_edge_length_km']:.3f}km edge, ~{data['avg_area_km2']:.6f}km² area"
    }


def find_optimal_resolution(area_km2: float, target_cells: int = None) -> Dict[str, Any]:
    """
    Find the optimal H3 resolution for a given area or target number of cells.
    
    Args:
        area_km2: Area in square kilometers
        target_cells: Target number of cells (optional)
        
    Returns:
        Dictionary with recommended resolution and analysis
        
    Example:
        >>> optimal = find_optimal_resolution(100.0)  # 100 km²
        >>> print(f"Recommended resolution: {optimal['recommended_resolution']}")
    """
    recommendations = []
    
    for resolution in range(16):
        res_info = get_resolution_info(resolution)
        
        # Estimate number of cells needed
        estimated_cells = area_km2 / res_info['avg_area_km2']
        
        # Calculate efficiency score
        if target_cells:
            efficiency = 1.0 / (1.0 + abs(estimated_cells - target_cells) / target_cells)
        else:
            # Prefer resolutions that give reasonable cell counts (10-10000)
            if 10 <= estimated_cells <= 10000:
                efficiency = 1.0
            elif estimated_cells < 10:
                efficiency = estimated_cells / 10
            else:
                efficiency = 10000 / estimated_cells
        
        recommendations.append({
            'resolution': resolution,
            'estimated_cells': int(estimated_cells),
            'efficiency_score': efficiency,
            'avg_area_km2': res_info['avg_area_km2'],
            'avg_edge_length_km': res_info['avg_edge_length_km']
        })
    
    # Sort by efficiency score
    recommendations.sort(key=lambda x: x['efficiency_score'], reverse=True)
    
    return {
        'area_km2': area_km2,
        'target_cells': target_cells,
        'recommended_resolution': recommendations[0]['resolution'],
        'estimated_cells': recommendations[0]['estimated_cells'],
        'all_options': recommendations[:5]  # Top 5 options
    }


def create_h3_grid_for_bounds(min_lat: float, max_lat: float, 
                             min_lng: float, max_lng: float,
                             resolution: int) -> List[str]:
    """
    Create an H3 grid covering the specified bounding box.
    
    Args:
        min_lat: Minimum latitude
        max_lat: Maximum latitude
        min_lng: Minimum longitude
        max_lng: Maximum longitude
        resolution: H3 resolution
        
    Returns:
        Set of H3 cell indices covering the bounding box
        
    Example:
        >>> grid = create_h3_grid_for_bounds(37.7, 37.8, -122.5, -122.4, 9)
        >>> print(f"Created grid with {len(grid)} cells")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    # Validate bounds
    if not (-90 <= min_lat <= max_lat <= 90):
        raise ValueError("Invalid latitude bounds")
    if not (-180 <= min_lng <= max_lng <= 180):
        raise ValueError("Invalid longitude bounds")
    if not (0 <= resolution <= 15):
        raise ValueError("Resolution must be between 0 and 15")
    
    try:
        # Create bounding box polygon
        bbox_coords = [
            (min_lat, min_lng),
            (min_lat, max_lng),
            (max_lat, max_lng),
            (max_lat, min_lng)
        ]
        
        return polygon_to_cells(bbox_coords, resolution)
    
    except Exception as e:
        logger.error(f"Failed to create H3 grid for bounds: {e}")
        raise


# Core Coordinate Operations

def coordinate_to_cell(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude coordinates to H3 cell index.
    
    Args:
        lat: Latitude in degrees (-90 to 90)
        lng: Longitude in degrees (-180 to 180)
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 cell index string
        
    Raises:
        ImportError: If h3-py package not available
        ValueError: If coordinates or resolution invalid
        
    Example:
        >>> cell = coordinate_to_cell(37.7749, -122.4194, 9)
        >>> print(cell)
        '89283082e3fffff'
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    # Validate inputs
    if not -90 <= lat <= 90:
        raise ValueError(f"Latitude {lat} must be between -90 and 90")
    
    if not -180 <= lng <= 180:
        raise ValueError(f"Longitude {lng} must be between -180 and 180")
    
    if not 0 <= resolution <= 15:
        raise ValueError(f"Resolution {resolution} must be between 0 and 15")
    
    try:
        return h3.latlng_to_cell(lat, lng, resolution)
    except Exception as e:
        logger.error(f"Failed to convert coordinates ({lat}, {lng}) to H3 cell: {e}")
        raise


def cell_to_coordinates(h3_index: str) -> Tuple[float, float]:
    """
    Convert H3 cell index to latitude/longitude coordinates.
    
    Args:
        h3_index: H3 cell index string
        
    Returns:
        Tuple of (latitude, longitude) coordinates
        
    Raises:
        ImportError: If h3-py package not available
        ValueError: If H3 index is invalid
        
    Example:
        >>> coords = cell_to_coordinates('89283082e3fffff')
        >>> print(f"Lat: {coords[0]:.4f}, Lng: {coords[1]:.4f}")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.cell_to_latlng(h3_index)
    except Exception as e:
        logger.error(f"Failed to convert H3 index {h3_index} to coordinates: {e}")
        raise ValueError(f"Invalid H3 index: {h3_index}")


def cell_to_boundary(h3_index: str, geo_json: bool = False) -> List[Tuple[float, float]]:
    """
    Get the boundary coordinates of an H3 cell.
    
    Based on methods from Helsinki bike sharing analysis:
    https://towardsdatascience.com/exploring-location-data-using-a-hexagon-grid-3509b68b04a2
    
    Args:
        h3_index: H3 cell index string
        geo_json: If True, return coordinates in GeoJSON format (lng, lat)
        
    Returns:
        List of boundary coordinate tuples
        
    Example:
        >>> boundary = cell_to_boundary('89283082e3fffff')
        >>> print(f"Hexagon has {len(boundary)} vertices")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.cell_to_boundary(h3_index, geo_json=geo_json)
    except Exception as e:
        logger.error(f"Failed to get boundary for H3 index {h3_index}: {e}")
        raise ValueError(f"Invalid H3 index: {h3_index}")


def cells_to_geojson(h3_indices: List[str], properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convert H3 cell indices to GeoJSON FeatureCollection.
    
    Based on methods from UGRC's H3 analysis:
    https://gis.utah.gov/blog/2022-10-26-using-h3-hexes/
    
    Args:
        h3_indices: List of H3 cell indices
        properties: Optional properties to add to each feature
        
    Returns:
        GeoJSON FeatureCollection dictionary
        
    Example:
        >>> cells = ['89283082e3fffff', '89283082e7fffff']
        >>> geojson = cells_to_geojson(cells, {'type': 'analysis_area'})
        >>> print(f"Created FeatureCollection with {len(geojson['features'])} features")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    features = []
    
    for h3_index in h3_indices:
        try:
            # Get boundary coordinates
            boundary = h3.cell_to_boundary(h3_index, geo_json=True)
            
            # Create polygon coordinates (close the ring)
            coordinates = [list(boundary) + [boundary[0]]]
            
            # Create feature
            feature = {
                "type": "Feature",
                "properties": {
                    "h3_index": h3_index,
                    "resolution": h3.get_resolution(h3_index)
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": coordinates
                }
            }
            
            # Add additional properties if provided
            if properties:
                feature["properties"].update(properties)
            
            features.append(feature)
            
        except Exception as e:
            logger.warning(f"Failed to convert H3 index {h3_index} to GeoJSON: {e}")
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


# Grid Operations

def grid_disk(h3_index: str, k: int) -> List[str]:
    """
    Get all H3 cells within k rings of the given cell (k-ring).
    
    Based on methods from Foursquare's H3 guide:
    https://location.foursquare.com/resources/reports-and-insights/ebook/how-to-use-h3-for-geospatial-analytics/
    
    Args:
        h3_index: Center H3 cell index
        k: Number of rings (0 = just the center cell)
        
    Returns:
        Set of H3 cell indices within k rings
        
    Example:
        >>> neighbors = grid_disk('89283082e3fffff', 2)
        >>> print(f"Found {len(neighbors)} cells within 2 rings")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return list(h3.grid_disk(h3_index, k))
    except Exception as e:
        logger.error(f"Failed to get grid disk for {h3_index} with k={k}: {e}")
        raise


def grid_ring(h3_index: str, k: int) -> List[str]:
    """
    Get H3 cells at exactly k rings from the given cell.
    
    Args:
        h3_index: Center H3 cell index
        k: Ring distance (must be > 0)
        
    Returns:
        Set of H3 cell indices at exactly k rings
        
    Example:
        >>> ring_cells = grid_ring('89283082e3fffff', 1)
        >>> print(f"Found {len(ring_cells)} cells at ring 1")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if k <= 0:
        raise ValueError("Ring distance k must be greater than 0")
    
    try:
        return list(h3.grid_ring(h3_index, k))
    except Exception as e:
        logger.error(f"Failed to get grid ring for {h3_index} with k={k}: {e}")
        raise


def grid_distance(h3_index1: str, h3_index2: str) -> int:
    """
    Calculate the grid distance between two H3 cells.
    
    Based on methods from Analytics Vidhya's H3 guide:
    https://www.analyticsvidhya.com/blog/2025/03/ubers-h3-for-spatial-indexing/
    
    Args:
        h3_index1: First H3 cell index
        h3_index2: Second H3 cell index
        
    Returns:
        Grid distance (number of steps)
        
    Example:
        >>> distance = grid_distance('89283082e3fffff', '89283082e7fffff')
        >>> print(f"Grid distance: {distance} steps")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.grid_distance(h3_index1, h3_index2)
    except Exception as e:
        logger.error(f"Failed to calculate grid distance between {h3_index1} and {h3_index2}: {e}")
        raise


def grid_path(h3_index1: str, h3_index2: str) -> List[str]:
    """
    Find a path between two H3 cells.
    
    Args:
        h3_index1: Start H3 cell index
        h3_index2: End H3 cell index
        
    Returns:
        List of H3 cell indices forming a path
        
    Example:
        >>> path = grid_path('89283082e3fffff', '89283082e7fffff')
        >>> print(f"Path has {len(path)} steps")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.grid_path_cells(h3_index1, h3_index2)
    except Exception as e:
        logger.error(f"Failed to find grid path between {h3_index1} and {h3_index2}: {e}")
        raise


# Hierarchy Operations

def cell_to_parent(h3_index: str, parent_resolution: int) -> str:
    """
    Get the parent cell at a coarser resolution.
    
    Args:
        h3_index: H3 cell index
        parent_resolution: Target parent resolution (must be < current resolution)
        
    Returns:
        Parent H3 cell index
        
    Example:
        >>> parent = cell_to_parent('89283082e3fffff', 8)
        >>> print(f"Parent cell: {parent}")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        current_resolution = h3.get_resolution(h3_index)
        if parent_resolution >= current_resolution:
            raise ValueError(f"Parent resolution {parent_resolution} must be less than current resolution {current_resolution}")
        
        return h3.cell_to_parent(h3_index, parent_resolution)
    except Exception as e:
        logger.error(f"Failed to get parent for {h3_index} at resolution {parent_resolution}: {e}")
        raise


def cell_to_children(h3_index: str, child_resolution: int) -> List[str]:
    """
    Get the children cells at a finer resolution.
    
    Args:
        h3_index: H3 cell index
        child_resolution: Target child resolution (must be > current resolution)
        
    Returns:
        Set of child H3 cell indices
        
    Example:
        >>> children = cell_to_children('89283082e3fffff', 10)
        >>> print(f"Found {len(children)} children")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        current_resolution = h3.get_resolution(h3_index)
        if child_resolution <= current_resolution:
            raise ValueError(f"Child resolution {child_resolution} must be greater than current resolution {current_resolution}")
        
        return list(h3.cell_to_children(h3_index, child_resolution))
    except Exception as e:
        logger.error(f"Failed to get children for {h3_index} at resolution {child_resolution}: {e}")
        raise


def compact_cells(h3_indices: Set[str]) -> List[str]:
    """
    Compact a set of H3 cells by replacing clusters with their parents.
    
    Args:
        h3_indices: Set of H3 cell indices
        
    Returns:
        Compacted set of H3 cell indices
        
    Example:
        >>> cells = {'89283082e3fffff', '89283082e7fffff', '89283082ebfffff'}
        >>> compacted = compact_cells(cells)
        >>> print(f"Compacted from {len(cells)} to {len(compacted)} cells")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return list(h3.compact_cells(h3_indices))
    except Exception as e:
        logger.error(f"Failed to compact cells: {e}")
        raise


def uncompact_cells(h3_indices: Set[str], target_resolution: int) -> List[str]:
    """
    Uncompact a set of H3 cells to a target resolution.
    
    Args:
        h3_indices: Set of H3 cell indices
        target_resolution: Target resolution for uncompacting
        
    Returns:
        Uncompacted set of H3 cell indices
        
    Example:
        >>> cells = {'89283082e3fffff'}
        >>> uncompacted = uncompact_cells(cells, 10)
        >>> print(f"Uncompacted to {len(uncompacted)} cells")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return list(h3.uncompact_cells(h3_indices, target_resolution))
    except Exception as e:
        logger.error(f"Failed to uncompact cells to resolution {target_resolution}: {e}")
        raise


# Area Operations

def polygon_to_cells(polygon_coords: List[Tuple[float, float]], resolution: int) -> List[str]:
    """
    Get H3 cells that cover a polygon.
    
    Based on methods from UGRC's address point analysis:
    https://gis.utah.gov/blog/2022-10-26-using-h3-hexes/
    
    Args:
        polygon_coords: List of (lat, lng) or (lng, lat) coordinate tuples
        resolution: H3 resolution for the cells
        geo_json_conformant: If True, coordinates are (lng, lat); if False, (lat, lng)
        
    Returns:
        Set of H3 cell indices covering the polygon
        
    Example:
        >>> coords = [(37.7749, -122.4194), (37.7849, -122.4194), (37.7849, -122.4094), (37.7749, -122.4094)]
        >>> cells = polygon_to_cells(coords, 9, geo_json_conformant=False)
        >>> print(f"Polygon covered by {len(cells)} H3 cells")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        # Use H3's polygon_to_cells function
        # H3 expects coordinates as (lat, lng)
        return list(h3.polygon_to_cells(polygon_coords, resolution))
    except Exception as e:
        logger.error(f"Failed to convert polygon to H3 cells: {e}")
        raise


def cells_to_polygon(h3_indices: Set[str]) -> List[Tuple[float, float]]:
    """
    Create a polygon boundary from a set of H3 cells.
    
    Args:
        h3_indices: Set of H3 cell indices
        
    Returns:
        List of (lat, lng) coordinates forming the polygon boundary
        
    Example:
        >>> cells = {'89283082e3fffff', '89283082e7fffff'}
        >>> boundary = cells_to_polygon(cells)
        >>> print(f"Boundary has {len(boundary)} vertices")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.cells_to_polygon(h3_indices, geo_json=False)
    except Exception as e:
        logger.error(f"Failed to convert cells to polygon: {e}")
        raise


def cell_area(h3_index: str, unit: str = 'km^2') -> float:
    """
    Calculate the area of an H3 cell.
    
    Args:
        h3_index: H3 cell index
        unit: Area unit ('km^2', 'm^2', 'rads^2')
        
    Returns:
        Cell area in specified units
        
    Example:
        >>> area = cell_area('89283082e3fffff', 'km^2')
        >>> print(f"Cell area: {area:.6f} km²")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.cell_area(h3_index, unit=unit)
    except Exception as e:
        logger.error(f"Failed to calculate area for {h3_index}: {e}")
        raise


def cells_area(h3_indices: Set[str], unit: str = 'km^2') -> float:
    """
    Calculate the total area of a set of H3 cells.
    
    Args:
        h3_indices: Set of H3 cell indices
        unit: Area unit ('km^2', 'm^2', 'rads^2')
        
    Returns:
        Total area in specified units
        
    Example:
        >>> cells = {'89283082e3fffff', '89283082e7fffff'}
        >>> total_area = cells_area(cells, 'km^2')
        >>> print(f"Total area: {total_area:.6f} km²")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        total_area = 0.0
        for h3_index in h3_indices:
            total_area += h3.cell_area(h3_index, unit=unit)
        return total_area
    except Exception as e:
        logger.error(f"Failed to calculate total area: {e}")
        raise


# Analysis Operations

def neighbor_cells(h3_index: str) -> List[str]:
    """
    Get the immediate neighbors of an H3 cell.
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        Set of neighboring H3 cell indices
        
    Example:
        >>> neighbors = neighbor_cells('89283082e3fffff')
        >>> print(f"Cell has {len(neighbors)} neighbors")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        # Get k-ring with k=1 and remove the center cell
        k_ring = list(h3.grid_disk(h3_index, 1))
        if h3_index in k_ring:
            k_ring.remove(h3_index)
        return k_ring
    except Exception as e:
        logger.error(f"Failed to get neighbors for {h3_index}: {e}")
        raise


def cell_resolution(h3_index: str) -> int:
    """
    Get the resolution of an H3 cell.
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        H3 resolution (0-15)
        
    Example:
        >>> resolution = cell_resolution('89283082e3fffff')
        >>> print(f"Cell resolution: {resolution}")
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    try:
        return h3.get_resolution(h3_index)
    except Exception as e:
        logger.error(f"Failed to get resolution for {h3_index}: {e}")
        raise


def is_valid_cell(h3_index: str) -> bool:
    """
    Check if an H3 index is valid.
    
    Args:
        h3_index: H3 cell index to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> valid = is_valid_cell('89283082e3fffff')
        >>> print(f"Index is valid: {valid}")
    """
    if not H3_AVAILABLE:
        return False
    
    try:
        return h3.is_valid_cell(h3_index)
    except Exception:
        return False


def are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool:
    """
    Check if two H3 cells are neighbors.
    
    Args:
        h3_index1: First H3 cell index
        h3_index2: Second H3 cell index
        
    Returns:
        True if cells are neighbors, False otherwise
        
    Example:
        >>> neighbors = are_neighbor_cells('89283082e3fffff', '89283082e7fffff')
        >>> print(f"Cells are neighbors: {neighbors}")
    """
    if not H3_AVAILABLE:
        return False
    
    try:
        return h3.are_neighbor_cells(h3_index1, h3_index2)
    except Exception:
        return False


# Advanced Operations

def cells_intersection(cells1: Set[str], cells2: Set[str]) -> List[str]:
    """
    Find the intersection of two sets of H3 cells.
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        Set of H3 cell indices in both sets
        
    Example:
        >>> set1 = {'89283082e3fffff', '89283082e7fffff'}
        >>> set2 = {'89283082e7fffff', '89283082ebfffff'}
        >>> intersection = cells_intersection(set1, set2)
        >>> print(f"Intersection has {len(intersection)} cells")
    """
    return list(cells1.intersection(cells2))


def cells_union(cells1: Set[str], cells2: Set[str]) -> List[str]:
    """
    Find the union of two sets of H3 cells.
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        Set of H3 cell indices in either set
        
    Example:
        >>> set1 = {'89283082e3fffff', '89283082e7fffff'}
        >>> set2 = {'89283082e7fffff', '89283082ebfffff'}
        >>> union = cells_union(set1, set2)
        >>> print(f"Union has {len(union)} cells")
    """
    return list(cells1.union(cells2))


def cells_difference(cells1: Set[str], cells2: Set[str]) -> List[str]:
    """
    Find the difference between two sets of H3 cells.
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        Set of H3 cell indices in cells1 but not in cells2
        
    Example:
        >>> set1 = {'89283082e3fffff', '89283082e7fffff'}
        >>> set2 = {'89283082e7fffff', '89283082ebfffff'}
        >>> difference = cells_difference(set1, set2)
        >>> print(f"Difference has {len(difference)} cells")
    """
    return list(cells1.difference(cells2))


def grid_statistics(h3_indices: Set[str]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a set of H3 cells.
    
    Based on methods from multiple H3 analysis guides.
    
    Args:
        h3_indices: Set of H3 cell indices
        
    Returns:
        Dictionary containing grid statistics
        
    Example:
        >>> cells = {'89283082e3fffff', '89283082e7fffff', '89283082ebfffff'}
        >>> stats = grid_statistics(cells)
        >>> print(f"Total area: {stats['total_area_km2']:.2f} km²")
    """
    if not h3_indices:
        return {'error': 'No cells provided'}
    
    if not H3_AVAILABLE:
        return {'error': 'h3-py package required'}
    
    try:
        # Basic counts
        total_cells = len(h3_indices)
        
        # Resolution analysis
        resolutions = [h3.get_resolution(idx) for idx in h3_indices]
        unique_resolutions = set(resolutions)
        
        # Area calculations
        total_area_km2 = sum(h3.cell_area(idx, 'km^2') for idx in h3_indices)
        total_area_m2 = sum(h3.cell_area(idx, 'm^2') for idx in h3_indices)
        
        # Connectivity analysis
        connected_pairs = 0
        total_possible_pairs = total_cells * (total_cells - 1) // 2
        
        h3_list = list(h3_indices)
        for i in range(len(h3_list)):
            for j in range(i + 1, len(h3_list)):
                if h3.are_neighbor_cells(h3_list[i], h3_list[j]):
                    connected_pairs += 1
        
        connectivity_ratio = connected_pairs / total_possible_pairs if total_possible_pairs > 0 else 0
        
        # Compactness (try to compact and see reduction)
        try:
            compacted = h3.compact_cells(h3_indices)
            compactness_ratio = len(compacted) / total_cells
        except:
            compactness_ratio = 1.0  # No compaction possible
        
        # Bounding box
        if h3_indices:
            all_coords = [h3.cell_to_latlng(idx) for idx in h3_indices]
            lats = [coord[0] for coord in all_coords]
            lngs = [coord[1] for coord in all_coords]
            
            bounding_box = {
                'min_lat': min(lats),
                'max_lat': max(lats),
                'min_lng': min(lngs),
                'max_lng': max(lngs)
            }
            
            # Calculate bounding box area
            bbox_area_km2 = (bounding_box['max_lat'] - bounding_box['min_lat']) * \
                           (bounding_box['max_lng'] - bounding_box['min_lng']) * 111.32 * 111.32  # Rough conversion
        else:
            bounding_box = None
            bbox_area_km2 = 0
        
        return {
            'total_cells': total_cells,
            'unique_resolutions': list(unique_resolutions),
            'resolution_counts': {res: resolutions.count(res) for res in unique_resolutions},
            'total_area_km2': total_area_km2,
            'total_area_m2': total_area_m2,
            'average_area_km2': total_area_km2 / total_cells if total_cells > 0 else 0,
            'connected_pairs': connected_pairs,
            'connectivity_ratio': connectivity_ratio,
            'compactness_ratio': compactness_ratio,
            'bounding_box': bounding_box,
            'bbox_area_km2': bbox_area_km2,
            'coverage_efficiency': (total_area_km2 / bbox_area_km2) if bbox_area_km2 > 0 else 0
        }
    
    except Exception as e:
        logger.error(f"Failed to calculate grid statistics: {e}")
        return {'error': str(e)}
    """
    Convert H3 cell index to latitude/longitude coordinates.
    
    Args:
        h3_index: H3 cell index string
        
    Returns:
        Tuple of (latitude, longitude) in degrees
        
    Raises:
        ImportError: If h3-py package not available
        ValueError: If H3 index invalid
        
    Example:
        >>> lat, lng = cell_to_coordinates('89283082e3fffff')
        >>> print(f"({lat:.6f}, {lng:.6f})")
        (37.774929, -122.419415)
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    try:
        return h3.cell_to_latlng(h3_index)
    except Exception as e:
        logger.error(f"Failed to convert H3 cell {h3_index} to coordinates: {e}")
        raise


def cell_to_boundary(h3_index: str, geo_json_format: bool = False) -> Union[List[Tuple[float, float]], List[List[float]]]:
    """
    Get boundary coordinates of H3 cell as polygon vertices.
    
    Args:
        h3_index: H3 cell index string
        geo_json_format: If True, return as [lng, lat] for GeoJSON compatibility
        
    Returns:
        List of coordinate tuples (lat, lng) or [lng, lat] if geo_json_format=True
        
    Raises:
        ImportError: If h3-py package not available
        ValueError: If H3 index invalid
        
    Example:
        >>> boundary = cell_to_boundary('89283082e3fffff')
        >>> print(f"Hexagon has {len(boundary)} vertices")
        Hexagon has 6 vertices
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    try:
        boundary = list(h3.cell_to_boundary(h3_index))
        
        if geo_json_format:
            # Convert (lat, lng) to [lng, lat] for GeoJSON
            return [[lng, lat] for lat, lng in boundary]
        else:
            return boundary
            
    except Exception as e:
        logger.error(f"Failed to get boundary for H3 cell {h3_index}: {e}")
        raise


def cells_to_geojson(h3_indices: List[str], properties: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Convert list of H3 cell indices to GeoJSON FeatureCollection.
    
    Args:
        h3_indices: List of H3 cell index strings
        properties: Optional dict mapping cell indices to properties
        
    Returns:
        GeoJSON FeatureCollection dictionary
        
    Example:
        >>> cells = ['89283082e3fffff', '89283082e7fffff']
        >>> props = {'89283082e3fffff': {'value': 100}}
        >>> geojson = cells_to_geojson(cells, props)
        >>> print(geojson['type'])
        FeatureCollection
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    features = []
    
    for h3_index in h3_indices:
        if not h3.is_valid_cell(h3_index):
            logger.warning(f"Skipping invalid H3 cell: {h3_index}")
            continue
        
        try:
            # Get cell boundary
            boundary = cell_to_boundary(h3_index, geo_json_format=True)
            
            # Ensure polygon is closed
            if boundary and boundary[0] != boundary[-1]:
                boundary.append(boundary[0])
            
            # Get cell properties
            lat, lng = cell_to_coordinates(h3_index)
            resolution = h3.get_resolution(h3_index)
            area_km2 = h3.cell_area(h3_index, 'km^2')
            
            # Create feature
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [boundary]
                },
                "properties": {
                    "h3_index": h3_index,
                    "resolution": resolution,
                    "latitude": lat,
                    "longitude": lng,
                    "area_km2": area_km2
                }
            }
            
            # Add custom properties
            if properties and h3_index in properties:
                feature["properties"].update(properties[h3_index])
            
            features.append(feature)
            
        except Exception as e:
            logger.error(f"Failed to process H3 cell {h3_index}: {e}")
            continue
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


# Grid Operations

def grid_disk(h3_index: str, k: int = 1) -> List[str]:
    """
    Get all cells within k distance of the given cell (filled disk).
    
    Args:
        h3_index: Center H3 cell index
        k: Distance (number of rings), 0 returns only center cell
        
    Returns:
        List of H3 cell indices within k distance
        
    Example:
        >>> center = '89283082e3fffff'
        >>> neighbors = grid_disk(center, k=2)
        >>> print(f"Found {len(neighbors)} cells within 2 rings")
        Found 19 cells within 2 rings
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    if k < 0:
        raise ValueError(f"Distance k must be non-negative, got {k}")
    
    try:
        return list(h3.grid_disk(h3_index, k))
    except Exception as e:
        logger.error(f"Failed to get grid disk for {h3_index} with k={k}: {e}")
        raise


def grid_ring(h3_index: str, k: int) -> List[str]:
    """
    Get all cells at exactly k distance from the given cell (hollow ring).
    
    Args:
        h3_index: Center H3 cell index
        k: Distance (ring number), must be > 0
        
    Returns:
        List of H3 cell indices at exactly k distance
        
    Example:
        >>> center = '89283082e3fffff'
        >>> ring = grid_ring(center, k=1)
        >>> print(f"Ring 1 has {len(ring)} cells")
        Ring 1 has 6 cells
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    if k <= 0:
        raise ValueError(f"Ring distance k must be positive, got {k}")
    
    try:
        return list(h3.grid_ring(h3_index, k))
    except Exception as e:
        logger.error(f"Failed to get grid ring for {h3_index} with k={k}: {e}")
        raise


def grid_distance(h3_index1: str, h3_index2: str) -> int:
    """
    Calculate grid distance between two H3 cells.
    
    Args:
        h3_index1: First H3 cell index
        h3_index2: Second H3 cell index
        
    Returns:
        Grid distance (number of cells between)
        
    Example:
        >>> cell1 = '89283082e3fffff'
        >>> cell2 = '89283082e7fffff'
        >>> distance = grid_distance(cell1, cell2)
        >>> print(f"Distance: {distance} cells")
        Distance: 2 cells
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index1):
        raise ValueError(f"Invalid H3 cell index: {h3_index1}")
    
    if not h3.is_valid_cell(h3_index2):
        raise ValueError(f"Invalid H3 cell index: {h3_index2}")
    
    # Check if cells have same resolution
    res1 = h3.get_resolution(h3_index1)
    res2 = h3.get_resolution(h3_index2)
    
    if res1 != res2:
        logger.warning(f"Cells have different resolutions: {res1} vs {res2}")
    
    try:
        return h3.grid_distance(h3_index1, h3_index2)
    except Exception as e:
        logger.error(f"Failed to calculate distance between {h3_index1} and {h3_index2}: {e}")
        raise


def grid_path(h3_index1: str, h3_index2: str) -> List[str]:
    """
    Find path of cells between two H3 cells.
    
    Args:
        h3_index1: Start H3 cell index
        h3_index2: End H3 cell index
        
    Returns:
        List of H3 cell indices forming path (including start and end)
        
    Example:
        >>> start = '89283082e3fffff'
        >>> end = '89283082e7fffff'
        >>> path = grid_path(start, end)
        >>> print(f"Path has {len(path)} cells")
        Path has 3 cells
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index1):
        raise ValueError(f"Invalid H3 cell index: {h3_index1}")
    
    if not h3.is_valid_cell(h3_index2):
        raise ValueError(f"Invalid H3 cell index: {h3_index2}")
    
    try:
        return list(h3.grid_path_cells(h3_index1, h3_index2))
    except Exception as e:
        logger.error(f"Failed to find path between {h3_index1} and {h3_index2}: {e}")
        raise


# Hierarchy Operations

def cell_to_parent(h3_index: str, parent_resolution: int) -> str:
    """
    Get parent cell at coarser resolution.
    
    Args:
        h3_index: H3 cell index
        parent_resolution: Target parent resolution (must be < current resolution)
        
    Returns:
        Parent H3 cell index
        
    Example:
        >>> child = '89283082e3fffff'  # Resolution 9
        >>> parent = cell_to_parent(child, 7)
        >>> print(f"Parent at resolution 7: {parent}")
        Parent at resolution 7: 87283082e3fffff
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    current_resolution = h3.get_resolution(h3_index)
    
    if parent_resolution >= current_resolution:
        raise ValueError(f"Parent resolution {parent_resolution} must be < current resolution {current_resolution}")
    
    if parent_resolution < 0:
        raise ValueError(f"Parent resolution {parent_resolution} must be >= 0")
    
    try:
        return h3.cell_to_parent(h3_index, parent_resolution)
    except Exception as e:
        logger.error(f"Failed to get parent of {h3_index} at resolution {parent_resolution}: {e}")
        raise


def cell_to_children(h3_index: str, child_resolution: int) -> List[str]:
    """
    Get child cells at finer resolution.
    
    Args:
        h3_index: H3 cell index
        child_resolution: Target child resolution (must be > current resolution)
        
    Returns:
        List of child H3 cell indices
        
    Example:
        >>> parent = '87283082e3fffff'  # Resolution 7
        >>> children = cell_to_children(parent, 9)
        >>> print(f"Parent has {len(children)} children at resolution 9")
        Parent has 49 children at resolution 9
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    current_resolution = h3.get_resolution(h3_index)
    
    if child_resolution <= current_resolution:
        raise ValueError(f"Child resolution {child_resolution} must be > current resolution {current_resolution}")
    
    if child_resolution > 15:
        raise ValueError(f"Child resolution {child_resolution} must be <= 15")
    
    try:
        return list(h3.cell_to_children(h3_index, child_resolution))
    except Exception as e:
        logger.error(f"Failed to get children of {h3_index} at resolution {child_resolution}: {e}")
        raise


def compact_cells(h3_indices: List[str]) -> List[str]:
    """
    Compact set of cells to mixed resolutions for efficiency.
    
    Args:
        h3_indices: List of H3 cell indices
        
    Returns:
        List of compacted H3 cell indices (may have mixed resolutions)
        
    Example:
        >>> cells = grid_disk('89283082e3fffff', k=2)
        >>> compacted = compact_cells(cells)
        >>> print(f"Compacted {len(cells)} cells to {len(compacted)}")
        Compacted 19 cells to 7
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3_indices:
        return []
    
    # Validate all indices
    invalid_indices = [idx for idx in h3_indices if not h3.is_valid_cell(idx)]
    if invalid_indices:
        raise ValueError(f"Invalid H3 cell indices: {invalid_indices[:5]}...")  # Show first 5
    
    try:
        return list(h3.compact_cells(h3_indices))
    except Exception as e:
        logger.error(f"Failed to compact {len(h3_indices)} cells: {e}")
        raise


def uncompact_cells(h3_indices: List[str], target_resolution: int) -> List[str]:
    """
    Uncompact cells to uniform resolution.
    
    Args:
        h3_indices: List of H3 cell indices (may have mixed resolutions)
        target_resolution: Target resolution for all cells
        
    Returns:
        List of H3 cell indices at uniform resolution
        
    Example:
        >>> mixed_res_cells = ['87283082e3fffff', '89283082e3fffff']
        >>> uniform = uncompact_cells(mixed_res_cells, 9)
        >>> print(f"Uncompacted to {len(uniform)} cells at resolution 9")
        Uncompacted to 50 cells at resolution 9
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3_indices:
        return []
    
    if not 0 <= target_resolution <= 15:
        raise ValueError(f"Target resolution {target_resolution} must be between 0 and 15")
    
    # Validate all indices
    invalid_indices = [idx for idx in h3_indices if not h3.is_valid_cell(idx)]
    if invalid_indices:
        raise ValueError(f"Invalid H3 cell indices: {invalid_indices[:5]}...")  # Show first 5
    
    try:
        return list(h3.uncompact_cells(h3_indices, target_resolution))
    except Exception as e:
        logger.error(f"Failed to uncompact {len(h3_indices)} cells to resolution {target_resolution}: {e}")
        raise


# Area Operations

def polygon_to_cells(polygon_coords: Union[List[Tuple[float, float]], Dict[str, Any]], 
                    resolution: int, 
                    geo_json_format: bool = False) -> List[str]:
    """
    Convert polygon to H3 cells that cover the area.
    
    Args:
        polygon_coords: Polygon coordinates as list of (lat, lng) tuples or GeoJSON geometry
        resolution: H3 resolution for coverage
        geo_json_format: If True, treat coordinates as [lng, lat] (GeoJSON format)
        
    Returns:
        List of H3 cell indices covering the polygon
        
    Example:
        >>> # San Francisco polygon (simplified)
        >>> sf_coords = [(37.7749, -122.4194), (37.7849, -122.4094), (37.7649, -122.4094)]
        >>> cells = polygon_to_cells(sf_coords, resolution=8)
        >>> print(f"Polygon covered by {len(cells)} H3 cells")
        Polygon covered by 42 H3 cells
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not 0 <= resolution <= 15:
        raise ValueError(f"Resolution {resolution} must be between 0 and 15")
    
    # Handle different input formats
    if isinstance(polygon_coords, dict):
        # GeoJSON geometry object
        geojson_geom = polygon_coords
    else:
        # List of coordinate tuples
        if not polygon_coords:
            return []
        
        # Convert coordinates to GeoJSON format
        if geo_json_format:
            # Already in [lng, lat] format
            coords = polygon_coords
        else:
            # Convert from (lat, lng) to [lng, lat]
            coords = [[lng, lat] for lat, lng in polygon_coords]
        
        # Ensure polygon is closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        
        geojson_geom = {
            "type": "Polygon",
            "coordinates": [coords]
        }
    
    try:
        return list(h3.geo_to_cells(geojson_geom, resolution))
    except Exception as e:
        logger.error(f"Failed to convert polygon to H3 cells: {e}")
        raise


def cells_to_polygon(h3_indices: List[str]) -> List[Tuple[float, float]]:
    """
    Convert H3 cells to polygon boundary (convex hull approximation).
    
    Args:
        h3_indices: List of H3 cell indices
        
    Returns:
        List of (lat, lng) coordinates forming polygon boundary
        
    Example:
        >>> cells = grid_disk('89283082e3fffff', k=1)
        >>> boundary = cells_to_polygon(cells)
        >>> print(f"Boundary has {len(boundary)} vertices")
        Boundary has 12 vertices
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3_indices:
        return []
    
    # Validate indices
    invalid_indices = [idx for idx in h3_indices if not h3.is_valid_cell(idx)]
    if invalid_indices:
        raise ValueError(f"Invalid H3 cell indices: {invalid_indices[:5]}...")
    
    try:
        # Get all boundary points from all cells
        all_points = []
        for h3_index in h3_indices:
            boundary = cell_to_boundary(h3_index)
            all_points.extend(boundary)
        
        if not all_points:
            return []
        
        # Simple convex hull using gift wrapping algorithm
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
        
        # Find convex hull
        points = list(set(all_points))  # Remove duplicates
        points = sorted(points)
        
        if len(points) <= 1:
            return points
        
        # Build lower hull
        lower = []
        for p in points:
            while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
                lower.pop()
            lower.append(p)
        
        # Build upper hull
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
                upper.pop()
            upper.append(p)
        
        # Remove last point of each half because it's repeated
        return lower[:-1] + upper[:-1]
        
    except Exception as e:
        logger.error(f"Failed to convert H3 cells to polygon: {e}")
        raise


def cell_area(h3_index: str, unit: str = 'km^2') -> float:
    """
    Get area of H3 cell.
    
    Args:
        h3_index: H3 cell index
        unit: Area unit ('km^2', 'm^2', or 'rads^2')
        
    Returns:
        Cell area in specified unit
        
    Example:
        >>> area = cell_area('89283082e3fffff', 'km^2')
        >>> print(f"Cell area: {area:.6f} km²")
        Cell area: 0.105332 km²
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    valid_units = ['km^2', 'm^2', 'rads^2']
    if unit not in valid_units:
        raise ValueError(f"Unit must be one of {valid_units}, got '{unit}'")
    
    try:
        return h3.cell_area(h3_index, unit)
    except Exception as e:
        logger.error(f"Failed to get area of H3 cell {h3_index}: {e}")
        raise


def cells_area(h3_indices: List[str], unit: str = 'km^2') -> float:
    """
    Get total area of multiple H3 cells.
    
    Args:
        h3_indices: List of H3 cell indices
        unit: Area unit ('km^2', 'm^2', or 'rads^2')
        
    Returns:
        Total area of all cells in specified unit
        
    Example:
        >>> cells = grid_disk('89283082e3fffff', k=1)
        >>> total_area = cells_area(cells, 'km^2')
        >>> print(f"Total area: {total_area:.6f} km²")
        Total area: 0.737324 km²
    """
    if not h3_indices:
        return 0.0
    
    total_area = 0.0
    for h3_index in h3_indices:
        try:
            total_area += cell_area(h3_index, unit)
        except Exception as e:
            logger.warning(f"Skipping invalid cell {h3_index}: {e}")
            continue
    
    return total_area


# Analysis Operations

def neighbor_cells(h3_index: str) -> List[str]:
    """
    Get immediate neighbor cells (k=1 ring, excluding center).
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        List of neighboring H3 cell indices
        
    Example:
        >>> neighbors = neighbor_cells('89283082e3fffff')
        >>> print(f"Cell has {len(neighbors)} neighbors")
        Cell has 6 neighbors
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    try:
        # Get k=1 ring (excludes center cell)
        return grid_ring(h3_index, 1)
    except Exception as e:
        logger.error(f"Failed to get neighbors of {h3_index}: {e}")
        raise


def cell_resolution(h3_index: str) -> int:
    """
    Get resolution of H3 cell.
    
    Args:
        h3_index: H3 cell index
        
    Returns:
        H3 resolution (0-15)
        
    Example:
        >>> resolution = cell_resolution('89283082e3fffff')
        >>> print(f"Cell resolution: {resolution}")
        Cell resolution: 9
    """
    if not H3_AVAILABLE:
        raise ImportError("h3-py package required. Install with 'pip install h3'")
    
    if not h3.is_valid_cell(h3_index):
        raise ValueError(f"Invalid H3 cell index: {h3_index}")
    
    try:
        return h3.get_resolution(h3_index)
    except Exception as e:
        logger.error(f"Failed to get resolution of {h3_index}: {e}")
        raise


def is_valid_cell(h3_index: str) -> bool:
    """
    Check if H3 cell index is valid.
    
    Args:
        h3_index: H3 cell index to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> valid = is_valid_cell('89283082e3fffff')
        >>> print(f"Valid: {valid}")
        Valid: True
    """
    if not H3_AVAILABLE:
        return False
    
    try:
        return h3.is_valid_cell(h3_index)
    except Exception:
        return False


def are_neighbor_cells(h3_index1: str, h3_index2: str) -> bool:
    """
    Check if two H3 cells are neighbors.
    
    Args:
        h3_index1: First H3 cell index
        h3_index2: Second H3 cell index
        
    Returns:
        True if cells are neighbors, False otherwise
        
    Example:
        >>> neighbors = are_neighbor_cells('89283082e3fffff', '89283082e7fffff')
        >>> print(f"Are neighbors: {neighbors}")
        Are neighbors: True
    """
    if not H3_AVAILABLE:
        return False
    
    if not (is_valid_cell(h3_index1) and is_valid_cell(h3_index2)):
        return False
    
    try:
        return h3.are_neighbor_cells(h3_index1, h3_index2)
    except Exception:
        return False


# Advanced Operations

def cells_intersection(cells1: List[str], cells2: List[str]) -> List[str]:
    """
    Find intersection of two sets of H3 cells.
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        List of H3 cell indices in both sets
        
    Example:
        >>> set1 = grid_disk('89283082e3fffff', k=1)
        >>> set2 = grid_disk('89283082e7fffff', k=1)
        >>> intersection = cells_intersection(set1, set2)
        >>> print(f"Intersection has {len(intersection)} cells")
        Intersection has 2 cells
    """
    set1 = set(cells1)
    set2 = set(cells2)
    return list(set1.intersection(set2))


def cells_union(cells1: List[str], cells2: List[str]) -> List[str]:
    """
    Find union of two sets of H3 cells.
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        List of H3 cell indices in either set (no duplicates)
        
    Example:
        >>> set1 = grid_disk('89283082e3fffff', k=1)
        >>> set2 = grid_disk('89283082e7fffff', k=1)
        >>> union = cells_union(set1, set2)
        >>> print(f"Union has {len(union)} cells")
        Union has 12 cells
    """
    set1 = set(cells1)
    set2 = set(cells2)
    return list(set1.union(set2))


def cells_difference(cells1: List[str], cells2: List[str]) -> List[str]:
    """
    Find difference of two sets of H3 cells (cells1 - cells2).
    
    Args:
        cells1: First set of H3 cell indices
        cells2: Second set of H3 cell indices
        
    Returns:
        List of H3 cell indices in cells1 but not in cells2
        
    Example:
        >>> set1 = grid_disk('89283082e3fffff', k=1)
        >>> set2 = grid_disk('89283082e7fffff', k=1)
        >>> difference = cells_difference(set1, set2)
        >>> print(f"Difference has {len(difference)} cells")
        Difference has 5 cells
    """
    set1 = set(cells1)
    set2 = set(cells2)
    return list(set1.difference(set2))


def grid_statistics(h3_indices: List[str]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics for a set of H3 cells.
    
    Args:
        h3_indices: List of H3 cell indices
        
    Returns:
        Dictionary with grid statistics
        
    Example:
        >>> cells = grid_disk('89283082e3fffff', k=2)
        >>> stats = grid_statistics(cells)
        >>> print(f"Grid has {stats['cell_count']} cells covering {stats['total_area_km2']:.2f} km²")
        Grid has 19 cells covering 2.00 km²
    """
    if not h3_indices:
        return {
            'cell_count': 0,
            'total_area_km2': 0.0,
            'resolutions': [],
            'bounds': None
        }
    
    # Filter valid cells
    valid_cells = [idx for idx in h3_indices if is_valid_cell(idx)]
    
    if not valid_cells:
        return {
            'cell_count': 0,
            'valid_cells': 0,
            'invalid_cells': len(h3_indices),
            'total_area_km2': 0.0,
            'resolutions': [],
            'bounds': None
        }
    
    # Calculate statistics
    resolutions = []
    coordinates = []
    total_area = 0.0
    
    for h3_index in valid_cells:
        try:
            # Get resolution
            res = cell_resolution(h3_index)
            resolutions.append(res)
            
            # Get coordinates
            lat, lng = cell_to_coordinates(h3_index)
            coordinates.append((lat, lng))
            
            # Get area
            area = cell_area(h3_index, 'km^2')
            total_area += area
            
        except Exception as e:
            logger.warning(f"Failed to process cell {h3_index}: {e}")
            continue
    
    # Calculate bounds
    bounds = None
    if coordinates:
        lats, lngs = zip(*coordinates)
        bounds = {
            'min_lat': min(lats),
            'max_lat': max(lats),
            'min_lng': min(lngs),
            'max_lng': max(lngs),
            'center_lat': sum(lats) / len(lats),
            'center_lng': sum(lngs) / len(lngs)
        }
    
    # Resolution statistics
    resolution_counts = {}
    for res in resolutions:
        resolution_counts[res] = resolution_counts.get(res, 0) + 1
    
    return {
        'cell_count': len(h3_indices),
        'valid_cells': len(valid_cells),
        'invalid_cells': len(h3_indices) - len(valid_cells),
        'total_area_km2': total_area,
        'average_area_km2': total_area / len(valid_cells) if valid_cells else 0,
        'resolutions': list(set(resolutions)),
        'resolution_counts': resolution_counts,
        'bounds': bounds,
        'coordinates': coordinates
    }
