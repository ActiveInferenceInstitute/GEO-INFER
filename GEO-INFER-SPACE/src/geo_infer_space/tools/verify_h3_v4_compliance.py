#!/usr/bin/env python3
"""
H3 v4 API Compliance Verification Script

This script verifies that all H3 API usage in the codebase is using the correct v4 API.
It checks for any remaining v3 API calls and validates that the codebase is fully v4 compliant.

Author: GEO-INFER Framework
Version: 4.0.0
License: Apache-2.0
"""

import os
import re
import sys
from typing import List, Dict, Tuple

# H3 v3 API patterns that should NOT exist in the codebase
V3_API_PATTERNS = [
    r'h3\.geo_to_h3\s*\(',
    r'h3\.h3_to_geo\s*\(',
    r'h3\.h3_is_valid\s*\(',
    r'h3\.h3_unidirectional_edge_is_valid\s*\(',
    r'h3\.h3_is_pentagon\s*\(',
    r'h3\.h3_is_res_class_iii\s*\(',
    r'h3\.h3_indexes_are_neighbors\s*\(',
    r'h3\.h3_to_parent\s*\(',
    r'h3\.h3_to_center_child\s*\(',
    r'h3\.h3_to_children\s*\(',
    r'h3\.num_hexagons\s*\(',
    r'h3\.get_res0_indexes\s*\(',
    r'h3\.get_pentagon_indexes\s*\(',
    r'h3\.h3_get_base_cell\s*\(',
    r'h3\.h3_get_resolution\s*\(',
    r'h3\.h3_get_faces\s*\(',
    r'h3\.compact\s*\(',
    r'h3\.uncompact\s*\(',
    r'h3\.polyfill\s*\(',
    r'h3\.h3_distance\s*\(',
    r'h3\.h3_line\s*\(',
    r'h3\.hex_range_distances\s*\(',
    r'h3\.k_ring_distances\s*\(',
    r'h3\.hex_range\s*\(',
    r'h3\.k_ring\s*\(',
    r'h3\.hex_ranges\s*\(',
    r'h3\.hex_ring\s*\(',
    r'h3\.experimental_local_ij_to_h3\s*\(',
    r'h3\.experimental_h3_to_local_ij\s*\(',
    r'h3\.get_h3_unidirectional_edge\s*\(',
    r'h3\.get_h3_indexes_from_unidirectional_edge\s*\(',
    r'h3\.get_h3_unidirectional_edges_from_hexagon\s*\(',
    r'h3\.get_h3_unidirectional_edge_boundary\s*\(',
    r'h3\.get_origin_h3_index_from_unidirectional_edge\s*\(',
    r'h3\.get_destination_h3_index_from_unidirectional_edge\s*\(',
    r'h3\.hex_area_km2\s*\(',
    r'h3\.hex_area_m2\s*\(',
    r'h3\.edge_length_km\s*\(',
    r'h3\.edge_length_m\s*\(',
    r'h3\.point_dist_km\s*\(',
    r'h3\.point_dist_m\s*\(',
    r'h3\.point_dist_rads\s*\(',
    r'h3\.exact_edge_length_rads\s*\(',
    r'h3\.exact_edge_length_km\s*\(',
    r'h3\.exact_edge_length_m\s*\(',
    r'h3\.h3_to_geo_boundary\s*\(',
    r'h3\.h3_set_to_linked_geo\s*\(',
    r'h3\.h3_set_to_multi_polygon\s*\(',
    r'h3\.geo_to_h3shape\s*\(',
    r'h3\.compact_cells_cells\s*\(',
    r'h3\.uncompact_cells_cells_cells\s*\(',
]

