#!/usr/bin/env python3
"""
H3 Core Operations Module

Provides fundamental H3 geospatial operations using H3 v4.3.0.
Core functions for cell indexing, coordinate conversion, and geometric operations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3 as h3_lib
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, LAT_MIN, LAT_MAX, LNG_MIN, LNG_MAX,
    ERROR_MESSAGES, H3_AREA_KM2, H3_EDGE_LENGTH_KM
)


def latlng_to_cell(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude coordinates to H3 cell index.
    
    Args:
        lat: Latitude in degrees (-90 to 90)
        lng: Longitude in degrees (-180 to 180)
        resolution: H3 resolution (0-15)
        
    Returns:
        H3 cell index as string
        
    Raises:
        ValueError: If coordinates or resolution are invalid
        
    Example:
        >>> latlng_to_cell(37.7749, -122.4194, 9)
        '89283082e73ffff'
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    if not LAT_MIN <= lat <= LAT_MAX:
        raise ValueError(f"Latitude must be between {LAT_MIN} and {LAT_MAX}")
    
    if not LNG_MIN <= lng <= LNG_MAX:
        raise ValueError(f"Longitude must be between {LNG_MIN} and {LNG_MAX}")
    
    return h3_lib.latlng_to_cell(lat, lng, resolution)


def cell_to_latlng(cell: str) -> Tuple[float, float]:
    """
    Convert H3 cell index to latitude/longitude coordinates.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        Tuple of (latitude, longitude) in degrees
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_latlng('89283082e73ffff')
        (37.7749, -122.4194)
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.cell_to_latlng(cell)


def cell_to_boundary(cell: str) -> List[Tuple[float, float]]:
    """
    Get the boundary coordinates of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of coordinate tuples defining the cell boundary
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_boundary('89283082e73ffff')
        [(37.7749, -122.4194), (37.7749, -122.4194), ...]
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return list(h3_lib.cell_to_boundary(cell))


def cell_to_polygon(cell: str) -> Dict[str, Any]:
    """
    Convert H3 cell to GeoJSON polygon.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        GeoJSON polygon dictionary
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_polygon('89283082e73ffff')
        {'type': 'Polygon', 'coordinates': [[[...]]]}
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    boundary = h3_lib.cell_to_boundary(cell)
    return {
        'type': 'Polygon',
        'coordinates': [boundary]
    }


def polygon_to_cells(polygon: Dict[str, Any], resolution: int) -> List[str]:
    """
    Convert GeoJSON polygon to H3 cells.
    
    Args:
        polygon: GeoJSON polygon dictionary
        resolution: H3 resolution (0-15)
        
    Returns:
        List of H3 cell indices
        
    Raises:
        ValueError: If polygon or resolution is invalid
        
    Example:
        >>> polygon = {'type': 'Polygon', 'coordinates': [[[...]]]}
        >>> polygon_to_cells(polygon, 9)
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    if polygon.get('type') != 'Polygon':
        raise ValueError("Input must be a GeoJSON Polygon")
    
    return list(h3_lib.polygon_to_cells(polygon, resolution))


def polyfill(polygon: Dict[str, Any], resolution: int) -> List[str]:
    """
    Fill a polygon with H3 cells (alias for polygon_to_cells).
    
    Args:
        polygon: GeoJSON polygon dictionary
        resolution: H3 resolution (0-15)
        
    Returns:
        List of H3 cell indices
        
    Raises:
        ValueError: If polygon or resolution is invalid
    """
    return polygon_to_cells(polygon, resolution)


def cell_area(cell: str, unit: str = 'km^2') -> float:
    """
    Calculate the area of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        unit: Area unit ('km^2', 'm^2', 'rads^2')
        
    Returns:
        Cell area in specified units
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_area('89283082e73ffff', 'km^2')
        0.1053325
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.cell_area(cell, unit=unit)


def cell_perimeter(cell: str, unit: str = 'km') -> float:
    """
    Calculate the perimeter of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        unit: Length unit ('km', 'm', 'rads')
        
    Returns:
        Cell perimeter in specified units
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_perimeter('89283082e73ffff', 'km')
        0.174375668
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.cell_perimeter(cell, unit=unit)


def edge_length(resolution: int, unit: str = 'km') -> float:
    """
    Get the edge length for a given H3 resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        unit: Length unit ('km', 'm', 'rads')
        
    Returns:
        Edge length in specified units
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> edge_length(9, 'km')
        0.174375668
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3_lib.edge_length(resolution, unit=unit)


def num_cells(resolution: int) -> int:
    """
    Get the number of H3 cells at a given resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        Number of cells at the resolution
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> num_cells(9)
        4842432842
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3_lib.num_cells(resolution)


def get_resolution(cell: str) -> int:
    """
    Get the resolution of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        H3 resolution (0-15)
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_resolution('89283082e73ffff')
        9
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.get_resolution(cell)


def is_valid_cell(cell: str) -> bool:
    """
    Check if an H3 cell index is valid.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_cell('89283082e73ffff')
        True
        >>> is_valid_cell('invalid')
        False
    """
    return h3_lib.is_valid_cell(cell)


def is_pentagon(cell: str) -> bool:
    """
    Check if an H3 cell is a pentagon.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        True if pentagon, False otherwise
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> is_pentagon('89283082e73ffff')
        False
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.is_pentagon(cell)


def is_class_iii(cell: str) -> bool:
    """
    Check if an H3 cell is a Class III cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        True if Class III, False otherwise
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> is_class_iii('89283082e73ffff')
        True
    """
    if not h3_lib.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3_lib.is_class_iii(cell)


def is_res_class_iii(resolution: int) -> bool:
    """
    Check if a resolution produces Class III cells.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        True if Class III resolution, False otherwise
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> is_res_class_iii(9)
        True
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3_lib.is_res_class_iii(resolution)


# Export all functions
__all__ = [
    'latlng_to_cell',
    'cell_to_latlng',
    'cell_to_boundary',
    'cell_to_polygon',
    'polygon_to_cells',
    'polyfill',
    'cell_area',
    'cell_perimeter',
    'edge_length',
    'num_cells',
    'get_resolution',
    'is_valid_cell',
    'is_pentagon',
    'is_class_iii',
    'is_res_class_iii'
] 