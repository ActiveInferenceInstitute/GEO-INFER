#!/usr/bin/env python3
"""
H3 Geospatial Operations Package

Provides comprehensive H3 geospatial operations using H3 v4.3.0.
Core functions for cell indexing, coordinate conversion, and geometric operations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

from .core import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_boundary,
    cell_to_polygon,
    polygon_to_cells,
    polyfill,
    cell_area,
    cell_perimeter,
    edge_length,
    num_cells,
    get_resolution,
    is_valid_cell,
    is_pentagon,
    is_class_iii,
    is_res_class_iii
)

__version__ = "4.3.0"
__author__ = "GEO-INFER Framework"
__license__ = "Apache-2.0"

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