# Expected H3 v4 API patterns that should exist
V4_API_PATTERNS = [
    r'h3\.latlng_to_cell\s*\(',
    r'h3\.cell_to_latlng\s*\(',
    r'h3\.is_valid_cell\s*\(',
    r'h3\.is_valid_directed_edge\s*\(',
    r'h3\.is_pentagon\s*\(',
    r'h3\.is_res_class_iii\s*\(',
    r'h3\.are_neighbor_cells\s*\(',
    r'h3\.cell_to_parent\s*\(',
    r'h3\.cell_to_center_child\s*\(',
    r'h3\.cell_to_children\s*\(',
    r'h3\.get_num_cells\s*\(',
    r'h3\.get_res0_cells\s*\(',
    r'h3\.get_pentagons\s*\(',
    r'h3\.get_base_cell_number\s*\(',
    r'h3\.get_resolution\s*\(',
    r'h3\.get_icosahedron_faces\s*\(',
    r'h3\.compact_cells\s*\(',
    r'h3\.uncompact_cells\s*\(',
    r'h3\.polygon_to_cells\s*\(',
    r'h3\.grid_distance\s*\(',
    r'h3\.grid_path_cells\s*\(',
    r'h3\.grid_disk_distances_unsafe\s*\(',
    r'h3\.grid_disk_distances\s*\(',
    r'h3\.grid_disk_unsafe\s*\(',
    r'h3\.grid_disk\s*\(',
    r'h3\.grid_disks_unsafe\s*\(',
    r'h3\.grid_ring_unsafe\s*\(',
    r'h3\.local_ij_to_cell\s*\(',
    r'h3\.cell_to_local_ij\s*\(',
    r'h3\.cells_to_directed_edge\s*\(',
    r'h3\.directed_edge_to_cells\s*\(',
    r'h3\.origin_to_directed_edges\s*\(',
    r'h3\.directed_edge_to_boundary\s*\(',
    r'h3\.get_directed_edge_origin\s*\(',
    r'h3\.get_directed_edge_destination\s*\(',
    r'h3\.get_hexagon_area_avg_km2\s*\(',
    r'h3\.get_hexagon_area_avg_m2\s*\(',
    r'h3\.get_hexagon_edge_length_avg_km\s*\(',
    r'h3\.get_hexagon_edge_length_avg_m\s*\(',
    r'h3\.great_circle_distance_km\s*\(',
    r'h3\.great_circle_distance_m\s*\(',
    r'h3\.great_circle_distance_rads\s*\(',
    r'h3\.edge_length_rads\s*\(',
    r'h3\.edge_length_km\s*\(',
    r'h3\.edge_length_m\s*\(',
    r'h3\.cell_to_boundary\s*\(',
    r'h3\.cells_to_linked_multi_polygon\s*\(',
    r'h3\.cells_to_multi_polygon\s*\(',
    r'h3\.geo_to_cells\s*\(',
]

def find_python_files_with_h3(root_dir: str) -> List[str]:
    """Find all Python files that contain H3 usage."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env', 'build']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'h3.' in content.lower():
                            python_files.append(file_path)
                except (UnicodeDecodeError, PermissionError):
                    continue
    
    return python_files

def check_file_for_v3_api(file_path: str) -> Tuple[bool, List[str]]:
    """Check a single file for v3 API usage."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        return False, [f"Error reading file: {e}"]
    
    issues = []
    
    # Check for v3 API patterns
    for pattern in V3_API_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            issues.append(f"Found v3 API pattern: {pattern} ({len(matches)} occurrences)")
    
    return len(issues) > 0, issues

