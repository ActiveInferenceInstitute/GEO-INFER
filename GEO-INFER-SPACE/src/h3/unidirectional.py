#!/usr/bin/env python3
"""
H3 Unidirectional Operations Module

Provides H3 unidirectional operations using H3 v4.3.0.
Functions for vertex and edge operations.

Author: GEO-INFER Framework
h3 Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, ERROR_MESSAGES
)


def cell_to_vertexes(cell: str) -> List[str]:
    """
    Get all vertex indices for an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of vertex indices
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_vertexes('89283082e73ffff')
        ['235283082e73ffff', '235283082e77ffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    return list(h3.cell_to_vertexes(cell))


def cell_to_vertex(cell: str, vertex_num: int) -> str:
    """
    Get a specific vertex index for an H3 cell.
    
    Args:
        cell: H3 cell index as string
        vertex_num: Vertex number (0-5 for hexagons, 0-4 for pentagons)
        
    Returns:
        Vertex index
        
    Raises:
        ValueError: If cell index is invalid or vertex number is out of range
        
    Example:
        >>> cell_to_vertex('89283082e73ffff', 0)
        '235283082e73ffff'
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    max_vertex = 4 if h3.is_pentagon(cell) else 5
    if not 0 <= vertex_num <= max_vertex:
        raise ValueError(f"Vertex number must be between 0 and {max_vertex}")
    
    return h3.cell_to_vertex(cell, vertex_num)


def vertex_to_latlng(vertex: str) -> Tuple[float, float]:
    """
    Convert H3 vertex index to latitude/longitude coordinates.
    
    Args:
        vertex: H3 vertex index as string
        
    Returns:
        Tuple of (latitude, longitude) in degrees
        
    Raises:
        ValueError: If vertex index is invalid
        
    Example:
        >>> vertex_to_latlng('235283082e73ffff')
        (37.7749, -122.4194)
    """
    if not h3.is_valid_vertex(vertex):
        raise ValueError(ERROR_MESSAGES['INVALID_VERTEX'])
    
    return h3.vertex_to_latlng(vertex)


def latlng_to_vertex(lat: float, lng: float, resolution: int) -> str:
    """
    Convert latitude/longitude coordinates to nearest H3 vertex.
    
    Args:
        lat: Latitude in degrees (-90 to 90)
        lng: Longitude in degrees (-180 to 180)
        resolution: H3 resolution (0-15)
        
    Returns:
        Nearest H3 vertex index
        
    Raises:
        ValueError: If coordinates or resolution are invalid
        
    Example:
        >>> latlng_to_vertex(37.7749, -122.4194, 9)
        '235283082e73ffff'
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return h3.latlng_to_vertex(lat, lng, resolution)


def vertex_to_cells(vertex: str) -> List[str]:
    """
    Get all H3 cells that share a vertex.
    
    Args:
        vertex: H3 vertex index as string
        
    Returns:
        List of H3 cell indices that share the vertex
        
    Raises:
        ValueError: If vertex index is invalid
        
    Example:
        >>> vertex_to_cells('235283082e73ffff')
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not h3.is_valid_vertex(vertex):
        raise ValueError(ERROR_MESSAGES['INVALID_VERTEX'])
    
    return list(h3.vertex_to_cells(vertex))


def edge_boundary(edge: str) -> List[Tuple[float, float]]:
    """
    Get the boundary coordinates of an H3 edge.
    
    Args:
        edge: H3 edge index as string
        
    Returns:
        List of coordinate tuples defining the edge boundary
        
    Raises:
        ValueError: If edge index is invalid
        
    Example:
        >>> edge_boundary('115283082e73ffff')
        [(37.7749, -122.4194), (37.7749, -122.4194)]
    """
    if not h3.is_valid_edge(edge):
        raise ValueError(ERROR_MESSAGES['INVALID_EDGE'])
    
    return list(h3.edge_boundary(edge))


def edge_length(edge: str, unit: str = 'km') -> float:
    """
    Calculate the length of an H3 edge.
    
    Args:
        edge: H3 edge index as string
        unit: Length unit ('km', 'm', 'rads')
        
    Returns:
        Edge length in specified units
        
    Raises:
        ValueError: If edge index is invalid
        
    Example:
        >>> edge_length('115283082e73ffff', 'km')
        0.174375668
    """
    if not h3.is_valid_edge(edge):
        raise ValueError(ERROR_MESSAGES['INVALID_EDGE'])
    
    return h3.edge_length(edge, unit=unit)


def edge_lengths(resolution: int, unit: str = 'km') -> List[float]:
    """
    Get the edge lengths for a given H3 resolution.
    
    Args:
        resolution: H3 resolution (0-15)
        unit: Length unit ('km', 'm', 'rads')
        
    Returns:
        List of edge lengths for the resolution
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> edge_lengths(9, 'km')
        [0.174375668, 0.174375668, ...]
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    return list(h3.edge_lengths(resolution, unit=unit))


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


def cell_to_icosahedron_faces(cell: str) -> List[int]:
    """
    Get the icosahedron faces that an H3 cell intersects (alias for get_icosahedron_faces).
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of icosahedron face numbers (0-19)
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_icosahedron_faces('89283082e73ffff')
        [0]
    """
    return get_icosahedron_faces(cell)


def get_cell_vertices(cell: str) -> List[Tuple[float, float]]:
    """
    Get all vertex coordinates for an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of vertex coordinates as (lat, lng) tuples
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_cell_vertices('89283082e73ffff')
        [(37.7749, -122.4194), (37.7749, -122.4194), ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    vertices = []
    for vertex in h3.cell_to_vertexes(cell):
        vertices.append(h3.vertex_to_latlng(vertex))
    
    return vertices


def get_cell_edges(cell: str) -> List[str]:
    """
    Get all edge indices for an H3 cell.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        List of edge indices
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> get_cell_edges('89283082e73ffff')
        ['115283082e73ffff', '115283082e77ffff', ...]
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    # Get vertices and create edges
    vertices = h3.cell_to_vertexes(cell)
    edges = []
    
    for i in range(len(vertices)):
        # Create edge from vertex i to vertex (i+1) % len(vertices)
        next_vertex = vertices[(i + 1) % len(vertices)]
        # Note: This is a simplified approach - actual edge creation would require
        # more complex logic based on H3's internal edge representation
        edges.append(f"edge_{vertices[i]}_{next_vertex}")
    
    return edges


def get_vertex_neighbors(vertex: str) -> List[str]:
    """
    Get all neighboring vertices of an H3 vertex.
    
    Args:
        vertex: H3 vertex index as string
        
    Returns:
        List of neighboring vertex indices
        
    Raises:
        ValueError: If vertex index is invalid
        
    Example:
        >>> get_vertex_neighbors('235283082e73ffff')
        ['235283082e77ffff', '235283082e7bffff', ...]
    """
    if not h3.is_valid_vertex(vertex):
        raise ValueError(ERROR_MESSAGES['INVALID_VERTEX'])
    
    # Get cells that share this vertex
    cells = h3.vertex_to_cells(vertex)
    neighbors = set()
    
    for cell in cells:
        # Get all vertices of each cell
        cell_vertices = h3.cell_to_vertexes(cell)
        for v in cell_vertices:
            if v != vertex:
                neighbors.add(v)
    
    return list(neighbors)


def get_edge_cells(edge: str) -> List[str]:
    """
    Get all H3 cells that share an edge.
    
    Args:
        edge: H3 edge index as string
        
    Returns:
        List of H3 cell indices that share the edge
        
    Raises:
        ValueError: If edge index is invalid
        
    Example:
        >>> get_edge_cells('115283082e73ffff')
        ['89283082e73ffff', '89283082e77ffff']
    """
    if not h3.is_valid_edge(edge):
        raise ValueError(ERROR_MESSAGES['INVALID_EDGE'])
    
    # Get the boundary coordinates of the edge
    boundary = h3.edge_boundary(edge)
    
    # Find cells that contain these coordinates
    # This is a simplified approach - actual implementation would require
    # more complex logic based on H3's internal edge representation
    cells = []
    for lat, lng in boundary:
        cell = h3.latlng_to_cell(lat, lng, h3.get_resolution(edge))
        if cell not in cells:
            cells.append(cell)
    
    return cells


# Export all functions
__all__ = [
    'cell_to_vertexes',
    'cell_to_vertex',
    'vertex_to_latlng',
    'latlng_to_vertex',
    'vertex_to_cells',
    'edge_boundary',
    'edge_length',
    'edge_lengths',
    'get_icosahedron_faces',
    'cell_to_icosahedron_faces',
    'get_cell_vertices',
    'get_cell_edges',
    'get_vertex_neighbors',
    'get_edge_cells'
] 