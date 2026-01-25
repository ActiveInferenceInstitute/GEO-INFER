#!/usr/bin/env python3
"""
H3 Operations Module for GEO-INFER-PLACE

Provides unified H3 v4 geospatial operations for the entire module.
All H3 functions are consolidated here to avoid duplication across files.

Usage:
    from geo_infer_place.utils.h3_operations import (
        latlng_to_cell,
        cell_to_latlng,
        polygon_to_cells,
    )
"""

import logging
from typing import List, Tuple, Any, Dict, Union

import h3

logger = logging.getLogger(__name__)

# ============================================================================
# Core H3 v4 Operations
# ============================================================================


def latlng_to_cell(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude coordinates to an H3 cell index.
    
    Args:
        lat: Latitude in degrees
        lng: Longitude in degrees
        resolution: H3 resolution (0-15)
    
    Returns:
        H3 cell index as string
    """
    return h3.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(cell: str) -> Tuple[float, float]:
    """
    Get the center coordinates of an H3 cell.
    
    Args:
        cell: H3 cell index
    
    Returns:
        Tuple of (latitude, longitude)
    """
    return h3.cell_to_latlng(cell)


def cell_to_latlng_boundary(cell: str) -> List[Tuple[float, float]]:
    """
    Get the boundary vertices of an H3 cell.
    
    Args:
        cell: H3 cell index
    
    Returns:
        List of (lat, lng) tuples forming the cell boundary
    """
    return h3.cell_to_boundary(cell)


def geo_to_cells(geojson: Dict[str, Any], resolution: int) -> List[str]:
    """
    Convert a GeoJSON polygon to a set of H3 cells.
    
    Args:
        geojson: GeoJSON polygon geometry
        resolution: H3 resolution
    
    Returns:
        List of H3 cell indices
    """
    return list(h3.geo_to_cells(geojson, resolution))


def polygon_to_cells(polygon: Any, resolution: int) -> List[str]:
    """
    Convert a Shapely polygon to H3 cells.
    
    Args:
        polygon: Shapely Polygon or GeoJSON dict
        resolution: H3 resolution
    
    Returns:
        List of H3 cell indices
    """
    if hasattr(polygon, '__geo_interface__'):
        geojson = polygon.__geo_interface__
    elif isinstance(polygon, dict):
        geojson = polygon
    else:
        raise ValueError(f"Unsupported polygon type: {type(polygon)}")
    
    return list(h3.geo_to_cells(geojson, resolution))


# ============================================================================
# Grid Operations
# ============================================================================


def grid_disk(cell: str, k: int = 1) -> List[str]:
    """
    Get all cells within k grid distance of the origin cell.
    
    Args:
        cell: Origin H3 cell index
        k: Distance (number of rings)
    
    Returns:
        List of H3 cell indices in the disk
    """
    return list(h3.grid_disk(cell, k))


def grid_distance(cell1: str, cell2: str) -> int:
    """
    Get the grid distance between two H3 cells.
    
    Args:
        cell1: First H3 cell index
        cell2: Second H3 cell index
    
    Returns:
        Grid distance (number of cells)
    """
    return h3.grid_distance(cell1, cell2)


def grid_ring(cell: str, k: int) -> List[str]:
    """
    Get cells at exactly k grid distance from origin.
    
    Args:
        cell: Origin H3 cell index
        k: Distance (ring number)
    
    Returns:
        List of H3 cell indices in the ring
    """
    return list(h3.grid_ring(cell, k))


# ============================================================================
# Cell Properties
# ============================================================================


def cell_area(cell: str, unit: str = 'km^2') -> float:
    """
    Get the area of an H3 cell.
    
    Args:
        cell: H3 cell index
        unit: Area unit ('km^2' or 'm^2')
    
    Returns:
        Cell area in specified units
    """
    return h3.cell_area(cell, unit=unit)


def get_resolution(cell: str) -> int:
    """
    Get the resolution of an H3 cell.
    
    Args:
        cell: H3 cell index
    
    Returns:
        Resolution (0-15)
    """
    return h3.get_resolution(cell)


def is_valid_cell(cell: str) -> bool:
    """
    Check if a string is a valid H3 cell index.
    
    Args:
        cell: H3 cell index to validate
    
    Returns:
        True if valid, False otherwise
    """
    return h3.is_valid_cell(cell)


def are_neighbor_cells(cell1: str, cell2: str) -> bool:
    """
    Check if two H3 cells are neighbors.
    
    Args:
        cell1: First H3 cell index
        cell2: Second H3 cell index
    
    Returns:
        True if cells are neighbors
    """
    return h3.are_neighbor_cells(cell1, cell2)


def get_base_cell_number(cell: str) -> int:
    """
    Get the base cell number of an H3 index.
    
    Args:
        cell: H3 cell index
    
    Returns:
        Base cell number (0-121)
    """
    return h3.get_base_cell_number(cell)


# ============================================================================
# Hierarchical Operations
# ============================================================================


def cell_to_parent(cell: str, parent_res: int) -> str:
    """
    Get the parent cell at a coarser resolution.
    
    Args:
        cell: H3 cell index
        parent_res: Parent resolution (must be less than cell's resolution)
    
    Returns:
        Parent H3 cell index
    """
    return h3.cell_to_parent(cell, parent_res)


def cell_to_children(cell: str, child_res: int) -> List[str]:
    """
    Get all child cells at a finer resolution.
    
    Args:
        cell: H3 cell index
        child_res: Child resolution (must be greater than cell's resolution)
    
    Returns:
        List of child H3 cell indices
    """
    return list(h3.cell_to_children(cell, child_res))


def compact_cells(cells: List[str]) -> List[str]:
    """
    Compact a set of cells to their most compact representation.
    
    Args:
        cells: List of H3 cell indices
    
    Returns:
        Compacted list of H3 cell indices
    """
    return list(h3.compact_cells(cells))


def uncompact_cells(cells: List[str], resolution: int) -> List[str]:
    """
    Uncompact cells to a specified resolution.
    
    Args:
        cells: Compacted list of H3 cell indices
        resolution: Target resolution
    
    Returns:
        Uncompacted list of H3 cell indices
    """
    return list(h3.uncompact_cells(cells, resolution))


# ============================================================================
# Utility Functions
# ============================================================================


def cells_to_geodataframe(cells: List[str]) -> 'gpd.GeoDataFrame':
    """
    Convert a list of H3 cells to a GeoDataFrame with polygon geometries.
    
    Args:
        cells: List of H3 cell indices
    
    Returns:
        GeoDataFrame with cell polygons
    """
    import geopandas as gpd
    from shapely.geometry import Polygon
    
    geometries = []
    for cell in cells:
        boundary = cell_to_latlng_boundary(cell)
        # H3 returns (lat, lng) but Shapely needs (lng, lat)
        polygon = Polygon([(lng, lat) for lat, lng in boundary])
        geometries.append(polygon)
    
    return gpd.GeoDataFrame(
        {'h3_cell': cells},
        geometry=geometries,
        crs='EPSG:4326'
    )


def estimate_cell_count(area_km2: float, resolution: int) -> int:
    """
    Estimate the number of H3 cells to cover an area.
    
    Args:
        area_km2: Area in square kilometers
        resolution: H3 resolution
    
    Returns:
        Estimated number of cells
    """
    avg_cell_area = h3.average_hexagon_area(resolution, unit='km^2')
    return max(1, int(area_km2 / avg_cell_area))


logger.debug("H3 operations module initialized with H3 v4 API")
