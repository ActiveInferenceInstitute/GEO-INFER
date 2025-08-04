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
import json
import csv
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

from visualization import (
    create_cell_map, create_resolution_chart, create_area_distribution_plot, create_comparison_plot
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_coordinate_conversion():
    """Demonstrate coordinate to cell conversion."""
    print("🔹 Coordinate Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test locations
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918)
    ]
    
    conversion_data = []
    all_cells = []
    
    for city, lat, lng in locations:
        print(f"\n📍 {city}:")
        
        city_data = {"city": city, "original_coordinates": {"lat": lat, "lng": lng}, "resolutions": {}}
        
        # Convert to H3 cells at different resolutions
        for resolution in [0, 5, 9, 12]:
            cell = latlng_to_cell(lat, lng, resolution)
            center_lat, center_lng = cell_to_latlng(cell)
            area = cell_area(cell, 'km^2')
            
            print(f"  Resolution {resolution}: {cell}")
            print(f"    Center: ({center_lat:.4f}, {center_lng:.4f})")
            print(f"    Area: {area:.6f} km²")
            print(f"    Is pentagon: {is_pentagon(cell)}")
            
            all_cells.append(cell)
            
            city_data["resolutions"][resolution] = {
                "cell": cell,
                "center": {"lat": center_lat, "lng": center_lng},
                "area_km2": area,
                "is_pentagon": is_pentagon(cell)
            }
        
        conversion_data.append(city_data)
    
    # Save conversion data to JSON
    output_file = output_dir / "01_coordinate_conversion.json"
    with open(output_file, 'w') as f:
        json.dump(conversion_data, f, indent=2)
    print(f"\n✅ Saved coordinate conversion data to {output_file}")
    
    # Create visualization of all cells
    map_path = output_dir / "01_coordinate_conversion_map.png"
    create_cell_map(all_cells, title="Coordinate Conversion Map", output_path=map_path)
    
    # Create resolution chart
    chart_path = output_dir / "01_resolution_distribution.png"
    create_resolution_chart(all_cells, title="Resolution Distribution", output_path=chart_path)


def demo_cell_properties():
    """Demonstrate cell property analysis."""
    print("\n🔹 Cell Properties Analysis")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
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
    
    # Save cell properties to JSON
    cell_properties = {
        "cell": test_cell,
        "resolution": get_resolution(test_cell),
        "area_km2": cell_area(test_cell, 'km^2'),
        "is_valid": is_valid_cell(test_cell),
        "is_pentagon": is_pentagon(test_cell),
        "center": cell_to_latlng(test_cell),
        "boundary": boundary
    }
    
    output_file = output_dir / "01_cell_properties.json"
    with open(output_file, 'w') as f:
        json.dump(cell_properties, f, indent=2)
    print(f"✅ Saved cell properties to {output_file}")
    
    # Create visualization of the cell
    map_path = output_dir / "01_cell_properties_map.png"
    create_cell_map([test_cell], title="Cell Properties Map", output_path=map_path)


def demo_resolution_comparison():
    """Demonstrate resolution comparison."""
    print("\n🔹 Resolution Comparison")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test location
    lat, lng = 37.7749, -122.4194
    
    print("Resolution | Cell Index | Area (km²) | Edge Length (km)")
    print("-" * 60)
    
    resolution_data = []
    all_cells = []
    
    for resolution in range(MIN_H3_RES, MAX_H3_RES + 1):
        cell = latlng_to_cell(lat, lng, resolution)
        area = cell_area(cell, 'km^2')
        all_cells.append(cell)
        
        # Calculate approximate edge length from area
        # For regular hexagon: area = (3√3/2) * edge_length²
        edge_length = (area * 2 / (3 * 3**0.5))**0.5
        
        print(f"{resolution:10d} | {cell:15s} | {area:10.6f} | {edge_length:15.6f}")
        
        resolution_data.append({
            "resolution": resolution,
            "cell": cell,
            "area_km2": area,
            "edge_length_km": edge_length
        })
    
    # Save resolution comparison to CSV
    output_file = output_dir / "01_resolution_comparison.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["resolution", "cell", "area_km2", "edge_length_km"])
        writer.writeheader()
        writer.writerows(resolution_data)
    print(f"✅ Saved resolution comparison to {output_file}")
    
    # Create area distribution plot
    plot_path = output_dir / "01_area_distribution.png"
    create_area_distribution_plot(all_cells, title="Area Distribution by Resolution", output_path=plot_path)


def demo_validation():
    """Demonstrate input validation."""
    print("\n🔹 Input Validation")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
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
    
    validation_results = []
    
    for invalid_cell in invalid_cells:
        is_valid = is_valid_cell(invalid_cell)
        print(f"Invalid cell '{invalid_cell}': {is_valid}")
        validation_results.append({
            "cell": invalid_cell,
            "is_valid": is_valid,
            "reason": "Invalid format" if not is_valid else "Valid"
        })
    
    # Save validation results to JSON
    output_file = output_dir / "01_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(validation_results, f, indent=2)
    print(f"✅ Saved validation results to {output_file}")
    
    # Create comparison plot of valid vs invalid cells
    valid_cells = [valid_cell]
    comparison_path = output_dir / "01_validation_comparison.png"
    create_comparison_plot([valid_cells, []], ["Valid Cells", "Invalid Cells"], 
                          title="Validation Comparison", output_path=comparison_path)


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
    print("📁 All outputs saved to the 'output' directory")
    print("📊 Generated visualizations:")
    print("   - 01_coordinate_conversion_map.png")
    print("   - 01_resolution_distribution.png")
    print("   - 01_cell_properties_map.png")
    print("   - 01_area_distribution.png")
    print("   - 01_validation_comparison.png")


if __name__ == "__main__":
    main() 