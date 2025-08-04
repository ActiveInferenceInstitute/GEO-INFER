#!/usr/bin/env python3
"""
H3 Utilities Module

Provides utility functions for H3 geospatial operations using H3 v4.3.0.
Helper functions for common operations and calculations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, H3_AREA_KM2, H3_EDGE_LENGTH_KM,
    H3_NUM_CELLS, H3_PENTAGONS, H3_CLASS_III_RESOLUTIONS
)


def get_hexagon_area_avg(resolution: int, unit: str = 'km^2') -> float:
    """
    Get the average area of hexagons at a given resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        unit: Area unit ('km^2', 'm^2', 'rads^2')
        
    Returns:
        Average hexagon area in specified units
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> get_hexagon_area_avg(9, 'km^2')
        0.1053325
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.get_hexagon_area_avg(resolution, unit=unit)


def get_hexagon_edge_length_avg(resolution: int, unit: str = 'km') -> float:
    """
    Get the average edge length of hexagons at a given resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        unit: Length unit ('km', 'm', 'rads')
        
    Returns:
        Average edge length in specified units
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> get_hexagon_edge_length_avg(9, 'km')
        0.174375668
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.get_hexagon_edge_length_avg(resolution, unit=unit)


def get_num_cells(resolution: int) -> int:
    """
    Get the number of H3 cells at a given resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        Number of cells at the resolution
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> get_num_cells(9)
        4842432842
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.num_cells(resolution)


def get_pentagons(resolution: int) -> List[str]:
    """
    Get all pentagon cells at a given resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        List of pentagon cell indices
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> get_pentagons(0)
        ['8001fffffffffff', '8003fffffffffff', ...]
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return list(h3.get_pentagons(resolution))


def get_res0_cells() -> List[str]:
    """
    Get all resolution 0 H3 cells.
    
    Returns:
        List of all resolution 0 cell indices
        
    Example:
        >>> get_res0_cells()
        ['8001fffffffffff', '8003fffffffffff', ...]
    """
    return list(h3.get_res0_cells())


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
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return h3.get_resolution(cell)


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
    return h3.is_valid_cell(cell)


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
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return h3.is_pentagon(cell)


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
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return h3.is_class_iii(cell)


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
    
    return h3.is_res_class_iii(resolution)


def get_base_cell_number(cell: str) -> int:
    """
    Get the base cell number of an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        Base cell number (0-121)
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_base_cell_number('89283082e73ffff')
        0
    """
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return h3.get_base_cell_number(cell)


def get_icosahedron_faces(cell: str) -> List[int]:
    """
    Get the icosahedron faces that an H3 cell intersects.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of icosahedron face numbers (0-19)
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_icosahedron_faces('89283082e73ffff')
        [0]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return list(h3.get_icosahedron_faces(cell))


def get_cell_edge_boundary(edge: str) -> List[Tuple[float, float]]:
    """
    Get the boundary coordinates of an H3 edge.
    
    Args:
        edge: H3 edge index as string
        
    Returns:
        List of coordinate tuples defining the edge boundary
        
    Raises:
        ValueError: If edge index is invalid
        
    Example:
        >>> get_cell_edge_boundary('115283082e73ffff')
        [(37.7749, -122.4194), (37.7749, -122.4194)]
    """
    if not h3.is_valid_edge(edge):
        raise ValueError("Invalid H3 edge index")
    
    return list(h3.edge_boundary(edge))


def get_cell_vertex_boundary(vertex: str) -> Tuple[float, float]:
    """
    Get the coordinates of an H3 vertex.
    
    Args:
        vertex: H3 vertex index as string
        
    Returns:
        Vertex coordinates as (lat, lng) tuple
        
    Raises:
        ValueError: If vertex index is invalid
        
    Example:
        >>> get_cell_vertex_boundary('235283082e73ffff')
        (37.7749, -122.4194)
    """
    if not h3.is_valid_vertex(vertex):
        raise ValueError("Invalid H3 vertex index")
    
    return h3.vertex_to_latlng(vertex)


def get_resolution_info(resolution: int) -> Dict[str, Any]:
    """
    Get comprehensive information about an H3 resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        Dictionary with resolution information
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> get_resolution_info(9)
        {
            'resolution': 9,
            'num_cells': 4842432842,
            'avg_area_km2': 0.1053325,
            'avg_edge_length_km': 0.174375668,
            'is_class_iii': True,
            'num_pentagons': 12
        }
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return {
        'resolution': resolution,
        'num_cells': get_num_cells(resolution),
        'avg_area_km2': get_hexagon_area_avg(resolution, 'km^2'),
        'avg_edge_length_km': get_hexagon_edge_length_avg(resolution, 'km'),
        'is_class_iii': is_res_class_iii(resolution),
        'num_pentagons': len(get_pentagons(resolution))
    }


def get_cell_info(cell: str) -> Dict[str, Any]:
    """
    Get comprehensive information about an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        Dictionary with cell information
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_cell_info('89283082e73ffff')
        {
            'cell': '89283082e73ffff',
            'resolution': 9,
            'base_cell': 0,
            'is_pentagon': False,
            'is_class_iii': True,
            'area_km2': 0.1053325,
            'perimeter_km': 0.174375668,
            'center': (37.7749, -122.4194),
            'icosahedron_faces': [0]
        }
    """
    if not h3.is_valid_cell(cell):
        raise ValueError("Invalid H3 cell index")
    
    return {
        'cell': cell,
        'resolution': get_resolution(cell),
        'base_cell': get_base_cell_number(cell),
        'is_pentagon': is_pentagon(cell),
        'is_class_iii': is_class_iii(cell),
        'area_km2': h3.cell_area(cell, 'km^2'),
        'perimeter_km': h3.cell_perimeter(cell, 'km'),
        'center': h3.cell_to_latlng(cell),
        'icosahedron_faces': get_icosahedron_faces(cell)
    }


def get_resolution_comparison(res1: int, res2: int) -> Dict[str, Any]:
    """
    Compare two H3 resolutions.
    
    Args:
        res1: First H3 resolution (0-15)
        res2: Second H3 resolution (0-15)
        
    Returns:
        Dictionary with comparison information
        
    Raises:
        ValueError: If either resolution is invalid
        
    Example:
        >>> get_resolution_comparison(9, 10)
        {
            'res1': {...},
            'res2': {...},
            'area_ratio': 7.0,
            'edge_length_ratio': 2.6457513110645907,
            'cell_count_ratio': 7.0
        }
    """
    if not MIN_H3_RES <= res1 <= MAX_H3_RES:
        raise ValueError(f"First resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    if not MIN_H3_RES <= res2 <= MAX_H3_RES:
        raise ValueError(f"Second resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    info1 = get_resolution_info(res1)
    info2 = get_resolution_info(res2)
    
    return {
        'res1': info1,
        'res2': info2,
        'area_ratio': info1['avg_area_km2'] / info2['avg_area_km2'],
        'edge_length_ratio': info1['avg_edge_length_km'] / info2['avg_edge_length_km'],
        'cell_count_ratio': info1['num_cells'] / info2['num_cells']
    }


# Export all functions
__all__ = [
    'get_hexagon_area_avg',
    'get_hexagon_edge_length_avg',
    'get_num_cells',
    'get_pentagons',
    'get_res0_cells',
    'get_resolution',
    'is_valid_cell',
    'is_pentagon',
    'is_class_iii',
    'is_res_class_iii',
    'get_base_cell_number',
    'get_icosahedron_faces',
    'get_cell_edge_boundary',
    'get_cell_vertex_boundary',
    'get_resolution_info',
    'get_cell_info',
    'get_resolution_comparison'
] 