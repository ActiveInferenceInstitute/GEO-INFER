#!/usr/bin/env python3
"""
H3 Geospatial Framework

A comprehensive H3 geospatial indexing framework using H3 v4.3.0.
Provides modular, well-tested geospatial operations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

# Import core operations
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

# Import indexing operations
from .indexing import (
    cell_to_center_child,
    cell_to_children,
    cell_to_parent,
    cell_to_pos,
    pos_to_cell,
    cell_to_string,
    string_to_cell,
    int_to_cell,
    cell_to_int
)

# Import traversal operations
from .traversal import (
    grid_disk,
    grid_ring,
    grid_path_cells,
    grid_distance,
    cell_to_local_ij,
    local_ij_to_cell,
    great_circle_distance,
    haversine_distance,
    grid_disk_rings,
    grid_neighbors,
    grid_compact,
    grid_uncompact
)

# Import hierarchy operations
from .hierarchy import (
    cell_to_sub_center_child,
    cell_to_sub_center_children,
    cell_to_sub_center_parent,
    cell_to_sub_center_children_size,
    cell_to_sub_center_children_positions,
    get_hierarchy_path,
    get_ancestors,
    get_descendants
)

# Import conversion operations
from .conversion import (
    cell_to_geojson,
    geojson_to_cells,
    wkt_to_cells,
    cells_to_wkt,
    cells_to_geojson,
    cells_to_shapefile_data,
    cells_to_kml,
    cells_to_csv
)

# Import analysis operations
from .analysis import (
    analyze_cell_distribution,
    calculate_spatial_statistics,
    find_nearest_cell,
    calculate_cell_density,
    analyze_resolution_distribution
)

# Import constants
from .constants import (
    MAX_H3_RES,
    MIN_H3_RES,
    LAT_MIN,
    LAT_MAX,
    LNG_MIN,
    LNG_MAX,
    ERROR_MESSAGES,
    H3_AREA_KM2,
    H3_EDGE_LENGTH_KM
)

# Version information
__version__ = "4.3.0"
__author__ = "GEO-INFER Framework"
__license__ = "Apache-2.0"

# Export all functions
__all__ = [
    # Core operations
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
    'is_res_class_iii',
    
    # Indexing operations
    'cell_to_center_child',
    'cell_to_children',
    'cell_to_parent',
    'cell_to_pos',
    'pos_to_cell',
    'cell_to_string',
    'string_to_cell',
    'int_to_cell',
    'cell_to_int',
    
    # Traversal operations
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
    'grid_uncompact',
    
    # Hierarchy operations
    'cell_to_sub_center_child',
    'cell_to_sub_center_children',
    'cell_to_sub_center_parent',
    'cell_to_sub_center_children_size',
    'cell_to_sub_center_children_positions',
    'get_hierarchy_path',
    'get_ancestors',
    'get_descendants',
    
    # Conversion operations
    'cell_to_geojson',
    'geojson_to_cells',
    'wkt_to_cells',
    'cells_to_wkt',
    'cells_to_geojson',
    'cells_to_shapefile_data',
    'cells_to_kml',
    'cells_to_csv',
    
    # Analysis operations
    'analyze_cell_distribution',
    'calculate_spatial_statistics',
    'find_nearest_cell',
    'calculate_cell_density',
    'analyze_resolution_distribution',
    
    # Constants
    'MAX_H3_RES',
    'MIN_H3_RES',
    'LAT_MIN',
    'LAT_MAX',
    'LNG_MIN',
    'LNG_MAX',
    'ERROR_MESSAGES',
    'H3_AREA_KM2',
    'H3_EDGE_LENGTH_KM'
] 