"""
Utility modules for GEO-INFER-PLACE

This package contains utility functions and classes for place-based 
geospatial analysis including H3 operations, configuration management,
data source integration, and helper functions.
"""

from geo_infer_space.utils.config_loader import LocationConfigLoader
from .data_sources import CaliforniaDataSources
from .h3_operations import (
    latlng_to_cell,
    cell_to_latlng,
    cell_to_latlng_boundary,
    geo_to_cells,
    polygon_to_cells,
    grid_disk,
    grid_distance,
    cell_area,
    get_resolution,
    is_valid_cell,
    are_neighbor_cells,
    cells_to_geodataframe,
)

__all__ = [
    "LocationConfigLoader",
    "CaliforniaDataSources",
    # H3 operations
    "latlng_to_cell",
    "cell_to_latlng",
    "cell_to_latlng_boundary",
    "geo_to_cells",
    "polygon_to_cells",
    "grid_disk",
    "grid_distance",
    "cell_area",
    "get_resolution",
    "is_valid_cell",
    "are_neighbor_cells",
    "cells_to_geodataframe",
] 