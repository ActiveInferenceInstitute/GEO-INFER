"""
Utility functions for GEO-INFER-SPACE.

This module provides utility functions for spatial operations,
coordinate transformations, and data processing.
"""

from .h3_utils import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,
    polygon_to_cells,
    geo_to_cells,
    grid_disk,
    grid_distance,
    compact_cells,
    uncompact_cells,
    cell_area,
    get_resolution,
    is_valid_cell,
    are_neighbor_cells,
    haversine_distance,
    cell_to_latlngjson,
    geojson_to_h3 as geojson_to_h3,
)
from ..backends.h3.operations import grid_ring

__all__ = [
    'latlng_to_cell',
    'cell_to_latlng',
    'cell_to_latlng_boundary',
    'polygon_to_cells',
    'geo_to_cells',
    'grid_disk',
    'grid_distance',
    'compact_cells',
    'uncompact_cells',
    'cell_area',
    'get_resolution',
    'is_valid_cell',
    'are_neighbor_cells',
    'haversine_distance',
    'cell_to_latlngjson',
    'grid_ring',
]
