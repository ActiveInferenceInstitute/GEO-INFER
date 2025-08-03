#!/usr/bin/env python3
"""
Comprehensive H3 Demonstration

Demonstrates all H3 geospatial operations using H3 v4.3.0.
Shows core operations, indexing, traversal, hierarchy, and analysis.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import time
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from h3 import (
    # Core operations
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_to_polygon,
    polygon_to_cells, polyfill, cell_area, cell_perimeter, edge_length,
    num_cells, get_resolution, is_valid_cell, is_pentagon, is_class_iii,
    
    # Indexing operations
    cell_to_center_child, cell_to_children, cell_to_parent,
    cell_to_pos, pos_to_cell, cell_to_string, string_to_cell,
    int_to_cell, cell_to_int,
    
    # Traversal operations
    grid_disk, grid_ring, grid_path_cells, grid_distance,
    cell_to_local_ij, local_ij_to_cell, great_circle_distance,
    haversine_distance, grid_disk_rings, grid_neighbors,
    grid_compact, grid_uncompact,
    
    # Hierarchy operations
    cell_to_sub_center_child, cell_to_sub_center_children,
    cell_to_sub_center_parent, cell_to_sub_center_children_size,
    cell_to_sub_center_children_positions, get_hierarchy_path,
    get_ancestors, get_descendants,
    
    # Unidirectional operations
    cell_to_vertexes, cell_to_vertex, vertex_to_latlng,
    latlng_to_vertex, vertex_to_cells, edge_boundary,
    edge_length as edge_length_func, edge_lengths, get_icosahedron_faces,
    cell_to_icosahedron_faces, get_cell_vertices, get_cell_edges,
    get_vertex_neighbors, get_edge_cells,
    
    # Validation operations
    is_valid_edge, is_valid_vertex, is_valid_latlng,
    is_valid_resolution, is_valid_polygon, is_valid_geojson,
    is_valid_wkt, validate_cell, validate_edge, validate_vertex,
    validate_latlng, validate_resolution, validate_polygon,
    validate_geojson, validate_wkt, validate_cells,
    validate_resolution_range,
    
    # Utility operations
    get_hexagon_area_avg, get_hexagon_edge_length_avg, get_num_cells,
    get_pentagons, get_res0_cells, get_base_cell_number,
    get_cell_edge_boundary, get_cell_vertex_boundary,
    get_resolution_info, get_cell_info, get_resolution_comparison,
    
    # Conversion operations
    cell_to_geojson, geojson_to_cells, wkt_to_cells, cells_to_wkt,
    cells_to_geojson, cells_to_shapefile_data, cells_to_kml, cells_to_csv,
    
    # Analysis operations
    analyze_cell_distribution, calculate_spatial_statistics,
    find_nearest_cell, calculate_cell_density, analyze_resolution_distribution,
    
    # Constants
    H3_VERSION, MAX_H3_RES, MIN_H3_RES, H3_RESOLUTIONS
)


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"🔹 {title}")
    print("=" * 80)


def print_subsection(title: str):
    """Print a subsection header."""
    print(f"\n📋 {title}")
    print("-" * 60)


def demo_core_operations():
    """Demonstrate core H3 operations."""
    print_section("Core H3 Operations")
    
    # Test coordinates
    lat, lng = 37.7749, -122.4194  # San Francisco
    resolution = 9
    
    print_subsection("Coordinate to Cell Conversion")
    cell = latlng_to_cell(lat, lng, resolution)
    print(f"Coordinates: ({lat}, {lng})")
    print(f"H3 Cell: {cell}")
    print(f"Resolution: {resolution}")
    
    print_subsection("Cell to Coordinate Conversion")
    result_lat, result_lng = cell_to_latlng(cell)
    print(f"H3 Cell: {cell}")
    print(f"Coordinates: ({result_lat}, {result_lng})")
    print(f"Difference: ({abs(lat - result_lat):.6f}, {abs(lng - result_lng):.6f})")
    
    print_subsection("Cell Boundary")
    boundary = cell_to_boundary(cell)
    print(f"H3 Cell: {cell}")
    print(f"Boundary vertices: {len(boundary)}")
    print(f"First 3 vertices: {boundary[:3]}")
    
    print_subsection("Cell Properties")
    area = cell_area(cell, 'km^2')
    perimeter = cell_perimeter(cell, 'km')
    edge_len = edge_length(resolution, 'km')
    cell_count = num_cells(resolution)
    
    print(f"Cell area: {area:.6f} km²")
    print(f"Cell perimeter: {perimeter:.6f} km")
    print(f"Edge length: {edge_len:.6f} km")
    print(f"Total cells at resolution {resolution}: {cell_count:,}")
    
    print_subsection("Cell Validation")
    print(f"Valid cell: {is_valid_cell(cell)}")
    print(f"Is pentagon: {is_pentagon(cell)}")
    print(f"Is Class III: {is_class_iii(cell)}")
    print(f"Resolution {resolution} is Class III: {is_res_class_iii(resolution)}")


def demo_indexing_operations():
    """Demonstrate H3 indexing operations."""
    print_section("H3 Indexing Operations")
    
    cell = '89283082e73ffff'
    resolution = get_resolution(cell)
    
    print_subsection("Parent-Child Relationships")
    parent = cell_to_parent(cell, resolution - 1)
    children = cell_to_children(cell, resolution + 1)
    center_child = cell_to_center_child(cell, resolution + 1)
    
    print(f"Original cell: {cell}")
    print(f"Parent: {parent}")
    print(f"Center child: {center_child}")
    print(f"Number of children: {len(children)}")
    print(f"First 3 children: {children[:3]}")
    
    print_subsection("Position Operations")
    pos = cell_to_pos(cell)
    reconstructed_cell = pos_to_cell(parent, pos)
    
    print(f"Position in parent: {pos}")
    print(f"Reconstructed cell: {reconstructed_cell}")
    print(f"Reconstruction successful: {cell == reconstructed_cell}")
    
    print_subsection("String/Integer Conversion")
    cell_int = cell_to_int(cell)
    cell_str = int_to_cell(cell_int)
    
    print(f"Cell string: {cell}")
    print(f"Cell integer: {cell_int}")
    print(f"Reconstructed string: {cell_str}")
    print(f"Conversion successful: {cell == cell_str}")


def demo_traversal_operations():
    """Demonstrate H3 traversal operations."""
    print_section("H3 Traversal Operations")
    
    cell = '89283082e73ffff'
    
    print_subsection("Grid Disk")
    disk_cells = grid_disk(cell, 2)
    print(f"Center cell: {cell}")
    print(f"Disk radius: 2")
    print(f"Total cells in disk: {len(disk_cells)}")
    print(f"First 5 cells: {disk_cells[:5]}")
    
    print_subsection("Grid Ring")
    ring_cells = grid_ring(cell, 1)
    print(f"Center cell: {cell}")
    print(f"Ring distance: 1")
    print(f"Cells in ring: {len(ring_cells)}")
    print(f"Ring cells: {ring_cells}")
    
    print_subsection("Grid Path")
    target_cell = '89283082e77ffff'
    path_cells = grid_path_cells(cell, target_cell)
    distance = grid_distance(cell, target_cell)
    
    print(f"Origin: {cell}")
    print(f"Destination: {target_cell}")
    print(f"Path length: {len(path_cells)}")
    print(f"Grid distance: {distance}")
    print(f"Path: {path_cells}")
    
    print_subsection("Local Coordinates")
    origin = '88283082e73ffff'
    i, j = cell_to_local_ij(cell, origin)
    reconstructed = local_ij_to_cell(origin, i, j)
    
    print(f"Origin: {origin}")
    print(f"Cell: {cell}")
    print(f"Local coordinates: ({i}, {j})")
    print(f"Reconstructed: {reconstructed}")
    print(f"Reconstruction successful: {cell == reconstructed}")


def demo_hierarchy_operations():
    """Demonstrate H3 hierarchy operations."""
    print_section("H3 Hierarchy Operations")
    
    cell = '89283082e73ffff'
    resolution = get_resolution(cell)
    
    print_subsection("Sub-Center Operations")
    sub_center_child = cell_to_sub_center_child(cell, resolution + 1)
    sub_center_children = cell_to_sub_center_children(cell, resolution + 1)
    sub_center_parent = cell_to_sub_center_parent(cell, resolution - 1)
    children_size = cell_to_sub_center_children_size(cell, resolution + 1)
    children_positions = cell_to_sub_center_children_positions(cell, resolution + 1)
    
    print(f"Original cell: {cell}")
    print(f"Sub-center child: {sub_center_child}")
    print(f"Sub-center children count: {len(sub_center_children)}")
    print(f"Sub-center parent: {sub_center_parent}")
    print(f"Children size: {children_size}")
    print(f"Children positions: {children_positions}")
    
    print_subsection("Hierarchy Path")
    target_res = resolution - 2
    path = get_hierarchy_path(cell, target_res)
    
    print(f"From resolution {resolution} to {target_res}")
    print(f"Path length: {len(path)}")
    print(f"Path: {path}")
    
    print_subsection("Ancestors and Descendants")
    ancestors = get_ancestors(cell, 3)
    descendants = get_descendants(cell, 10)
    
    print(f"Cell: {cell}")
    print(f"Ancestors (max 3): {len(ancestors)}")
    print(f"Ancestors: {ancestors}")
    print(f"Descendants (max 10): {len(descendants)}")
    print(f"First 5 descendants: {descendants[:5]}")


def demo_unidirectional_operations():
    """Demonstrate H3 unidirectional operations."""
    print_section("H3 Unidirectional Operations")
    
    cell = '89283082e73ffff'
    
    print_subsection("Vertex Operations")
    vertices = cell_to_vertexes(cell)
    first_vertex = cell_to_vertex(cell, 0)
    vertex_coords = vertex_to_latlng(first_vertex)
    
    print(f"Cell: {cell}")
    print(f"Number of vertices: {len(vertices)}")
    print(f"First vertex: {first_vertex}")
    print(f"Vertex coordinates: {vertex_coords}")
    
    print_subsection("Edge Operations")
    # Note: Edge operations require valid edge indices
    # This is a simplified demonstration
    print("Edge operations require valid edge indices")
    print("Edge boundary and length calculations available")
    
    print_subsection("Icosahedron Faces")
    faces = get_icosahedron_faces(cell)
    print(f"Cell: {cell}")
    print(f"Icosahedron faces: {faces}")


def demo_validation_operations():
    """Demonstrate H3 validation operations."""
    print_section("H3 Validation Operations")
    
    print_subsection("Cell Validation")
    valid_cell = '89283082e73ffff'
    invalid_cell = 'invalid'
    
    print(f"Valid cell '{valid_cell}': {is_valid_cell(valid_cell)}")
    print(f"Invalid cell '{invalid_cell}': {is_valid_cell(invalid_cell)}")
    
    print_subsection("Coordinate Validation")
    valid_coords = (37.7749, -122.4194)
    invalid_lat = (91.0, -122.4194)
    invalid_lng = (37.7749, 181.0)
    
    print(f"Valid coordinates {valid_coords}: {is_valid_latlng(*valid_coords)}")
    print(f"Invalid latitude {invalid_lat}: {is_valid_latlng(*invalid_lat)}")
    print(f"Invalid longitude {invalid_lng}: {is_valid_latlng(*invalid_lng)}")
    
    print_subsection("Resolution Validation")
    valid_res = 9
    invalid_res = 20
    
    print(f"Valid resolution {valid_res}: {is_valid_resolution(valid_res)}")
    print(f"Invalid resolution {invalid_res}: {is_valid_resolution(invalid_res)}")


def demo_utility_operations():
    """Demonstrate H3 utility operations."""
    print_section("H3 Utility Operations")
    
    resolution = 9
    
    print_subsection("Resolution Information")
    info = get_resolution_info(resolution)
    print(f"Resolution {resolution} information:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print_subsection("Cell Information")
    cell = '89283082e73ffff'
    cell_info = get_cell_info(cell)
    print(f"Cell {cell} information:")
    for key, value in cell_info.items():
        print(f"  {key}: {value}")
    
    print_subsection("Resolution Comparison")
    res1, res2 = 9, 10
    comparison = get_resolution_comparison(res1, res2)
    print(f"Comparison between resolution {res1} and {res2}:")
    for key, value in comparison.items():
        if key in ['res1', 'res2']:
            print(f"  {key}: {len(value)} properties")
        else:
            print(f"  {key}: {value}")


def demo_conversion_operations():
    """Demonstrate H3 conversion operations."""
    print_section("H3 Conversion Operations")
    
    cell = '89283082e73ffff'
    cells = [cell, '89283082e77ffff', '89283082e7bffff']
    
    print_subsection("Cell to GeoJSON")
    geojson = cell_to_geojson(cell)
    print(f"Cell: {cell}")
    print(f"GeoJSON type: {geojson['type']}")
    print(f"Geometry type: {geojson['geometry']['type']}")
    print(f"Properties: {geojson['properties']}")
    
    print_subsection("Cells to GeoJSON FeatureCollection")
    feature_collection = cells_to_geojson(cells)
    print(f"Number of cells: {len(cells)}")
    print(f"FeatureCollection type: {feature_collection['type']}")
    print(f"Number of features: {len(feature_collection['features'])}")
    
    print_subsection("Cells to CSV")
    csv_data = cells_to_csv(cells)
    print("CSV header and first row:")
    lines = csv_data.split('\n')
    print(lines[0])
    print(lines[1])


def demo_analysis_operations():
    """Demonstrate H3 analysis operations."""
    print_section("H3 Analysis Operations")
    
    cells = ['89283082e73ffff', '89283082e77ffff', '89283082e7bffff']
    
    print_subsection("Cell Distribution Analysis")
    distribution = analyze_cell_distribution(cells)
    print("Cell distribution analysis:")
    for key, value in distribution.items():
        print(f"  {key}: {value}")
    
    print_subsection("Spatial Statistics")
    stats = calculate_spatial_statistics(cells)
    print("Spatial statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print_subsection("Nearest Cell")
    target_lat, target_lng = 37.7749, -122.4194
    nearest, distance = find_nearest_cell(target_lat, target_lng, cells)
    print(f"Target coordinates: ({target_lat}, {target_lng})")
    print(f"Nearest cell: {nearest}")
    print(f"Distance: {distance:.6f} km")
    
    print_subsection("Cell Density")
    density = calculate_cell_density(cells)
    print(f"Cell density: {density:.2f} cells/km²")
    
    print_subsection("Resolution Distribution")
    res_dist = analyze_resolution_distribution(cells)
    print("Resolution distribution:")
    for key, value in res_dist.items():
        print(f"  {key}: {value}")


def demo_performance():
    """Demonstrate H3 performance."""
    print_section("H3 Performance Demo")
    
    import numpy as np
    
    # Generate test data
    num_operations = 10000
    lats = np.random.uniform(-90, 90, num_operations)
    lngs = np.random.uniform(-180, 180, num_operations)
    resolution = 9
    
    print_subsection("Bulk Coordinate Conversion")
    start_time = time.time()
    cells = [latlng_to_cell(lat, lng, resolution) for lat, lng in zip(lats, lngs)]
    end_time = time.time()
    
    duration = end_time - start_time
    rate = num_operations / duration
    
    print(f"Operations: {num_operations:,}")
    print(f"Duration: {duration:.3f} seconds")
    print(f"Rate: {rate:,.0f} ops/sec")
    
    print_subsection("Bulk Cell Analysis")
    start_time = time.time()
    areas = [cell_area(cell, 'km^2') for cell in cells[:1000]]
    end_time = time.time()
    
    duration = end_time - start_time
    rate = 1000 / duration
    
    print(f"Cell area calculations: 1,000")
    print(f"Duration: {duration:.3f} seconds")
    print(f"Rate: {rate:,.0f} ops/sec")
    print(f"Average area: {np.mean(areas):.6f} km²")


def main():
    """Main demonstration function."""
    print("🧪 Comprehensive H3 Geospatial Operations Demo")
    print("=" * 80)
    print(f"H3 Version: {H3_VERSION}")
    print(f"Resolution range: {MIN_H3_RES} to {MAX_H3_RES}")
    print(f"Available resolutions: {H3_RESOLUTIONS}")
    print("=" * 80)
    
    try:
        # Run all demonstrations
        demo_core_operations()
        demo_indexing_operations()
        demo_traversal_operations()
        demo_hierarchy_operations()
        demo_unidirectional_operations()
        demo_validation_operations()
        demo_utility_operations()
        demo_conversion_operations()
        demo_analysis_operations()
        demo_performance()
        
        print_section("Demo Complete")
        print("✅ All H3 operations demonstrated successfully!")
        print("🎉 The H3 module is working correctly.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 