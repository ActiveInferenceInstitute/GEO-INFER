#!/usr/bin/env python3
"""
H3 Conversion Module

Provides H3 format conversion operations using H3 v4.3.0.
Functions for converting between H3 and various geospatial formats.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import h3
import numpy as np
from typing import Union, List, Tuple, Optional, Dict, Any
from .constants import (
    MAX_H3_RES, MIN_H3_RES, ERROR_MESSAGES
)


def cell_to_geojson(cell: str) -> Dict[str, Any]:
    """
    Convert H3 cell to GeoJSON Feature.
    
    Args:
        cell: H3 cell index as string
        
    Returns:
        GeoJSON Feature dictionary
        
    Raises:
        ValueError: If cell index is invalid
        
    Example:
        >>> cell_to_geojson('89283082e73ffff')
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Polygon',
                'coordinates': [[[...]]]
            },
            'properties': {
                'h3_index': '89283082e73ffff',
                'resolution': 9
            }
        }
    """
    if not h3.is_valid_cell(cell):
        raise ValueError(ERROR_MESSAGES['INVALID_CELL'])
    
    boundary = h3.cell_to_boundary(cell)
    
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [boundary]
        },
        'properties': {
            'h3_index': cell,
            'resolution': h3.get_resolution(cell)
        }
    }


def geojson_to_cells(geojson: Dict[str, Any], resolution: int) -> List[str]:
    """
    Convert GeoJSON to H3 cells.
    
    Args:
        geojson: GeoJSON dictionary
        resolution: H3 resolution (0-15)
        
    Returns:
        List of H3 cell indices
        
    Raises:
        ValueError: If GeoJSON or resolution is invalid
        
    Example:
        >>> geojson = {'type': 'Polygon', 'coordinates': [[[...]]]}
        >>> geojson_to_cells(geojson, 9)
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    if geojson.get('type') == 'Feature':
        geometry = geojson.get('geometry')
        if not geometry:
            raise ValueError("Feature must have geometry")
        return h3.polygon_to_cells(geometry, resolution)
    
    elif geojson.get('type') == 'FeatureCollection':
        features = geojson.get('features', [])
        cells = []
        for feature in features:
            cells.extend(geojson_to_cells(feature, resolution))
        return list(set(cells))  # Remove duplicates
    
    elif geojson.get('type') in ['Polygon', 'MultiPolygon']:
        return list(h3.polygon_to_cells(geojson, resolution))
    
    else:
        raise ValueError("Unsupported GeoJSON type")


def wkt_to_cells(wkt: str, resolution: int) -> List[str]:
    """
    Convert WKT string to H3 cells.
    
    Args:
        wkt: Well-Known Text string
        resolution: H3 resolution (0-15)
        
    Returns:
        List of H3 cell indices
        
    Raises:
        ValueError: If WKT or resolution is invalid
        
    Example:
        >>> wkt_to_cells('POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))', 9)
        ['89283082e73ffff', '89283082e77ffff', ...]
    """
    if not MIN_H3_RES <= resolution <= MAX_H3_RES:
        raise ValueError(f"Resolution must be between {MIN_H3_RES} and {MAX_H3_RES}")
    
    # Parse WKT to extract coordinates
    # This is a simplified implementation - in practice you'd want to use
    # a proper WKT parser like shapely
    if 'POLYGON' in wkt.upper():
        # Extract coordinates from WKT
        coords_str = wkt[wkt.find('(')+1:wkt.rfind(')')]
        coords = []
        
        # Parse coordinate pairs
        pairs = coords_str.split(',')
        for pair in pairs:
            pair = pair.strip()
            if '(' in pair:
                pair = pair[pair.find('(')+1:pair.rfind(')')]
            
            lng, lat = map(float, pair.split())
            coords.append([lat, lng])
        
        # Create GeoJSON polygon
        polygon = {
            'type': 'Polygon',
            'coordinates': [coords]
        }
        
        return list(h3.polygon_to_cells(polygon, resolution))
    
    else:
        raise ValueError("Unsupported WKT type")


