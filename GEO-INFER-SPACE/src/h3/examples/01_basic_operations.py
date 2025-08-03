#!/usr/bin/env python3
"""
Basic H3 Operations Example

Demonstrates fundamental H3 operations using tested methods.
Shows coordinate conversion, cell properties, and basic geometric operations.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    get_resolution, is_valid_cell, is_pentagon
)

from constants import (
    MAX_H3_RES, MIN_H3_RES
)


def demo_coordinate_conversion():
    """Demonstrate coordinate to cell conversion."""
    print("🔹 Coordinate Conversion")
    print("-" * 40)
    
    # Test locations
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918)
    ]
    
    for city, lat, lng in locations:
        print(f"\n📍 {city}:")
        
        # Convert to H3 cells at different resolutions
        for resolution in [0, 5, 9, 12]:
            cell = latlng_to_cell(lat, lng, resolution)
            center_lat, center_lng = cell_to_latlng(cell)
            area = cell_area(cell, 'km^2')
            
            print(f"  Resolution {resolution}: {cell}")
            print(f"    Center: ({center_lat:.4f}, {center_lng:.4f})")
            print(f"    Area: {area:.6f} km²")
            print(f"    Is pentagon: {is_pentagon(cell)}")


def demo_cell_properties():
    """Demonstrate cell property analysis."""
    print("\n🔹 Cell Properties Analysis")
    print("-" * 40)
    
    # Test cell at resolution 9
    test_cell = latlng_to_cell(37.7749, -122.4194, 9)
    
    print(f"Test Cell: {test_cell}")
    print(f"Resolution: {get_resolution(test_cell)}")
    print(f"Area: {cell_area(test_cell, 'km^2'):.6f} km²")
    print(f"Is valid: {is_valid_cell(test_cell)}")
    print(f"Is pentagon: {is_pentagon(test_cell)}")
    
    # Get cell boundary
    boundary = cell_to_boundary(test_cell)
    print(f"Boundary vertices: {len(boundary)}")
    print("Boundary coordinates:")
    for i, (lat, lng) in enumerate(boundary):
        print(f"  Vertex {i}: ({lat:.6f}, {lng:.6f})")


def demo_resolution_comparison():
    """Demonstrate resolution comparison."""
    print("\n🔹 Resolution Comparison")
    print("-" * 40)
    
    # Test location
    lat, lng = 37.7749, -122.4194
    
    print("Resolution | Cell Index | Area (km²) | Edge Length (km)")
    print("-" * 60)
    
    for resolution in range(MIN_H3_RES, MAX_H3_RES + 1):
        cell = latlng_to_cell(lat, lng, resolution)
        area = cell_area(cell, 'km^2')
        
        # Calculate approximate edge length from area
        # For regular hexagon: area = (3√3/2) * edge_length²
        edge_length = (area * 2 / (3 * 3**0.5))**0.5
        
        print(f"{resolution:10d} | {cell:15s} | {area:10.6f} | {edge_length:15.6f}")


def demo_validation():
    """Demonstrate input validation."""
    print("\n🔹 Input Validation")
    print("-" * 40)
    
    # Valid inputs
    valid_cell = latlng_to_cell(37.7749, -122.4194, 9)
    print(f"Valid cell '{valid_cell}': {is_valid_cell(valid_cell)}")
    
    # Invalid inputs
    invalid_cells = [
        "invalid_cell",
        "89283082e73fff",  # Too short
        "89283082e73fffff",  # Too long
        "89283082e73fffg",  # Invalid character
    ]
    
    for invalid_cell in invalid_cells:
        print(f"Invalid cell '{invalid_cell}': {is_valid_cell(invalid_cell)}")


def main():
    """Run all basic operation demonstrations."""
    print("🌍 Basic H3 Operations Example")
    print("=" * 50)
    print("Demonstrating fundamental H3 operations using tested methods")
    print("=" * 50)
    
    demo_coordinate_conversion()
    demo_cell_properties()
    demo_resolution_comparison()
    demo_validation()
    
    print("\n✅ Basic operations demonstration completed!")


if __name__ == "__main__":
    main() 