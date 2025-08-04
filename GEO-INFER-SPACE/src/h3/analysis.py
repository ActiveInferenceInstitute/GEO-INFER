#!/usr/bin/env python3
"""
H3 Analysis Module

Provides H3 analytical operations using H3 v4.3.0.
Functions for spatial analysis, statistics, and geometric calculations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, ERROR_MESSAGES, H3_AREA_KM2, H3_EDGE_LENGTH_KM
)
from core import is_class_iii, is_res_class_iii, cell_perimeter
from traversal import great_circle_distance


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
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3.cell_area(cell, unit=unit)


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
    
    return h3.edge_length(resolution, unit=unit)


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
    
    return h3.num_cells(resolution)


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
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
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
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return h3.is_pentagon(cell)


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
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
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
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
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
        raise ValueError(ERROR_MESSAGES['INVALID_EDGE'])
    
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
        raise ValueError(ERROR_MESSAGES['INVALID_VERTEX'])
    
    return h3.vertex_to_latlng(vertex)


def analyze_cell_distribution(cells: List[str]) -> Dict[str, Any]:
    """
    Analyze the distribution of H3 cells.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        Dictionary with distribution analysis
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> analyze_cell_distribution(['89283082e73ffff', '89283082e77ffff'])
        {
            'total_cells': 2,
            'resolutions': {9: 2},
            'pentagons': 0,
            'class_iii_cells': 2,
            'total_area_km2': 0.210665,
            'avg_area_km2': 0.1053325
        }
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    resolutions = {}
    pentagons = 0
    class_iii_cells = 0
    total_area = 0.0
    
    for cell in cells:
        if not h3.is_valid_cell(cell):
            continue
        res = h3.get_resolution(cell)
        resolutions[res] = resolutions.get(res, 0) + 1
        
        if h3.is_pentagon(cell):
            pentagons += 1
        
        if is_class_iii(cell):
            class_iii_cells += 1
        
        total_area += h3.cell_area(cell, 'km^2')
    
    return {
        'total_cells': len(cells),
        'resolutions': resolutions,
        'pentagons': pentagons,
        'class_iii_cells': class_iii_cells,
        'total_area_km2': total_area,
        'avg_area_km2': total_area / len(cells) if cells else 0.0
    }


def calculate_spatial_statistics(cells: List[str]) -> Dict[str, Any]:
    """
    Calculate spatial statistics for a set of H3 cells.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        Dictionary with spatial statistics
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> calculate_spatial_statistics(['89283082e73ffff'])
        {
            'centroid': (37.7749, -122.4194),
            'total_area_km2': 0.1053325,
            'total_perimeter_km': 0.174375668,
            'compactness': 0.9069
        }
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    if not cells:
        return {
            'centroid': None,
            'total_area_km2': 0.0,
            'total_perimeter_km': 0.0,
            'compactness': 0.0
        }
    
    # Calculate centroid (average of cell centers)
    centers = [h3.cell_to_latlng(cell) for cell in cells]
    avg_lat = np.mean([lat for lat, lng in centers])
    avg_lng = np.mean([lng for lat, lng in centers])
    
    # Calculate total area and perimeter
    total_area = sum(h3.cell_area(cell, 'km^2') for cell in cells)
    total_perimeter = sum(cell_perimeter(cell, 'km') for cell in cells)
    
    # Calculate compactness (isoperimetric ratio)
    # For a perfect circle, compactness = 1.0
    # For hexagons, compactness ≈ 0.9069
    compactness = (4 * np.pi * total_area) / (total_perimeter ** 2) if total_perimeter > 0 else 0.0
    
    return {
        'centroid': (avg_lat, avg_lng),
        'total_area_km2': total_area,
        'total_perimeter_km': total_perimeter,
        'compactness': compactness
    }


def find_nearest_cell(target_lat: float, target_lng: float, cells: List[str]) -> Tuple[str, float]:
    """
    Find the nearest H3 cell to a given point.
    
    Args:
        target_lat: Target latitude in degrees
        target_lng: Target longitude in degrees
        cells: List of H3 cell indices to search
        
    Returns:
        Tuple of (nearest_cell, distance_km)
        
    Raises:
        ValueError: If any cell is invalid or no cells provided
        
    Example:
        >>> find_nearest_cell(37.7749, -122.4194, ['89283082e73ffff'])
        ('89283082e73ffff', 0.0)
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    if not cells:
        raise ValueError("No cells provided")
    
    min_distance = float('inf')
    nearest_cell = None
    
    for cell in cells:
        cell_lat, cell_lng = h3.cell_to_latlng(cell)
        distance = great_circle_distance(target_lat, target_lng, cell_lat, cell_lng, unit='km')
        
        if distance < min_distance:
            min_distance = distance
            nearest_cell = cell
    
    return nearest_cell, min_distance


def calculate_cell_density(cells: List[str], area_km2: float = None) -> float:
    """
    Calculate the density of H3 cells in a given area.
    
    Args:
        cells: List of H3 cell indices
        area_km2: Area in km² (if None, uses total cell area)
        
    Returns:
        Cell density (cells per km²)
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> calculate_cell_density(['89283082e73ffff'])
        9.4934
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    if area_km2 is None:
        # Use total area of all cells
        area_km2 = sum(h3.cell_area(cell, 'km^2') for cell in cells)
    
    if area_km2 <= 0:
        return 0.0
    
    return len(cells) / area_km2


def analyze_resolution_distribution(cells: List[str]) -> Dict[str, Any]:
    """
    Analyze the resolution distribution of H3 cells.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        Dictionary with resolution analysis
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> analyze_resolution_distribution(['89283082e73ffff'])
        {
            'resolution_counts': {9: 1},
            'min_resolution': 9,
            'max_resolution': 9,
            'avg_resolution': 9.0,
            'resolution_std': 0.0
        }
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    resolutions = [h3.get_resolution(cell) for cell in cells]
    
    if not resolutions:
        return {
            'resolution_counts': {},
            'min_resolution': None,
            'max_resolution': None,
            'avg_resolution': 0.0,
            'resolution_std': 0.0
        }
    
    resolution_counts = {}
    for res in resolutions:
        resolution_counts[res] = resolution_counts.get(res, 0) + 1
    
    return {
        'resolution_counts': resolution_counts,
        'min_resolution': min(resolutions),
        'max_resolution': max(resolutions),
        'avg_resolution': np.mean(resolutions),
        'resolution_std': np.std(resolutions)
    }


# Export all functions
__all__ = [
    'cell_area',
    'edge_length',
    'num_cells',
    'get_resolution',
    'is_valid_cell',
    'is_pentagon',
    'is_class_iii',
    'is_res_class_iii',
    'get_base_cell_number',
    'get_icosahedron_faces',
    'get_cell_edge_boundary',
    'get_cell_vertex_boundary',
    'analyze_cell_distribution',
    'calculate_spatial_statistics',
    'find_nearest_cell',
    'calculate_cell_density',
    'analyze_resolution_distribution'
] 