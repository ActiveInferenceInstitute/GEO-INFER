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
    cell_to_children_size,
    cell_to_children_positions
)

# Import traversal operations
from .traversal import (
    grid_disk,
    grid_ring,
    grid_path_cells,
    grid_distance,
    grid_neighbors,
    great_circle_distance
)

# Import hierarchy operations
from .hierarchy import (
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
    H3_VERSION,
    MAX_H3_RES,
    MIN_H3_RES,
    H3_RESOLUTIONS,
    LAT_MIN,
    LAT_MAX,
    LNG_MIN,
    LNG_MAX,
    WGS84_EARTH_RADIUS_KM,
    ERROR_MESSAGES,
    H3_AREA_KM2
)

# Import validation operations
from .validation import (
    validate_cell,
    validate_resolution,
    validate_coordinates,
    validate_polygon
)

# Import unidirectional operations
from .unidirectional import (
    get_unidirectional_edge,
    get_origin_cell_from_unidirectional_edge,
    get_destination_cell_from_unidirectional_edge,
    get_unidirectional_edges_from_hexagon,
    get_unidirectional_edge_boundary_vertices,
    get_unidirectional_edge_boundary_vertices_geojson,
    get_unidirectional_edge_boundary_vertices_wkt,
    get_unidirectional_edge_boundary_vertices_latlng,
    get_unidirectional_edge_boundary_vertices_latlng_geojson,
    get_unidirectional_edge_boundary_vertices_latlng_wkt,
    get_unidirectional_edge_boundary_vertices_latlng_csv,
    get_unidirectional_edge_boundary_vertices_latlng_kml,
    get_unidirectional_edge_boundary_vertices_latlng_shapefile_data,
    get_unidirectional_edge_boundary_vertices_latlng_geojson,
    get_unidirectional_edge_boundary_vertices_latlng_wkt,
    get_unidirectional_edge_boundary_vertices_latlng_csv,
    get_unidirectional_edge_boundary_vertices_latlng_kml,
    get_unidirectional_edge_boundary_vertices_latlng_shapefile_data
)

# Import visualization operations
from .visualization import (
    create_cell_map,
    create_resolution_chart,
    create_area_distribution_plot,
    create_density_heatmap,
    create_comparison_plot,
    generate_visualization_report
)

# Import animation operations
from .animation import (
    create_grid_expansion_animation,
    create_resolution_transition_animation,
    create_path_animation,
    create_temporal_animation,
    create_animated_heatmap,
    generate_animation_report
)

# Import interactive operations
from .interactive import (
    create_interactive_map,
    create_simple_html_map,
    create_interactive_dashboard,
    create_zoomable_map,
    create_interactive_report
)

# Define all exported functions
__all__ = [
    # Core operations
    'latlng_to_cell', 'cell_to_latlng', 'cell_to_boundary', 'cell_to_polygon',
    'polygon_to_cells', 'polyfill', 'cell_area', 'cell_perimeter', 'edge_length',
    'num_cells', 'get_resolution', 'is_valid_cell', 'is_pentagon', 'is_class_iii',
    'is_res_class_iii',
    
    # Indexing operations
    'cell_to_center_child', 'cell_to_children', 'cell_to_parent',
    'cell_to_children_size', 'cell_to_children_positions',
    
    # Traversal operations
    'grid_disk', 'grid_ring', 'grid_path_cells', 'grid_distance', 'grid_neighbors',
    'great_circle_distance',
    
    # Hierarchy operations
    'get_hierarchy_path', 'get_ancestors', 'get_descendants',
    
    # Conversion operations
    'cell_to_geojson', 'geojson_to_cells', 'wkt_to_cells', 'cells_to_wkt',
    'cells_to_geojson', 'cells_to_shapefile_data', 'cells_to_kml', 'cells_to_csv',
    
    # Analysis operations
    'analyze_cell_distribution', 'calculate_spatial_statistics', 'find_nearest_cell',
    'calculate_cell_density', 'analyze_resolution_distribution',
    
    # Constants
    'H3_VERSION', 'MAX_H3_RES', 'MIN_H3_RES', 'H3_RESOLUTIONS', 'LAT_MIN',
    'LAT_MAX', 'LNG_MIN', 'LNG_MAX', 'WGS84_EARTH_RADIUS_KM', 'ERROR_MESSAGES',
    'H3_AREA_KM2',
    
    # Validation operations
    'validate_cell', 'validate_resolution', 'validate_coordinates', 'validate_polygon',
    
    # Unidirectional operations
    'get_unidirectional_edge', 'get_origin_cell_from_unidirectional_edge',
    'get_destination_cell_from_unidirectional_edge', 'get_unidirectional_edges_from_hexagon',
    'get_unidirectional_edge_boundary_vertices', 'get_unidirectional_edge_boundary_vertices_geojson',
    'get_unidirectional_edge_boundary_vertices_wkt', 'get_unidirectional_edge_boundary_vertices_latlng',
    'get_unidirectional_edge_boundary_vertices_latlng_geojson', 'get_unidirectional_edge_boundary_vertices_latlng_wkt',
    'get_unidirectional_edge_boundary_vertices_latlng_csv', 'get_unidirectional_edge_boundary_vertices_latlng_kml',
    'get_unidirectional_edge_boundary_vertices_latlng_shapefile_data', 'get_unidirectional_edge_boundary_vertices_latlng_geojson',
    'get_unidirectional_edge_boundary_vertices_latlng_wkt', 'get_unidirectional_edge_boundary_vertices_latlng_csv',
    'get_unidirectional_edge_boundary_vertices_latlng_kml', 'get_unidirectional_edge_boundary_vertices_latlng_shapefile_data',
    
    # Visualization operations
    'create_cell_map', 'create_resolution_chart', 'create_area_distribution_plot',
    'create_density_heatmap', 'create_comparison_plot', 'generate_visualization_report',
    
    # Animation operations
    'create_grid_expansion_animation', 'create_resolution_transition_animation',
    'create_path_animation', 'create_temporal_animation', 'create_animated_heatmap',
    'generate_animation_report',
    
    # Interactive operations
    'create_interactive_map', 'create_simple_html_map', 'create_interactive_dashboard',
    'create_zoomable_map', 'create_interactive_report'
]

# Version information
__version__ = "4.3.0"
__author__ = "GEO-INFER Framework"
__license__ = "Apache-2.0" 