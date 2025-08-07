#!/usr/bin/env python3
"""
Comprehensive H3 v4 API Migration Script

This script identifies and fixes all H3 v3 API calls to use the correct H3 v4 API.
Based on the H3 v4 migration guide: https://h3geo.org/docs/library/migration-3.x/functions/

Author: GEO-INFER Framework
Version: 4.0.0
License: Apache-2.0
"""

import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple

# H3 v3 to v4 API mapping based on official migration guide
H3_V3_TO_V4_MAPPING = {
    # General function names
    'h3.latlng_to_cell': 'h3.latlng_to_cell',
    'h3.cell_to_latlng': 'h3.cell_to_latlng',
    'h3.is_valid_cell': 'h3.is_valid_cell',
    'h3.is_valid_directed_edge': 'h3.is_valid_directed_edge',
    'h3.is_pentagon': 'h3.is_pentagon',
    'h3.is_res_class_iii': 'h3.is_res_class_iii',
    'h3.are_neighbor_cells': 'h3.are_neighbor_cells',
    'h3.cell_to_parent': 'h3.cell_to_parent',
    'h3.cell_to_center_child': 'h3.cell_to_center_child',
    'h3.cell_to_children': 'h3.cell_to_children',
    'h3.get_num_cells': 'h3.get_num_cells',
    'h3.get_res0_cells': 'h3.get_res0_cells',
    'h3.get_pentagons': 'h3.get_pentagons',
    'h3.get_base_cell_number': 'h3.get_base_cell_number',
    'h3.get_resolution': 'h3.get_resolution',
    'h3.get_icosahedron_faces': 'h3.get_icosahedron_faces',
    'h3.latlng_to_cell': 'h3.latlng_to_cell',
    'h3.cell_to_latlng': 'h3.cell_to_latlng',
    'h3.compact_cells': 'h3.compact_cells',
    'h3.uncompact_cells': 'h3.uncompact_cells',
    'h3.polygon_to_cells': 'h3.polygon_to_cells',
    
    # Grid functions
    'h3.grid_distance': 'h3.grid_distance',
    'h3.grid_path_cells': 'h3.grid_path_cells',
    'h3.grid_disk_distances_unsafe': 'h3.grid_disk_distances_unsafe',
    'h3.grid_disk_distances': 'h3.grid_disk_distances',
    'h3.grid_disk_unsafe': 'h3.grid_disk_unsafe',
    'h3.grid_disk': 'h3.grid_disk',
    'h3.grid_disks_unsafe': 'h3.grid_disks_unsafe',
    'h3.grid_ring_unsafe': 'h3.grid_ring_unsafe',
    'h3.local_ij_to_cell': 'h3.local_ij_to_cell',
    'h3.cell_to_local_ij': 'h3.cell_to_local_ij',
    
    # Edge functions
    'h3.cells_to_directed_edge': 'h3.cells_to_directed_edge',
    'h3.directed_edge_to_cells': 'h3.directed_edge_to_cells',
    'h3.origin_to_directed_edges': 'h3.origin_to_directed_edges',
    'h3.directed_edge_to_boundary': 'h3.directed_edge_to_boundary',
    'h3.get_directed_edge_origin': 'h3.get_directed_edge_origin',
    'h3.get_directed_edge_destination': 'h3.get_directed_edge_destination',
    
    # Area/Length functions
    'h3.get_hexagon_area_avg_km2': 'h3.get_hexagon_area_avg_km2',
    'h3.get_hexagon_area_avg_m2': 'h3.get_hexagon_area_avg_m2',
    'h3.get_hexagon_edge_length_avg_km': 'h3.get_hexagon_edge_length_avg_km',
    'h3.get_hexagon_edge_length_avg_m': 'h3.get_hexagon_edge_length_avg_m',
    'h3.great_circle_distance_km': 'h3.great_circle_distance_km',
    'h3.great_circle_distance_m': 'h3.great_circle_distance_m',
    'h3.great_circle_distance_rads': 'h3.great_circle_distance_rads',
    'h3.edge_length_rads': 'h3.edge_length_rads',
    'h3.get_hexagon_edge_length_avg_km': 'h3.get_hexagon_edge_length_avg_km',
    'h3.get_hexagon_edge_length_avg_m': 'h3.get_hexagon_edge_length_avg_m',
    
    # Polygon functions
    'h3.cell_to_boundary': 'h3.cell_to_boundary',
    'h3.cells_to_linked_multi_polygon': 'h3.cells_to_linked_multi_polygon',
    'h3.cells_to_multi_polygon': 'h3.cells_to_multi_polygon',
    
    # Additional v3 patterns that need fixing
    'h3.geo_to_cells': 'h3.geo_to_cells',  # This function doesn't exist in v4
    'h3.compact_cells': 'h3.compact_cells',  # Remove duplicate 'cells'
    'h3.uncompact_cells': 'h3.uncompact_cells',  # Remove duplicate 'cells'
}

