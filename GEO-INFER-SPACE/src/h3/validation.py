#!/usr/bin/env python3
"""
H3 Validation Module

Provides comprehensive validation functions for H3 geospatial operations.
Validates cells, edges, vertices, coordinates, and geometric objects.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from constants import (
    MAX_H3_RES, MIN_H3_RES, LAT_MIN, LAT_MAX, LNG_MIN, LNG_MAX,
    ERROR_MESSAGES
)


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


def is_valid_edge(edge: str) -> bool:
    """
    Check if an H3 edge index is valid.
    
    Args:
        edge: H3 edge index as string
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_edge('115283082e73ffff')
        True
        >>> is_valid_edge('invalid')
        False
    """
    return h3.is_valid_edge(edge)


def is_valid_vertex(vertex: str) -> bool:
    """
    Check if an H3 vertex index is valid.
    
    Args:
        vertex: H3 vertex index as string
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_vertex('235283082e73ffff')
        True
        >>> is_valid_vertex('invalid')
        False
    """
    return h3.is_valid_vertex(vertex)


def is_valid_latlng(lat: float, lng: float) -> bool:
    """
    Check if latitude/longitude coordinates are valid.
    
    Args:
        lat: Latitude in degrees
        lng: Longitude in degrees
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_latlng(37.7749, -122.4194)
        True
        >>> is_valid_latlng(91.0, 0.0)
        False
    """
    return (LAT_MIN <= lat <= LAT_MAX and 
            LNG_MIN <= lng <= LNG_MAX)


def is_valid_resolution(resolution: int) -> bool:
    """
    Check if an H3 resolution is valid.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_resolution(9)
        True
        >>> is_valid_resolution(20)
        False
    """
    return MIN_H3_RES <= resolution <= MAX_H3_RES


def is_valid_polygon(polygon: Dict[str, Any]) -> bool:
    """
    Check if a GeoJSON polygon is valid for H3 operations.
    
    Args:
        polygon: GeoJSON polygon dictionary
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> polygon = {'type': 'Polygon', 'coordinates': [[[...]]]}
        >>> is_valid_polygon(polygon)
        True
    """
    if not isinstance(polygon, dict):
        return False
    
    if polygon.get('type') != 'Polygon':
        return False
    
    coordinates = polygon.get('coordinates')
    if not isinstance(coordinates, list) or len(coordinates) == 0:
        return False
    
    # Check that each ring is a list of coordinate pairs
    for ring in coordinates:
        if not isinstance(ring, list) or len(ring) < 3:
            return False
        
        for coord in ring:
            if not isinstance(coord, (list, tuple)) or len(coord) != 2:
                return False
            
            lat, lng = coord
            if not is_valid_latlng(lat, lng):
                return False
    
    return True


def is_valid_geojson(geojson: Dict[str, Any]) -> bool:
    """
    Check if a GeoJSON object is valid for H3 operations.
    
    Args:
        geojson: GeoJSON dictionary
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> geojson = {'type': 'Feature', 'geometry': {...}}
        >>> is_valid_geojson(geojson)
        True
    """
    if not isinstance(geojson, dict):
        return False
    
    geojson_type = geojson.get('type')
    
    if geojson_type == 'Feature':
        geometry = geojson.get('geometry')
        if not geometry or not isinstance(geometry, dict):
            return False
        return is_valid_geojson(geometry)
    
    elif geojson_type == 'FeatureCollection':
        features = geojson.get('features')
        if not isinstance(features, list):
            return False
        return all(is_valid_geojson(feature) for feature in features)
    
    elif geojson_type == 'Polygon':
        return is_valid_polygon(geojson)
    
    elif geojson_type == 'MultiPolygon':
        coordinates = geojson.get('coordinates')
        if not isinstance(coordinates, list):
            return False
        
        for polygon_coords in coordinates:
            polygon = {'type': 'Polygon', 'coordinates': polygon_coords}
            if not is_valid_polygon(polygon):
                return False
        
        return True
    
    else:
        return False


def is_valid_wkt(wkt: str) -> bool:
    """
    Check if a WKT string is valid for H3 operations.
    
    Args:
        wkt: Well-Known Text string
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> is_valid_wkt('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))')
        True
    """
    if not isinstance(wkt, str):
        return False
    
    # Basic WKT validation - check for common patterns
    wkt_upper = wkt.upper()
    
    if 'POLYGON' in wkt_upper:
        # Check for balanced parentheses
        if wkt.count('(') != wkt.count(')'):
            return False
        
        # Check for coordinate pairs
        if 'EMPTY' not in wkt_upper:
            # Extract coordinates between parentheses
            start = wkt.find('(')
            end = wkt.rfind(')')
            if start == -1 or end == -1:
                return False
            
            coords_str = wkt[start+1:end]
            # Basic coordinate format check
            if not any(char.isdigit() for char in coords_str):
                return False
    
    return True


def validate_cell(cell: str) -> None:
    """
    Validate an H3 cell index and raise an exception if invalid.
    
    Args:
        cell: H3 cell index as string
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> validate_cell('89283082e73ffff')
        >>> validate_cell('invalid')
        ValueError: Invalid H3 cell index
    """
    if not is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])


def validate_edge(edge: str) -> None:
    """
    Validate an H3 edge index and raise an exception if invalid.
    
    Args:
        edge: H3 edge index as string
        
    Raises:
        ValueError: If edge index is invalid
        
    Example:
        >>> validate_edge('115283082e73ffff')
        >>> validate_edge('invalid')
        ValueError: Invalid H3 edge index
    """
    if not is_valid_edge(edge):
        raise ValueError(ERROR_MESSAGES['INVALID_EDGE'])


def validate_vertex(vertex: str) -> None:
    """
    Validate an H3 vertex index and raise an exception if invalid.
    
    Args:
        vertex: H3 vertex index as string
        
    Raises:
        ValueError: If vertex index is invalid
        
    Example:
        >>> validate_vertex('235283082e73ffff')
        >>> validate_vertex('invalid')
        ValueError: Invalid H3 vertex index
    """
    if not is_valid_vertex(vertex):
        raise ValueError(ERROR_MESSAGES['INVALID_VERTEX'])


def validate_latlng(lat: float, lng: float) -> None:
    """
    Validate latitude/longitude coordinates and raise an exception if invalid.
    
    Args:
        lat: Latitude in degrees
        lng: Longitude in degrees
        
    Raises:
        ValueError: If coordinates are invalid
        
    Example:
        >>> validate_latlng(37.7749, -122.4194)
        >>> validate_latlng(91.0, 0.0)
        ValueError: Invalid latitude/longitude coordinates
    """
    if not is_valid_latlng(lat, lng):
        raise ValueError(ERROR_MESSAGES['INVALID_LATLNG'])


def validate_resolution(resolution: int) -> None:
    """
    Validate an H3 resolution and raise an exception if invalid.
    
    Args:
        resolution: H3 resolution (0-15)
        
    Raises:
        ValueError: If resolution is invalid
        
    Example:
        >>> validate_resolution(9)
        >>> validate_resolution(20)
        ValueError: Invalid H3 resolution (must be 0-15)
    """
    if not is_valid_resolution(resolution):
        raise ValueError(ERROR_MESSAGES['INVALID_RESOLUTION'])


def validate_polygon(polygon: Dict[str, Any]) -> None:
    """
    Validate a GeoJSON polygon and raise an exception if invalid.
    
    Args:
        polygon: GeoJSON polygon dictionary
        
    Raises:
        ValueError: If polygon is invalid
        
    Example:
        >>> polygon = {'type': 'Polygon', 'coordinates': [[[...]]]}
        >>> validate_polygon(polygon)
        >>> validate_polygon({'invalid': 'polygon'})
        ValueError: Invalid polygon geometry
    """
    if not is_valid_polygon(polygon):
        raise ValueError(ERROR_MESSAGES['INVALID_POLYGON'])


def validate_geojson(geojson: Dict[str, Any]) -> None:
    """
    Validate a GeoJSON object and raise an exception if invalid.
    
    Args:
        geojson: GeoJSON dictionary
        
    Raises:
        ValueError: If GeoJSON is invalid
        
    Example:
        >>> geojson = {'type': 'Feature', 'geometry': {...}}
        >>> validate_geojson(geojson)
        >>> validate_geojson({'invalid': 'geojson'})
        ValueError: Invalid GeoJSON object
    """
    if not is_valid_geojson(geojson):
        raise ValueError(ERROR_MESSAGES['INVALID_GEOJSON'])


def validate_wkt(wkt: str) -> None:
    """
    Validate a WKT string and raise an exception if invalid.
    
    Args:
        wkt: Well-Known Text string
        
    Raises:
        ValueError: If WKT is invalid
        
    Example:
        >>> validate_wkt('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))')
        >>> validate_wkt('invalid')
        ValueError: Invalid WKT format
    """
    if not is_valid_wkt(wkt):
        raise ValueError(ERROR_MESSAGES['INVALID_WKT'])


def validate_cells(cells: List[str]) -> None:
    """
    Validate a list of H3 cell indices and raise an exception if any are invalid.
    
    Args:
        cells: List of H3 cell indices
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> validate_cells(['89283082e73ffff', '89283082e77ffff'])
        >>> validate_cells(['89283082e73ffff', 'invalid'])
        ValueError: Invalid H3 cell index
    """
    for cell in cells:
        validate_cell(cell)


def validate_resolution_range(resolution: int, min_res: int = MIN_H3_RES, max_res: int = MAX_H3_RES) -> None:
    """
    Validate an H3 resolution is within a specified range.
    
    Args:
        resolution: H3 resolution to validate
        min_res: Minimum allowed resolution
        max_res: Maximum allowed resolution
        
    Raises:
        ValueError: If resolution is outside the specified range
        
    Example:
        >>> validate_resolution_range(9, 0, 15)
        >>> validate_resolution_range(20, 0, 15)
        ValueError: Resolution must be between 0 and 15
    """
    if not min_res <= resolution <= max_res:
        raise ValueError(f"Resolution must be between {min_res} and {max_res}")


# Export all functions
__all__ = [
    'is_valid_cell',
    'is_valid_edge',
    'is_valid_vertex',
    'is_valid_latlng',
    'is_valid_resolution',
    'is_valid_polygon',
    'is_valid_geojson',
    'is_valid_wkt',
    'validate_cell',
    'validate_edge',
    'validate_vertex',
    'validate_latlng',
    'validate_resolution',
    'validate_polygon',
    'validate_geojson',
    'validate_wkt',
    'validate_cells',
    'validate_resolution_range'
] 