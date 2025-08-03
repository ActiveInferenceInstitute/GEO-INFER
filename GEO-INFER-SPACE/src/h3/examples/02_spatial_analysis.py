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

from h3 import (
    # Core operations
    latlng_to_cell, cell_to_latlng, cell_area,
    
    # Traversal operations
    grid_disk, grid_ring, grid_path_cells, grid_distance,
    great_circle_distance, grid_neighbors,
    
    # Analysis operations
    analyze_cell_distribution, calculate_spatial_statistics,
    find_nearest_cell, calculate_cell_density, analyze_resolution_distribution
)


def demo_grid_operations():
    """Demonstrate grid disk and ring operations."""
    print("🔹 Grid Operations")
    print("-" * 40)
    
    # Test cell
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Center cell: {center_cell}")
    
    # Grid disk (cells within k steps)
    for k in [1, 2, 3]:
        disk_cells = grid_disk(center_cell, k)
        print(f"\nGrid disk (k={k}):")
        print(f"  Number of cells: {len(disk_cells)}")
        print(f"  Total area: {sum(cell_area(cell, 'km^2') for cell in disk_cells):.6f} km²")
        
        # Show first few cells
        for i, cell in enumerate(disk_cells[:5]):
            lat, lng = cell_to_latlng(cell)
            area = cell_area(cell, 'km^2')
            print(f"    Cell {i+1}: {cell} ({lat:.4f}, {lng:.4f}) - {area:.6f} km²")
    
    # Grid ring (cells exactly k steps away)
    for k in [1, 2]:
        ring_cells = grid_ring(center_cell, k)
        print(f"\nGrid ring (k={k}):")
        print(f"  Number of cells: {len(ring_cells)}")
        print(f"  Average area: {sum(cell_area(cell, 'km^2') for cell in ring_cells) / len(ring_cells):.6f} km²")


def demo_distance_calculations():
    """Demonstrate distance calculations."""
    print("\n🔹 Distance Calculations")
    print("-" * 40)
    
    # Test locations
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918)
    ]
    
    # Convert to cells at resolution 9
    cells = []
    for city, lat, lng in locations:
        cell = latlng_to_cell(lat, lng, 9)
        cells.append((city, cell, lat, lng))
    
    # Calculate distances between all pairs
    print("Great Circle Distances (km):")
    print("City 1 -> City 2 | Distance")
    print("-" * 40)
    
    for i, (city1, cell1, lat1, lng1) in enumerate(cells):
        for j, (city2, cell2, lat2, lng2) in enumerate(cells[i+1:], i+1):
            # Great circle distance
            gc_distance = great_circle_distance(lat1, lng1, lat2, lng2, 'km')
            
            # Grid distance
            grid_dist = grid_distance(cell1, cell2)
            
            print(f"{city1:15s} -> {city2:15s} | {gc_distance:8.1f} km (grid: {grid_dist})")


def demo_path_analysis():
    """Demonstrate path finding between cells."""
    print("\n🔹 Path Analysis")
    print("-" * 40)
    
    # Test path: San Francisco to New York
    sf_cell = latlng_to_cell(37.7749, -122.4194, 9)
    ny_cell = latlng_to_cell(40.7128, -74.0060, 9)
    
    print(f"Path from San Francisco to New York:")
    print(f"  SF Cell: {sf_cell}")
    print(f"  NY Cell: {ny_cell}")
    
    # Find path
    path_cells = grid_path_cells(sf_cell, ny_cell)
    print(f"  Path length: {len(path_cells)} cells")
    print(f"  Grid distance: {grid_distance(sf_cell, ny_cell)} steps")
    
    # Calculate path statistics
    path_areas = [cell_area(cell, 'km^2') for cell in path_cells]
    total_area = sum(path_areas)
    avg_area = total_area / len(path_areas)
    
    print(f"  Total path area: {total_area:.6f} km²")
    print(f"  Average cell area: {avg_area:.6f} km²")
    
    # Show path coordinates
    print("  Path coordinates:")
    for i, cell in enumerate(path_cells[::10]):  # Show every 10th cell
        lat, lng = cell_to_latlng(cell)
        print(f"    Step {i*10}: ({lat:.4f}, {lng:.4f})")