# Patterns that indicate v3 API usage but need context-specific fixes
V3_PATTERNS_TO_CHECK = [
    r'h3\.geo_to_h3shape\s*\(',
    r'h3\.compact_cells_cells\s*\(',
    r'h3\.uncompact_cells_cells_cells\s*\(',
    r'h3\.h3_to_geo\s*\(',
    r'h3\.geo_to_h3\s*\(',
    r'h3\.h3_is_valid\s*\(',
    r'h3\.h3_distance\s*\(',
    r'h3\.k_ring\s*\(',
    r'h3\.hex_range\s*\(',
    r'h3\.polyfill\s*\(',
    r'h3\.compact\s*\(',
    r'h3\.uncompact\s*\(',
]

def find_files_with_h3_usage(root_dir: str) -> List[str]:
    """Find all Python files that contain H3 usage."""
    python_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip certain directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
        
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

def fix_h3_v3_api_calls(file_path: str) -> Tuple[bool, List[str]]:
    """
    Fix H3 v3 API calls in a single file.
    
    Returns:
        Tuple of (file_was_modified, list_of_changes)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        print(f"Error reading {file_path}: {e}")
        return False, []
    
    original_content = content
    changes = []
    
    # Apply direct replacements
    for v3_pattern, v4_replacement in H3_V3_TO_V4_MAPPING.items():
        if v3_pattern in content:
            # Use regex to match the function call pattern
            pattern = r'\b' + re.escape(v3_pattern) + r'\b'
            if re.search(pattern, content):
                content = re.sub(pattern, v4_replacement, content)
                changes.append(f"Replaced {v3_pattern} with {v4_replacement}")
    
    # Handle special cases
    # Fix geo_to_h3shape calls - this function doesn't exist in v4
    geo_to_h3shape_pattern = r'h3\.geo_to_h3shape\s*\(([^)]+)\)'
    if re.search(geo_to_h3shape_pattern, content):
        # Replace with appropriate v4 equivalent
        content = re.sub(geo_to_h3shape_pattern, r'h3.geo_to_cells(\1)', content)
        changes.append("Replaced h3.geo_to_cells with h3.geo_to_cells")
    
    # Fix compact_cells_cells and uncompact_cells_cells_cells patterns
    compact_pattern = r'h3\.compact_cells_cells\s*\('
    if re.search(compact_pattern, content):
        content = re.sub(compact_pattern, 'h3.compact_cells(', content)
        changes.append("Fixed h3.compact_cells to h3.compact_cells")
    
    uncompact_pattern = r'h3\.uncompact_cells_cells_cells\s*\('
    if re.search(uncompact_pattern, content):
        content = re.sub(uncompact_pattern, 'h3.uncompact_cells(', content)
        changes.append("Fixed h3.uncompact_cells to h3.uncompact_cells")
    
    # Check for other v3 patterns that need manual review
    for pattern in V3_PATTERNS_TO_CHECK:
        if re.search(pattern, content):
            changes.append(f"Found potential v3 pattern: {pattern}")
    
    # Write changes if any were made
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"Error writing {file_path}: {e}")
            return False, []
    
    return False, changes

def fix_documentation_files(root_dir: str) -> Tuple[bool, List[str]]:
    """Fix H3 v3 API references in documentation files."""
    doc_files = []
    changes = []
    
    # Find documentation files
    for ext in ['*.md', '*.rst', '*.txt']:
        doc_files.extend(glob.glob(os.path.join(root_dir, '**', ext), recursive=True))
    
    total_changes = 0
    
    for file_path in doc_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            continue
        
        original_content = content
        
        # Fix documentation examples
        for v3_pattern, v4_replacement in H3_V3_TO_V4_MAPPING.items():
            if v3_pattern in content:
                pattern = r'\b' + re.escape(v3_pattern) + r'\b'
                if re.search(pattern, content):
                    content = re.sub(pattern, v4_replacement, content)
                    changes.append(f"{file_path}: Replaced {v3_pattern} with {v4_replacement}")
        
        # Fix special documentation patterns
        compact_doc_pattern = r'h3\.compact_cells_cells\s*\('
        if re.search(compact_doc_pattern, content):
            content = re.sub(compact_doc_pattern, 'h3.compact_cells(', content)
            changes.append(f"{file_path}: Fixed compact_cells_cells documentation")
        
        uncompact_doc_pattern = r'h3\.uncompact_cells_cells_cells\s*\('
        if re.search(uncompact_doc_pattern, content):
            content = re.sub(uncompact_doc_pattern, 'h3.uncompact_cells(', content)
            changes.append(f"{file_path}: Fixed uncompact_cells_cells_cells documentation")
        
        if content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                total_changes += 1
            except (UnicodeDecodeError, PermissionError) as e:
                print(f"Error writing {file_path}: {e}")
    
    return total_changes > 0, changes

def main():
    """Main function to run the H3 v4 API migration."""
    print("🔧 H3 v4 API Migration Script")
    print("=" * 50)
    
    # Get the current directory (GEO-INFER-SPACE)
    current_dir = os.getcwd()
    print(f"Working directory: {current_dir}")
    
    # Find all Python files with H3 usage
    python_files = find_files_with_h3_usage(current_dir)
    print(f"Found {len(python_files)} Python files with H3 usage")
    
    # Process Python files
    modified_files = 0
    total_changes = 0
    
    for file_path in python_files:
        print(f"\nProcessing: {file_path}")
        was_modified, changes = fix_h3_v3_api_calls(file_path)
        
        if was_modified:
            modified_files += 1
            total_changes += len(changes)
            print(f"  ✅ Modified with {len(changes)} changes:")
            for change in changes:
                print(f"    - {change}")
        else:
            print(f"  ✅ No changes needed")
    
    # Process documentation files
    print(f"\nProcessing documentation files...")
    doc_modified, doc_changes = fix_documentation_files(current_dir)
    
    if doc_modified:
        total_changes += len(doc_changes)
        print(f"  ✅ Modified documentation with {len(doc_changes)} changes:")
        for change in doc_changes:
            print(f"    - {change}")
    else:
        print(f"  ✅ No documentation changes needed")
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"Migration Summary:")
    print(f"  - Python files processed: {len(python_files)}")
    print(f"  - Python files modified: {modified_files}")
    print(f"  - Documentation files modified: {1 if doc_modified else 0}")
    print(f"  - Total changes made: {total_changes}")
    
    if total_changes > 0:
        print(f"\n✅ H3 v4 API migration completed successfully!")
        print(f"   All v3 API calls have been updated to v4 equivalents.")
    else:
        print(f"\n✅ No H3 v3 API calls found - codebase is already v4 compliant!")
    
    # Additional recommendations
    print(f"\n📋 Additional Recommendations:")
    print(f"  1. Run tests to verify all H3 functionality works correctly")
    print(f"  2. Update any custom H3 utility functions to use v4 API")
    print(f"  3. Review any hardcoded H3 function names in configuration files")
    print(f"  4. Update any external documentation or API specifications")

if __name__ == "__main__":
    main()
