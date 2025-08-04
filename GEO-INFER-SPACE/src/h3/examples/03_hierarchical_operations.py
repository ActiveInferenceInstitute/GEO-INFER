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
import json
import csv
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_area, get_resolution
)

from indexing import (
    cell_to_center_child, cell_to_children, cell_to_parent
)

from hierarchy import (
    get_hierarchy_path, get_ancestors, get_descendants
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_parent_child_relationships():
    """Demonstrate parent-child relationships."""
    print("🔹 Parent-Child Relationships")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
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
    children_data = []
    for i, child in enumerate(children[:5]):
        lat, lng = cell_to_latlng(child)
        area = cell_area(child, 'km^2')
        print(f"  Child {i+1}: {child} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
        children_data.append({
            "child_index": i+1,
            "cell": child,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Get center child
    center_child = cell_to_center_child(start_cell, 10)
    print(f"Center child: {center_child}")
    
    # Verify parent-child relationship
    center_parent = cell_to_parent(center_child, 9)
    print(f"Center child's parent: {center_parent}")
    print(f"Matches original cell: {center_parent == start_cell}")
    
    # Save parent-child relationships to JSON
    relationship_data = {
        "start_cell": start_cell,
        "parent_cell": parent_cell,
        "children_count": len(children),
        "children_sample": children_data,
        "center_child": center_child,
        "center_child_parent": center_parent,
        "parent_child_match": center_parent == start_cell
    }
    
    output_file = output_dir / "03_parent_child_relationships.json"
    with open(output_file, 'w') as f:
        json.dump(relationship_data, f, indent=2)
    print(f"✅ Saved parent-child relationships to {output_file}")


def demo_hierarchy_path():
    """Demonstrate hierarchical path operations."""
    print("\n🔹 Hierarchy Path Operations")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cell at resolution 9
    start_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Starting cell: {start_cell}")
    
    # Get path to resolution 6 (going up)
    up_path = get_hierarchy_path(start_cell, 6)
    print(f"Path to resolution 6 (up):")
    up_path_data = []
    for i, cell in enumerate(up_path):
        res = get_resolution(cell)
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        print(f"  Res {res}: {cell} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
        up_path_data.append({
            "index": i,
            "cell": cell,
            "resolution": res,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Get path to resolution 12 (going down)
    down_path = get_hierarchy_path(start_cell, 12)
    print(f"\nPath to resolution 12 (down):")
    down_path_data = []
    for i, cell in enumerate(down_path):
        res = get_resolution(cell)
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        print(f"  Res {res}: {cell} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
        down_path_data.append({
            "index": i,
            "cell": cell,
            "resolution": res,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Save hierarchy path data to JSON
    path_data = {
        "start_cell": start_cell,
        "up_path": {
            "target_resolution": 6,
            "cells": up_path_data
        },
        "down_path": {
            "target_resolution": 12,
            "cells": down_path_data
        }
    }
    
    output_file = output_dir / "03_hierarchy_path.json"
    with open(output_file, 'w') as f:
        json.dump(path_data, f, indent=2)
    print(f"✅ Saved hierarchy path data to {output_file}")


def demo_ancestors_descendants():
    """Demonstrate ancestor and descendant operations."""
    print("\n🔹 Ancestors and Descendants")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cell
    test_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Test cell: {test_cell}")
    
    # Get ancestors (up to 3 levels)
    ancestors = get_ancestors(test_cell, 3)
    print(f"Ancestors (up to 3 levels):")
    ancestors_data = []
    for i, ancestor in enumerate(ancestors):
        res = get_resolution(ancestor)
        lat, lng = cell_to_latlng(ancestor)
        area = cell_area(ancestor, 'km^2')
        print(f"  Level {i+1} (res {res}): {ancestor} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
        ancestors_data.append({
            "level": i+1,
            "cell": ancestor,
            "resolution": res,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Get descendants (up to 10 cells)
    descendants = get_descendants(test_cell, 10)
    print(f"\nDescendants (up to 10 cells):")
    descendants_data = []
    for i, descendant in enumerate(descendants):
        res = get_resolution(descendant)
        lat, lng = cell_to_latlng(descendant)
        area = cell_area(descendant, 'km^2')
        print(f"  Descendant {i+1} (res {res}): {descendant} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
        descendants_data.append({
            "index": i+1,
            "cell": descendant,
            "resolution": res,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Save ancestors and descendants to JSON
    hierarchy_data = {
        "test_cell": test_cell,
        "ancestors": {
            "count": len(ancestors),
            "cells": ancestors_data
        },
        "descendants": {
            "count": len(descendants),
            "cells": descendants_data
        }
    }
    
    output_file = output_dir / "03_ancestors_descendants.json"
    with open(output_file, 'w') as f:
        json.dump(hierarchy_data, f, indent=2)
    print(f"✅ Saved ancestors and descendants to {output_file}")


def demo_hierarchical_analysis():
    """Demonstrate hierarchical analysis across multiple resolutions."""
    print("\n🔹 Hierarchical Analysis")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test location
    lat, lng = 37.7749, -122.4194
    
    # Analyze hierarchy from resolution 0 to 12
    print("Hierarchical Analysis from Resolution 0 to 12:")
    print("Resolution | Cell Index | Area (km²) | Children")
    print("-" * 60)
    
    hierarchy_analysis = []
    
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
        
        hierarchy_analysis.append({
            "resolution": resolution,
            "cell": cell,
            "area_km2": area,
            "children_count": children_count
        })
    
    # Analyze area scaling
    print(f"\nArea Scaling Analysis:")
    areas = []
    area_scaling = []
    for resolution in range(0, 13):
        cell = latlng_to_cell(lat, lng, resolution)
        area = cell_area(cell, 'km^2')
        areas.append(area)
    
    for i in range(len(areas) - 1):
        ratio = areas[i] / areas[i + 1]
        print(f"  Res {i} to {i+1}: {ratio:.2f}x larger")
        area_scaling.append({
            "from_resolution": i,
            "to_resolution": i+1,
            "area_ratio": ratio
        })
    
    # Save hierarchical analysis to JSON
    analysis_data = {
        "location": {"lat": lat, "lng": lng},
        "hierarchy_analysis": hierarchy_analysis,
        "area_scaling": area_scaling
    }
    
    output_file = output_dir / "03_hierarchical_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✅ Saved hierarchical analysis to {output_file}")


def demo_multi_resolution_operations():
    """Demonstrate operations across multiple resolutions."""
    print("\n🔹 Multi-Resolution Operations")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test locations
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437)
    ]
    
    multi_res_data = []
    
    for city, lat, lng in locations:
        print(f"\n📍 {city}:")
        city_data = {"city": city, "coordinates": {"lat": lat, "lng": lng}, "resolutions": {}}
        
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
            
            city_data["resolutions"][resolution] = {
                "cell": cell,
                "area_km2": area,
                "parent_area_km2": parent_area,
                "children_count": children_count,
                "children_area_km2": children_area
            }
        
        multi_res_data.append(city_data)
    
    # Save multi-resolution operations to JSON
    output_file = output_dir / "03_multi_resolution_operations.json"
    with open(output_file, 'w') as f:
        json.dump(multi_res_data, f, indent=2)
    print(f"✅ Saved multi-resolution operations to {output_file}")


def main():
    """Run all hierarchical operation demonstrations."""
    print("🌍 Hierarchical Operations Example")
    print("=" * 50)
    print("Demonstrating hierarchical operations using tested H3 methods")
    print("=" * 50)
    
    demo_parent_child_relationships()
    demo_hierarchy_path()
    demo_ancestors_descendants()
    demo_hierarchical_analysis()
    demo_multi_resolution_operations()
    
    print("\n✅ Hierarchical operations demonstration completed!")
    print("📁 All outputs saved to the 'output' directory")


if __name__ == "__main__":
    main() 