def demo_spatial_statistics():
    """Demonstrate spatial statistics analysis."""
    print("\n🔹 Spatial Statistics")
    print("-" * 40)
    
    # Create a set of cells around San Francisco
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    disk_cells = grid_disk(center_cell, 3)
    
    print(f"Analyzing {len(disk_cells)} cells around San Francisco:")
    
    # Analyze cell distribution
    distribution = analyze_cell_distribution(disk_cells)
    print(f"  Total cells: {distribution['total_cells']}")
    print(f"  Resolution distribution: {distribution['resolutions']}")
    print(f"  Pentagons: {distribution['pentagons']}")
    print(f"  Class III cells: {distribution['class_iii_cells']}")
    print(f"  Total area: {distribution['total_area_km2']:.6f} km²")
    print(f"  Average area: {distribution['avg_area_km2']:.6f} km²")
    
    # Calculate spatial statistics
    stats = calculate_spatial_statistics(disk_cells)
    print(f"\nSpatial Statistics:")
    print(f"  Centroid: {stats['centroid']}")
    print(f"  Total area: {stats['total_area_km2']:.6f} km²")
    print(f"  Compactness: {stats['compactness']:.4f}")
    
    # Analyze resolution distribution
    res_analysis = analyze_resolution_distribution(disk_cells)
    print(f"\nResolution Analysis:")
    print(f"  Min resolution: {res_analysis['min_resolution']}")
    print(f"  Max resolution: {res_analysis['max_resolution']}")
    print(f"  Average resolution: {res_analysis['avg_resolution']:.2f}")
    print(f"  Resolution std dev: {res_analysis['resolution_std']:.2f}")


def demo_nearest_cell_analysis():
    """Demonstrate nearest cell finding."""
    print("\n🔹 Nearest Cell Analysis")
    print("-" * 40)
    
    # Create a set of reference cells
    reference_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
        latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
    ]
    
    # Test points
    test_points = [
        (37.7849, -122.4094),  # Near San Francisco
        (40.7228, -73.9960),   # Near New York
        (34.0622, -118.2337),  # Near Los Angeles
        (39.7392, -104.9903),  # Denver (far from all)
    ]
    
    for i, (lat, lng) in enumerate(test_points):
        nearest_cell, distance = find_nearest_cell(lat, lng, reference_cells)
        nearest_lat, nearest_lng = cell_to_latlng(nearest_cell)
        
        print(f"Test point {i+1} ({lat:.4f}, {lng:.4f}):")
        print(f"  Nearest cell: {nearest_cell}")
        print(f"  Nearest center: ({nearest_lat:.4f}, {nearest_lng:.4f})")
        print(f"  Distance: {distance:.6f} km")


def demo_density_analysis():
    """Demonstrate cell density calculations."""
    print("\n🔹 Cell Density Analysis")
    print("-" * 40)
    
    # Create cells at different resolutions
    center_lat, center_lng = 37.7749, -122.4194
    
    for resolution in [7, 9, 11]:
        center_cell = latlng_to_cell(center_lat, center_lng, resolution)
        disk_cells = grid_disk(center_cell, 2)
        
        # Calculate density
        density = calculate_cell_density(disk_cells)
        
        print(f"Resolution {resolution}:")
        print(f"  Number of cells: {len(disk_cells)}")
        print(f"  Cell density: {density:.2f} cells/km²")
        
        # Calculate density with custom area
        custom_area = 100.0  # 100 km²
        custom_density = calculate_cell_density(disk_cells, custom_area)
        print(f"  Density in {custom_area} km² area: {custom_density:.2f} cells/km²")


def main():
    """Run all spatial analysis demonstrations."""
    print("🌍 Spatial Analysis Example")
    print("=" * 50)
    print("Demonstrating advanced spatial analysis using tested H3 methods")
    print("=" * 50)
    
    demo_grid_operations()
    demo_distance_calculations()
    demo_path_analysis()
    demo_spatial_statistics()
    demo_nearest_cell_analysis()
    demo_density_analysis()
    
    print("\n✅ Spatial analysis demonstration completed!")


if __name__ == "__main__":
    main() 