def cells_to_wkt(cells: List[str]) -> str:
    """
    Convert H3 cells to WKT MultiPolygon.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        WKT MultiPolygon string
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> cells_to_wkt(['89283082e73ffff', '89283082e77ffff'])
        'MULTIPOLYGON(((...)), ((...)))'
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    polygons = []
    for cell in cells:
        boundary = h3.cell_to_boundary(cell)
        # Convert to WKT format (lng lat pairs)
        coords = [f"{lng} {lat}" for lat, lng in boundary]
        polygon_str = f"(({', '.join(coords)}))"
        polygons.append(polygon_str)
    
    return f"MULTIPOLYGON({', '.join(polygons)})"


def cells_to_geojson(cells: List[str]) -> Dict[str, Any]:
    """
    Convert H3 cells to GeoJSON FeatureCollection.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        GeoJSON FeatureCollection dictionary
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> cells_to_geojson(['89283082e73ffff', '89283082e77ffff'])
        {
            'type': 'FeatureCollection',
            'features': [...]
        }
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    features = []
    for cell in cells:
        features.append(cell_to_geojson(cell))
    
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def cells_to_shapefile_data(cells: List[str]) -> Dict[str, Any]:
    """
    Convert H3 cells to shapefile-compatible data.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        Dictionary with geometries and properties for shapefile creation
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> cells_to_shapefile_data(['89283082e73ffff'])
        {
            'geometries': [...],
            'properties': [...]
        }
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    geometries = []
    properties = []
    
    for cell in cells:
        boundary = h3.cell_to_boundary(cell)
        geometries.append({
            'type': 'Polygon',
            'coordinates': [boundary]
        })
        
        properties.append({
            'h3_index': cell,
            'resolution': h3.get_resolution(cell),
            'area_km2': h3.cell_area(cell, 'km^2'),
            'is_pentagon': h3.is_pentagon(cell),
            'is_class_iii': h3.is_class_iii(cell)
        })
    
    return {
        'geometries': geometries,
        'properties': properties
    }


def cells_to_kml(cells: List[str]) -> str:
    """
    Convert H3 cells to KML format.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        KML string
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> cells_to_kml(['89283082e73ffff'])
        '<?xml version="1.0" encoding="UTF-8"?>...'
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    kml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        '<Document>',
        '<name>H3 Cells</name>'
    ]
    
    for i, cell in enumerate(cells):
        boundary = h3.cell_to_boundary(cell)
        
        # Create KML Placemark
        kml_parts.extend([
            f'<Placemark>',
            f'<name>H3 Cell {i+1}</name>',
            f'<description>',
            f'H3 Index: {cell}<br/>',
            f'Resolution: {h3.get_resolution(cell)}<br/>',
            f'Area: {h3.cell_area(cell, "km^2"):.6f} km²',
            f'</description>',
            f'<Polygon>',
            f'<outerBoundaryIs>',
            f'<LinearRing>',
            f'<coordinates>'
        ])
        
        # Add coordinates (lng,lat,alt format for KML)
        coords = [f"{lng},{lat},0" for lat, lng in boundary]
        kml_parts.append(' '.join(coords))
        
        kml_parts.extend([
            f'</coordinates>',
            f'</LinearRing>',
            f'</outerBoundaryIs>',
            f'</Polygon>',
            f'</Placemark>'
        ])
    
    kml_parts.extend([
        '</Document>',
        '</kml>'
    ])
    
    return '\n'.join(kml_parts)


def cells_to_csv(cells: List[str]) -> str:
    """
    Convert H3 cells to CSV format.
    
    Args:
        cells: List of H3 cell indices
        
    Returns:
        CSV string with cell information
        
    Raises:
        ValueError: If any cell is invalid
        
    Example:
        >>> cells_to_csv(['89283082e73ffff'])
        'h3_index,resolution,center_lat,center_lng,area_km2,is_pentagon\n...'
    """
    if not all(h3.is_valid_cell(cell) for cell in cells):
        raise ValueError("All cells must be valid")
    
    csv_lines = [
        'h3_index,resolution,center_lat,center_lng,area_km2,is_pentagon,is_class_iii'
    ]
    
    for cell in cells:
        center_lat, center_lng = h3.cell_to_latlng(cell)
        csv_lines.append(
            f'{cell},{h3.get_resolution(cell)},{center_lat},{center_lng},'
            f'{h3.cell_area(cell, "km^2")},{h3.is_pentagon(cell)},{h3.is_class_iii(cell)}'
        )
    
    return '\n'.join(csv_lines)


# Re-export core functions for convenience
from .core import latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_to_polygon, polygon_to_cells, polyfill


# Export all functions
__all__ = [
    'latlng_to_cell',
    'cell_to_latlng',
    'cell_to_boundary',
    'cell_to_polygon',
    'polygon_to_cells',
    'polyfill',
    'cell_to_geojson',
    'geojson_to_cells',
    'wkt_to_cells',
    'cells_to_wkt',
    'cells_to_geojson',
    'cells_to_shapefile_data',
    'cells_to_kml',
    'cells_to_csv'
] 