def check_file_for_v4_api(file_path: str) -> Tuple[bool, List[str]]:
    """Check a single file for v4 API usage."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        return False, [f"Error reading file: {e}"]
    
    v4_usage = []
    
    # Check for v4 API patterns
    for pattern in V4_API_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            v4_usage.append(f"Found v4 API pattern: {pattern} ({len(matches)} occurrences)")
    
    return len(v4_usage) > 0, v4_usage

def test_h3_v4_functionality():
    """Test that H3 v4 API is working correctly."""
    try:
        import h3
        print(f"✅ H3 version: {h3.__version__}")
        
        # Test basic v4 functionality
        cell = h3.latlng_to_cell(37.7749, -122.4194, 8)
        print(f"✅ latlng_to_cell: {cell}")
        
        lat, lng = h3.cell_to_latlng(cell)
        print(f"✅ cell_to_latlng: {lat}, {lng}")
        
        boundary = h3.cell_to_boundary(cell)
        print(f"✅ cell_to_boundary: {len(boundary)} points")
        
        is_valid = h3.is_valid_cell(cell)
        print(f"✅ is_valid_cell: {is_valid}")
        
        resolution = h3.get_resolution(cell)
        print(f"✅ get_resolution: {resolution}")
        
        parent = h3.cell_to_parent(cell, 7)
        print(f"✅ cell_to_parent: {parent}")
        
        children = h3.cell_to_children(cell, 9)
        print(f"✅ cell_to_children: {len(children)} children")
        
        disk = h3.grid_disk(cell, 1)
        print(f"✅ grid_disk: {len(disk)} cells")
        
        distance = h3.grid_distance(cell, list(disk)[0])
        print(f"✅ grid_distance: {distance}")
        
        return True
        
    except ImportError as e:
        print(f"❌ H3 not available: {e}")
        return False
    except Exception as e:
        print(f"❌ H3 v4 API test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🔍 H3 v4 API Compliance Verification")
    print("=" * 50)
    
    # Test H3 v4 functionality
    print("\n1. Testing H3 v4 API functionality...")
    h3_working = test_h3_v4_functionality()
    
    if not h3_working:
        print("❌ H3 v4 API not working correctly. Cannot proceed with verification.")
        sys.exit(1)
    
    # Find Python files with H3 usage
    print("\n2. Scanning for Python files with H3 usage...")
    current_dir = os.getcwd()
    python_files = find_python_files_with_h3(current_dir)
    print(f"Found {len(python_files)} Python files with H3 usage")
    
    # Check for v3 API usage
    print("\n3. Checking for v3 API usage...")
    v3_issues = []
    files_with_v3_issues = 0
    
    for file_path in python_files:
        has_v3_issues, issues = check_file_for_v3_api(file_path)
        if has_v3_issues:
            files_with_v3_issues += 1
            v3_issues.append(f"{file_path}:")
            v3_issues.extend([f"  - {issue}" for issue in issues])
    
    # Check for v4 API usage
    print("\n4. Checking for v4 API usage...")
    v4_usage = []
    files_with_v4_usage = 0
    
    for file_path in python_files:
        has_v4_usage, usage = check_file_for_v4_api(file_path)
        if has_v4_usage:
            files_with_v4_usage += 1
            v4_usage.extend([f"{file_path}: {usage_item}" for usage_item in usage])
    
    # Summary
    print("\n" + "=" * 50)
    print("Verification Summary:")
    print(f"  - Python files with H3 usage: {len(python_files)}")
    print(f"  - Files with v3 API issues: {files_with_v3_issues}")
    print(f"  - Files with v4 API usage: {files_with_v4_usage}")
    print(f"  - H3 v4 API working: {'✅ Yes' if h3_working else '❌ No'}")
    
    if v3_issues:
        print(f"\n❌ Found {len(v3_issues)} v3 API issues:")
        for issue in v3_issues[:10]:  # Show first 10 issues
            print(f"  {issue}")
        if len(v3_issues) > 10:
            print(f"  ... and {len(v3_issues) - 10} more issues")
        print("\n❌ Codebase is NOT fully v4 compliant!")
        return False
    else:
        print(f"\n✅ No v3 API issues found!")
        print(f"✅ Codebase is fully v4 compliant!")
        
        if v4_usage:
            print(f"\n📊 V4 API Usage Summary:")
            v4_patterns = {}
            for usage in v4_usage:
                pattern = re.search(r'Found v4 API pattern: (.*?) \(', usage)
                if pattern:
                    pattern_name = pattern.group(1)
                    v4_patterns[pattern_name] = v4_patterns.get(pattern_name, 0) + 1
            
            for pattern, count in sorted(v4_patterns.items()):
                print(f"  - {pattern}: {count} occurrences")
        
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
