#!/usr/bin/env python3
"""
Spatial Analysis Example

Demonstrates advanced spatial analysis using tested H3 methods.
Shows grid operations, distance calculations, and spatial statistics.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_area
)

from traversal import (
    grid_disk, grid_ring, great_circle_distance
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics,
    find_nearest_cell, calculate_cell_density
)

from visualization import (
    create_cell_map, create_density_heatmap
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_grid_and_distance_analysis():
    """Demonstrate grid operations and distance calculations."""
    print("🔹 Grid Operations & Distance Analysis")
    print("-" * 50)
    
    output_dir = ensure_output_dir()
    
    # Test cell
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Center cell: {center_cell}")
    
    # Grid disk and ring operations
    disk_cells = grid_disk(center_cell, 2)
    ring_cells = grid_ring(center_cell, 1)
    
    print(f"Grid disk (k=2): {len(disk_cells)} cells")
    print(f"Grid ring (k=1): {len(ring_cells)} cells")
    
    # Distance calculations between cities
    cities = [
        ("San Francisco", 37.7749, -122.4194),
        ("Los Angeles", 34.0522, -118.2437),
        ("New York", 40.7128, -74.0060)
    ]
    
    cells = [(city, latlng_to_cell(lat, lng, 9), lat, lng) for city, lat, lng in cities]
    
    print("\nGreat Circle Distances:")
    distance_data = []
    for i, (city1, cell1, lat1, lng1) in enumerate(cells):
        for j, (city2, cell2, lat2, lng2) in enumerate(cells[i+1:], i+1):
            gc_distance = great_circle_distance(lat1, lng1, lat2, lng2, 'km')
            print(f"  {city1} -> {city2}: {gc_distance:.1f} km")
            
            distance_data.append({
                "city1": city1, "city2": city2,
                "distance_km": gc_distance
            })
    
    # Save data
    grid_data = {
        "center_cell": center_cell,
        "disk_cells": disk_cells,
        "ring_cells": ring_cells,
        "distance_calculations": distance_data
    }
    
    output_file = output_dir / "02_grid_and_distance.json"
    with open(output_file, 'w') as f:
        json.dump(grid_data, f, indent=2)
    print(f"✅ Saved grid and distance data to {output_file}")
    
    # Create visualization
    all_cells = disk_cells + [cell for _, cell, _, _ in cells]
    map_path = output_dir / "02_grid_and_distance_map.png"
    create_cell_map(all_cells, title="Grid & Distance Analysis", output_path=map_path)


def demo_spatial_statistics():
    """Demonstrate spatial statistics analysis."""
    print("\n🔹 Spatial Statistics")
    print("-" * 50)
    
    output_dir = ensure_output_dir()
    
    # Spatial statistics on a disk
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    disk_cells = grid_disk(center_cell, 3)
    
    distribution = analyze_cell_distribution(disk_cells)
    stats = calculate_spatial_statistics(disk_cells)
    
    print(f"Spatial Statistics on {len(disk_cells)} cells:")
    print(f"  Total area: {distribution['total_area_km2']:.6f} km²")
    print(f"  Average area: {distribution['avg_area_km2']:.6f} km²")
    print(f"  Compactness: {stats['compactness']:.4f}")
    
    # Save data
    spatial_data = {
        "center_cell": center_cell,
        "analysis_cells": disk_cells,
        "distribution": distribution,
        "statistics": stats
    }
    
    output_file = output_dir / "02_spatial_statistics.json"
    with open(output_file, 'w') as f:
        json.dump(spatial_data, f, indent=2)
    print(f"✅ Saved spatial statistics to {output_file}")
    
    # Create heatmap
    heatmap_path = output_dir / "02_spatial_heatmap.png"
    create_density_heatmap(disk_cells, center_cell, radius=3, 
                          title="Spatial Statistics Heatmap", output_path=heatmap_path)


def demo_density_analysis():
    """Demonstrate density analysis and nearest cell finding."""
    print("\n🔹 Density & Nearest Cell Analysis")
    print("-" * 50)
    
    output_dir = ensure_output_dir()
    
    # Density analysis at different resolutions
    center_lat, center_lng = 37.7749, -122.4194
    
    density_data = []
    all_cells = []
    
    for resolution in [8, 9, 10]:
        center_cell = latlng_to_cell(center_lat, center_lng, resolution)
        disk_cells = grid_disk(center_cell, 2)
        density = calculate_cell_density(disk_cells)
        
        print(f"Resolution {resolution}: {len(disk_cells)} cells, {density:.2f} cells/km²")
        
        density_data.append({
            "resolution": resolution,
            "cell_count": len(disk_cells),
            "density_cells_per_km2": density
        })
        all_cells.extend(disk_cells)
    
    # Nearest cell analysis
    reference_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
    ]
    
    test_points = [
        (37.7849, -122.4094),  # Near San Francisco
        (40.7228, -73.9960),   # Near New York
    ]
    
    nearest_analysis = []
    for i, (lat, lng) in enumerate(test_points):
        nearest_cell, distance = find_nearest_cell(lat, lng, reference_cells)
        print(f"Test point {i+1}: nearest to {nearest_cell} ({distance:.6f} km)")
        
        nearest_analysis.append({
            "test_point": {"lat": lat, "lng": lng},
            "nearest_cell": nearest_cell,
            "distance_km": distance
        })
    
    # Save data
    analysis_data = {
        "density_analysis": density_data,
        "nearest_cell_analysis": nearest_analysis
    }
    
    output_file = output_dir / "02_density_and_nearest.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✅ Saved density and nearest cell data to {output_file}")
    
    # Create visualization
    map_path = output_dir / "02_density_and_nearest_map.png"
    create_cell_map(all_cells, title="Density & Nearest Analysis", output_path=map_path)


def main():
    """Run all spatial analysis demonstrations."""
    print("🌍 Spatial Analysis Example")
    print("=" * 50)
    print("Demonstrating advanced spatial analysis using tested H3 methods")
    print("=" * 50)
    
    demo_grid_and_distance_analysis()
    demo_spatial_statistics()
    demo_density_analysis()
    
    print("\n✅ Spatial analysis demonstration completed!")
    print("📁 All outputs saved to the 'output' directory")
    print("📊 Generated visualizations:")
    print("   - 02_grid_and_distance_map.png")
    print("   - 02_spatial_heatmap.png")
    print("   - 02_density_and_nearest_map.png")


if __name__ == "__main__":
    main() 