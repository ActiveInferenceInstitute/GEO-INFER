#!/usr/bin/env python3
"""
Hierarchical Operations Example

Demonstrates hierarchical H3 operations using tested methods.
Shows parent-child relationships, hierarchical navigation, and sub-center operations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from h3 import (
    # Core operations
    latlng_to_cell, cell_to_latlng, cell_area, get_resolution,
    
    # Indexing operations
    cell_to_center_child, cell_to_children, cell_to_parent,
    cell_to_pos, pos_to_cell,
    
    # Hierarchy operations
    cell_to_sub_center_child, cell_to_sub_center_children,
    cell_to_sub_center_parent, cell_to_sub_center_children_size,
    cell_to_sub_center_children_positions, get_hierarchy_path,
    get_ancestors, get_descendants
)


def demo_parent_child_relationships():
    """Demonstrate parent-child relationships."""
    print("🔹 Parent-Child Relationships")
    print("-" * 40)
    
    # Start with a cell at resolution 9
    start_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Starting cell (res 9): {start_cell}")
    
    # Get parent at resolution 8
    parent_cell = cell_to_parent(start_cell, 8)
    print(f"Parent cell (res 8): {parent_cell}")
    
    # Get children at resolution 10
    children = cell_to_children(start_cell, 10)
    print(f"Children (res 10): {len(children)} cells")
    
    # Show first few children
    for i, child in enumerate(children[:5]):
        lat, lng = cell_to_latlng(child)
        area = cell_area(child, 'km^2')
        print(f"  Child {i+1}: {child} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Get center child
    center_child = cell_to_center_child(start_cell, 10)
    print(f"Center child: {center_child}")
    
    # Verify parent-child relationship
    print(f"Center child's parent: {cell_to_parent(center_child, 9)}")
    print(f"Matches original cell: {cell_to_parent(center_child, 9) == start_cell}")


def demo_position_operations():
    """Demonstrate position operations within parent cells."""
    print("\n🔹 Position Operations")
    print("-" * 40)
    
    # Get a parent cell
    parent_cell = latlng_to_cell(37.7749, -122.4194, 8)
    print(f"Parent cell: {parent_cell}")
    
    # Get all children
    children = cell_to_children(parent_cell, 9)
    print(f"Number of children: {len(children)}")
    
    # Show position of each child
    print("Child positions:")
    for i, child in enumerate(children):
        pos = cell_to_pos(child)
        lat, lng = cell_to_latlng(child)
        area = cell_area(child, 'km^2')
        print(f"  Child {i+1}: Position {pos} - {child} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Test position to cell conversion
    for pos in range(len(children)):
        reconstructed_cell = pos_to_cell(parent_cell, pos)
        print(f"  Position {pos} -> Cell: {reconstructed_cell}")
        print(f"    Matches original: {reconstructed_cell == children[pos]}")


def demo_sub_center_operations():
    """Demonstrate sub-center operations."""
    print("\n🔹 Sub-Center Operations")
    print("-" * 40)
    
    # Test cell
    test_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Test cell: {test_cell}")
    
    # Get sub-center child
    sub_center_child = cell_to_sub_center_child(test_cell, 10)
    print(f"Sub-center child: {sub_center_child}")
    
    # Get all sub-center children
    sub_center_children = cell_to_sub_center_children(test_cell, 10)
    print(f"Sub-center children: {len(sub_center_children)}")
    
    # Show sub-center children
    for i, child in enumerate(sub_center_children[:5]):
        lat, lng = cell_to_latlng(child)
        area = cell_area(child, 'km^2')
        print(f"  Sub-center child {i+1}: {child} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Get sub-center parent
    sub_center_parent = cell_to_sub_center_parent(test_cell, 8)
    print(f"Sub-center parent: {sub_center_parent}")
    
    # Get sub-center children size
    children_size = cell_to_sub_center_children_size(test_cell, 10)
    print(f"Sub-center children size: {children_size}")
    
    # Get sub-center children positions
    children_positions = cell_to_sub_center_children_positions(test_cell, 10)
    print(f"Sub-center children positions: {children_positions}")


def demo_hierarchy_path():
    """Demonstrate hierarchical path operations."""
    print("\n🔹 Hierarchy Path Operations")
    print("-" * 40)
    
    # Test cell at resolution 9
    start_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Starting cell: {start_cell}")
    
    # Get path to resolution 6 (going up)
    up_path = get_hierarchy_path(start_cell, 6)
    print(f"Path to resolution 6 (up):")
    for i, cell in enumerate(up_path):
        res = get_resolution(cell)
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        print(f"  Res {res}: {cell} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Get path to resolution 12 (going down)
    down_path = get_hierarchy_path(start_cell, 12)
    print(f"\nPath to resolution 12 (down):")
    for i, cell in enumerate(down_path):
        res = get_resolution(cell)
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        print(f"  Res {res}: {cell} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")


def demo_ancestors_descendants():
    """Demonstrate ancestor and descendant operations."""
    print("\n🔹 Ancestors and Descendants")
    print("-" * 40)
    
    # Test cell
    test_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Test cell: {test_cell}")
    
    # Get ancestors (up to 3 levels)
    ancestors = get_ancestors(test_cell, 3)
    print(f"Ancestors (up to 3 levels):")
    for i, ancestor in enumerate(ancestors):
        res = get_resolution(ancestor)
        lat, lng = cell_to_latlng(ancestor)
        area = cell_area(ancestor, 'km^2')
        print(f"  Level {i+1} (res {res}): {ancestor} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Get descendants (up to 10 cells)
    descendants = get_descendants(test_cell, 10)
    print(f"\nDescendants (up to 10 cells):")
    for i, descendant in enumerate(descendants):
        res = get_resolution(descendant)
        lat, lng = cell_to_latlng(descendant)
        area = cell_area(descendant, 'km^2')
        print(f"  Descendant {i+1} (res {res}): {descendant} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")


def demo_hierarchical_analysis():
    """Demonstrate hierarchical analysis across multiple resolutions."""
    print("\n🔹 Hierarchical Analysis")
    print("-" * 40)
    
    # Test location
    lat, lng = 37.7749, -122.4194
    
    # Analyze hierarchy from resolution 0 to 12
    print("Hierarchical Analysis from Resolution 0 to 12:")
    print("Resolution | Cell Index | Area (km²) | Children")
    print("-" * 60)
    
    for resolution in range(0, 13):
        cell = latlng_to_cell(lat, lng, resolution)
        area = cell_area(cell, 'km^2')
        
        # Count children at next resolution
        if resolution < 12:
            children = cell_to_children(cell, resolution + 1)
            children_count = len(children)
        else:
            children_count = 0
        
        print(f"{resolution:10d} | {cell:15s} | {area:10.6f} | {children_count:8d}")
    
    # Analyze area scaling
    print(f"\nArea Scaling Analysis:")
    areas = []
    for resolution in range(0, 13):
        cell = latlng_to_cell(lat, lng, resolution)
        area = cell_area(cell, 'km^2')
        areas.append(area)
    
    for i in range(len(areas) - 1):
        ratio = areas[i] / areas[i + 1]
        print(f"  Res {i} to {i+1}: {ratio:.2f}x larger")


def demo_multi_resolution_operations():
    """Demonstrate operations across multiple resolutions."""
    print("\n🔹 Multi-Resolution Operations")
    print("-" * 40)
    
    # Test locations
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437)
    ]
    
    for city, lat, lng in locations:
        print(f"\n📍 {city}:")
        
        # Analyze at different resolutions
        for resolution in [6, 8, 10]:
            cell = latlng_to_cell(lat, lng, resolution)
            area = cell_area(cell, 'km^2')
            
            # Get parent and children
            if resolution > 0:
                parent = cell_to_parent(cell, resolution - 1)
                parent_area = cell_area(parent, 'km^2')
            else:
                parent_area = 0
            
            if resolution < 12:
                children = cell_to_children(cell, resolution + 1)
                children_count = len(children)
                children_area = sum(cell_area(child, 'km^2') for child in children)
            else:
                children_count = 0
                children_area = 0
            
            print(f"  Res {resolution}: {cell}")
            print(f"    Area: {area:.6f} km²")
            print(f"    Parent area: {parent_area:.6f} km²")
            print(f"    Children: {children_count} (total area: {children_area:.6f} km²)")


def main():
    """Run all hierarchical operation demonstrations."""
    print("🌍 Hierarchical Operations Example")
    print("=" * 50)
    print("Demonstrating hierarchical operations using tested H3 methods")
    print("=" * 50)
    
    demo_parent_child_relationships()
    demo_position_operations()
    demo_sub_center_operations()
    demo_hierarchy_path()
    demo_ancestors_descendants()
    demo_hierarchical_analysis()
    demo_multi_resolution_operations()
    
    print("\n✅ Hierarchical operations demonstration completed!")


if __name__ == "__main__":
    main() 