#!/usr/bin/env python3
"""
H3 Grid Traversal Module

Provides H3 grid traversal operations using H3 v4.3.0.
Functions for disk/ring traversal, path finding, and distance calculations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, ERROR_MESSAGES, WGS84_EARTH_RADIUS_KM
)


def grid_disk(cell: str, k: int) -> List[str]:
    """
    Get all H3 cells within k steps of a given cell.
    
    Args:
        cell: Center H3 cell index as string
        k: Number of steps from center (k >= 0)
        
    Returns:
        List of H3 cell indices within k steps
        
    Raises:
        ValueError: If cell is invalid or k is negative
        
    Example:
        >>> grid_disk('89283082e73ffff', 1)
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    if k < 0:
        raise ValueError("k must be non-negative")
    
    return list(h3.grid_disk(cell, k))


def grid_ring(cell: str, k: int) -> List[str]:
    """
    Get all H3 cells exactly k steps from a given cell.
    
    Args:
        cell: Center H3 cell index as string
        k: Number of steps from center (k >= 0)
        
    Returns:
        List of H3 cell indices exactly k steps away
        
    Raises:
        ValueError: If cell is invalid or k is negative
        
    Example:
        >>> grid_ring('89283082e73ffff', 1)
        ['89283082e77ffff', '89283082e7bffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    if k < 0:
        raise ValueError("k must be non-negative")
    
    return list(h3.grid_ring(cell, k))


def grid_path_cells(origin: str, destination: str) -> List[str]:
    """
    Get the shortest path of H3 cells between two cells.
    
    Args:
        origin: Starting H3 cell index as string
        destination: Ending H3 cell index as string
        
    Returns:
        List of H3 cell indices forming the shortest path
        
    Raises:
        ValueError: If either cell is invalid
        
    Example:
        >>> grid_path_cells('89283082e73ffff', '89283082e77ffff')
        ['89283082e73ffff', '89283082e77ffff']
    """
    if not h3.is_valid_cell(origin):
        raise ValueError("Origin cell is invalid")
    
    if not h3.is_valid_cell(destination):
        raise ValueError("Destination cell is invalid")
    
    return list(h3.grid_path_cells(origin, destination))


def grid_distance(origin: str, destination: str) -> int:
    """
    Calculate the grid distance between two H3 cells.
    
    Args:
        origin: Starting H3 cell index as string
        destination: Ending H3 cell index as string
        
    Returns:
        Grid distance (number of steps) between cells
        
    Raises:
        ValueError: If either cell is invalid
        
    Example:
        >>> grid_distance('89283082e73ffff', '89283082e77ffff')
        1
    """
    if not h3.is_valid_cell(origin):
        raise ValueError("Origin cell is invalid")
    
    if not h3.is_valid_cell(destination):
        raise ValueError("Destination cell is invalid")
    
    return h3.grid_distance(origin, destination)


def cell_to_local_ij(cell: str, origin: str) -> Tuple[int, int]:
    """
    Convert H3 cell to local i,j coordinates relative to an origin.
    
    Args:
        cell: H3 cell index as string
        origin: Origin H3 cell index as string
        
    Returns:
        Tuple of (i, j) local coordinates
        
    Raises:
        ValueError: If either cell is invalid
        
    Example:
        >>> cell_to_local_ij('89283082e77ffff', '89283082e73ffff')
        (0, 1)
    """
    if not h3.is_valid_cell(cell):
        raise ValueError("Cell is invalid")
    
    if not h3.is_valid_cell(origin):
        raise ValueError("Origin cell is invalid")
    
    return h3.cell_to_local_ij(cell, origin)


def local_ij_to_cell(origin: str, i: int, j: int) -> str:
    """
    Convert local i,j coordinates to H3 cell relative to an origin.
    
    Args:
        origin: Origin H3 cell index as string
        i: Local i coordinate
        j: Local j coordinate
        
    Returns:
        H3 cell index as string
        
    Raises:
        ValueError: If origin cell is invalid
        
    Example:
        >>> local_ij_to_cell('89283082e73ffff', 0, 1)
        '89283082e77ffff'
    """
    if not h3.is_valid_cell(origin):
        raise ValueError("Origin cell is invalid")
    
    return h3.local_ij_to_cell(origin, i, j)


def great_circle_distance(lat1: float, lng1: float, lat2: float, lng2: float, unit: str = 'km') -> float:
    """
    Calculate great circle distance between two points.
    
    Args:
        lat1: Latitude of first point in degrees
        lng1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lng2: Longitude of second point in degrees
        unit: Distance unit ('km', 'm', 'rads')
        
    Returns:
        Great circle distance in specified units
        
    Example:
        >>> great_circle_distance(37.7749, -122.4194, 40.7128, -74.0060)
        4129.0
    """
    # H3 v4 API change: great_circle_distance expects tuple coordinates
    return h3.great_circle_distance((lat1, lng1), (lat2, lng2), unit=unit)


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float, unit: str = 'km') -> float:
    """
    Calculate Haversine distance between two points.
    
    Args:
        lat1: Latitude of first point in degrees
        lng1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lng2: Longitude of second point in degrees
        unit: Distance unit ('km', 'm', 'rads')
        
    Returns:
        Haversine distance in specified units
        
    Example:
        >>> haversine_distance(37.7749, -122.4194, 40.7128, -74.0060)
        4129.0
    """
    # Convert to radians
    lat1_rad = np.radians(lat1)
    lng1_rad = np.radians(lng1)
    lat2_rad = np.radians(lat2)
    lng2_rad = np.radians(lng2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlng = lng2_rad - lng1_rad
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Convert to desired units
    if unit == 'km':
        return c * WGS84_EARTH_RADIUS_KM
    elif unit == 'm':
        return c * WGS84_EARTH_RADIUS_KM * 1000
    elif unit == 'rads':
        return c
    else:
        raise ValueError(f"Unsupported unit: {unit}")


def grid_disk_rings(cell: str, k: int) -> List[List[str]]:
    """
    Get all H3 cells within k steps of a given cell, organized by ring.
    
    Args:
        cell: Center H3 cell index as string
        k: Number of steps from center (k >= 0)
        
    Returns:
        List of lists, where each inner list contains cells at that ring distance
        
    Raises:
        ValueError: If cell is invalid or k is negative
        
    Example:
        >>> grid_disk_rings('89283082e73ffff', 2)
        [['89283082e73ffff'], ['89283082e77ffff', ...], [...]]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    if k < 0:
        raise ValueError("k must be non-negative")
    
    rings = []
    for i in range(k + 1):
        if i == 0:
            rings.append([cell])
        else:
            rings.append(list(h3.grid_ring(cell, i)))
    
    return rings


def grid_neighbors(cell: str) -> List[str]:
    """
    Get all immediate neighbors of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of neighboring H3 cell indices
        
    Raises:
        ValueError: If cell is invalid
        
    Example:
        >>> grid_neighbors('89283082e73ffff')
        ['89283082e77ffff', '89283082e7bffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return list(h3.grid_ring(cell, 1))


def grid_compact(cells: List[str]) -> List[str]:
    """
    Compact a set of H3 cells to the minimum set of parent cells.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        Compacted list of H3 cell indices
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> grid_compact(['89283082e73ffff', '89283082e77ffff'])
        ['88283082e73ffff']
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    return list(h3.compact_cells(cells))


def grid_uncompact(cells: List[str], resolution: int) -> List[str]:
    """
    Uncompact a set of H3 cells to a specific resolution.
    
    Args:
        cells: List of H3 cell indices
        resolution: Target resolution (must be >= max cell resolution)
        
    Returns:
        Uncompacted list of H3 cell indices
        
    Raises:
        ValueError: If any cell is invalid or resolution is too low
        
    Example:
        >>> grid_uncompact(['88283082e73ffff'], 9)
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    max_res = max(h3.get_resolution(cell) for cell in cells)
    if resolution < max_res:
        raise ValueError(f"Target resolution must be >= {max_res}")
    
    return list(h3.uncompact_cells(cells, resolution))


# Export all functions
__all__ = [
    'grid_disk',
    'grid_ring',
    'grid_path_cells',
    'grid_distance',
    'cell_to_local_ij',
    'local_ij_to_cell',
    'great_circle_distance',
    'haversine_distance',
    'grid_disk_rings',
    'grid_neighbors',
    'grid_compact',
    'grid_uncompact'
] 