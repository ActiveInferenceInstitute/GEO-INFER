#!/usr/bin/env python3
"""
Data Conversion Example

Demonstrates H3 data conversion and multi-channel dataset fusion using tested methods.
Shows format conversion, data integration, and export capabilities.

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
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area
)

from conversion import (
    cell_to_geojson, geojson_to_cells, wkt_to_cells, cells_to_wkt,
    cells_to_geojson, cells_to_shapefile_data, cells_to_kml, cells_to_csv
)

from traversal import (
    grid_disk, grid_ring
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_geojson_conversion():
    """Demonstrate GeoJSON conversion operations."""
    print("🔹 GeoJSON Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cells
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
        latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
    ]
    
    # Convert individual cell to GeoJSON
    print("Individual Cell to GeoJSON:")
    individual_geojson_data = []
    for i, cell in enumerate(test_cells):
        geojson = cell_to_geojson(cell)
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        
        print(f"  Cell {i+1}: {cell}")
        print(f"    Type: {geojson['type']}")
        print(f"    Properties: {geojson['properties']}")
        print(f"    Center: ({lat:.4f}, {lng:.4f})")
        print(f"    Area: {area:.6f} km²")
        
        individual_geojson_data.append({
            "cell_index": i+1,
            "cell": cell,
            "geojson": geojson,
            "center": {"lat": lat, "lng": lng},
            "area_km2": area
        })
    
    # Convert multiple cells to GeoJSON FeatureCollection
    print("\nMultiple Cells to GeoJSON FeatureCollection:")
    feature_collection = cells_to_geojson(test_cells)
    print(f"  Type: {feature_collection['type']}")
    print(f"  Number of features: {len(feature_collection['features'])}")
    
    # Show first feature
    first_feature = feature_collection['features'][0]
    print(f"  First feature type: {first_feature['type']}")
    print(f"  First feature properties: {first_feature['properties']}")
    
    # Save GeoJSON conversion data
    geojson_data = {
        "individual_cells": individual_geojson_data,
        "feature_collection": feature_collection
    }
    
    output_file = output_dir / "04_geojson_conversion.json"
    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=2)
    print(f"✅ Saved GeoJSON conversion data to {output_file}")


def demo_wkt_conversion():
    """Demonstrate WKT conversion operations."""
    print("\n🔹 WKT Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cells
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
    ]
    
    # Convert cells to WKT
    wkt_output = cells_to_wkt(test_cells)
    print("Cells to WKT:")
    print(f"  WKT: {wkt_output[:100]}...")  # Show first 100 chars
    
    # Test WKT to cells conversion (simplified)
    print("\nWKT to Cells (simplified test):")
    # Note: This is a simplified test since WKT parsing requires additional libraries
    print("  WKT conversion requires proper WKT parser implementation")
    
    # Save WKT conversion data
    wkt_data = {
        "input_cells": test_cells,
        "wkt_output": wkt_output,
        "wkt_length": len(wkt_output)
    }
    
    output_file = output_dir / "04_wkt_conversion.json"
    with open(output_file, 'w') as f:
        json.dump(wkt_data, f, indent=2)
    print(f"✅ Saved WKT conversion data to {output_file}")


def demo_csv_conversion():
    """Demonstrate CSV conversion operations."""
    print("\n🔹 CSV Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cells
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
        latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
        latlng_to_cell(41.8781, -87.6298, 9),   # Chicago
        latlng_to_cell(25.7617, -80.1918, 9),   # Miami
    ]
    
    # Convert to CSV
    csv_output = cells_to_csv(test_cells)
    print("Cells to CSV:")
    print(csv_output)
    
    # Save CSV conversion data
    csv_data = {
        "input_cells": test_cells,
        "csv_output": csv_output,
        "csv_lines": len(csv_output.splitlines())
    }
    
    output_file = output_dir / "04_csv_conversion.json"
    with open(output_file, 'w') as f:
        json.dump(csv_data, f, indent=2)
    print(f"✅ Saved CSV conversion data to {output_file}")
    
    # Also save the actual CSV file
    csv_file = output_dir / "04_cells_data.csv"
    with open(csv_file, 'w') as f:
        f.write(csv_output)
    print(f"✅ Saved CSV file to {csv_file}")


def demo_kml_conversion():
    """Demonstrate KML conversion operations."""
    print("\n🔹 KML Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cells
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
    ]
    
    # Convert to KML
    kml_output = cells_to_kml(test_cells)
    print("Cells to KML:")
    print(f"  KML length: {len(kml_output)} characters")
    print(f"  First 200 chars: {kml_output[:200]}...")
    
    # Save KML conversion data
    kml_data = {
        "input_cells": test_cells,
        "kml_output": kml_output,
        "kml_length": len(kml_output)
    }
    
    output_file = output_dir / "04_kml_conversion.json"
    with open(output_file, 'w') as f:
        json.dump(kml_data, f, indent=2)
    print(f"✅ Saved KML conversion data to {output_file}")
    
    # Also save the actual KML file
    kml_file = output_dir / "04_cells.kml"
    with open(kml_file, 'w') as f:
        f.write(kml_output)
    print(f"✅ Saved KML file to {kml_file}")


def demo_shapefile_data():
    """Demonstrate shapefile data conversion."""
    print("\n🔹 Shapefile Data Conversion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Test cells
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
        latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
    ]
    
    # Convert to shapefile data
    shapefile_data = cells_to_shapefile_data(test_cells)
    print("Cells to Shapefile Data:")
    print(f"  Number of geometries: {len(shapefile_data['geometries'])}")
    print(f"  Number of properties: {len(shapefile_data['properties'])}")
    
    # Show first property
    first_property = shapefile_data['properties'][0]
    print(f"  First property: {first_property}")
    
    # Save shapefile data
    output_file = output_dir / "04_shapefile_data.json"
    with open(output_file, 'w') as f:
        json.dump(shapefile_data, f, indent=2)
    print(f"✅ Saved shapefile data to {output_file}")


def demo_multi_channel_dataset_fusion():
    """Demonstrate multi-channel dataset fusion."""
    print("\n🔹 Multi-Channel Dataset Fusion")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Simulate different data channels
    # Channel 1: Population data
    population_data = {
        latlng_to_cell(37.7749, -122.4194, 9): {"population": 873965, "density": 7200},
        latlng_to_cell(40.7128, -74.0060, 9): {"population": 8336817, "density": 11000},
        latlng_to_cell(34.0522, -118.2437, 9): {"population": 3979576, "density": 3200},
    }
    
    # Channel 2: Environmental data
    environmental_data = {
        latlng_to_cell(37.7749, -122.4194, 9): {"air_quality": 45, "temperature": 14.5},
        latlng_to_cell(40.7128, -74.0060, 9): {"air_quality": 52, "temperature": 12.8},
        latlng_to_cell(34.0522, -118.2437, 9): {"air_quality": 65, "temperature": 18.2},
    }
    
    # Channel 3: Infrastructure data
    infrastructure_data = {
        latlng_to_cell(37.7749, -122.4194, 9): {"hospitals": 12, "schools": 45, "parks": 23},
        latlng_to_cell(40.7128, -74.0060, 9): {"hospitals": 89, "schools": 234, "parks": 67},
        latlng_to_cell(34.0522, -118.2437, 9): {"hospitals": 34, "schools": 156, "parks": 89},
    }
    
    # Fusion: Combine all channels
    print("Multi-Channel Dataset Fusion:")
    print("Cell | Population | Environment | Infrastructure")
    print("-" * 70)
    
    all_cells = set(population_data.keys()) | set(environmental_data.keys()) | set(infrastructure_data.keys())
    
    fusion_data = []
    for cell in all_cells:
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        
        pop_data = population_data.get(cell, {})
        env_data = environmental_data.get(cell, {})
        infra_data = infrastructure_data.get(cell, {})
        
        print(f"{cell} | {pop_data.get('population', 'N/A'):9d} | "
              f"AQ:{env_data.get('air_quality', 'N/A'):2d}°C:{env_data.get('temperature', 'N/A'):4.1f} | "
              f"H:{infra_data.get('hospitals', 'N/A'):2d} S:{infra_data.get('schools', 'N/A'):3d} P:{infra_data.get('parks', 'N/A'):2d}")
        
        fusion_data.append({
            "cell": cell,
            "coordinates": {"lat": lat, "lng": lng},
            "area_km2": area,
            "population": pop_data.get('population'),
            "density": pop_data.get('density'),
            "air_quality": env_data.get('air_quality'),
            "temperature": env_data.get('temperature'),
            "hospitals": infra_data.get('hospitals'),
            "schools": infra_data.get('schools'),
            "parks": infra_data.get('parks')
        })
    
    # Create fused GeoJSON
    print("\nCreating Fused GeoJSON:")
    fused_features = []
    
    for cell in all_cells:
        # Get base GeoJSON
        base_geojson = cell_to_geojson(cell)
        
        # Add fused properties
        fused_properties = {
            **base_geojson['properties'],
            **population_data.get(cell, {}),
            **environmental_data.get(cell, {}),
            **infrastructure_data.get(cell, {})
        }
        
        base_geojson['properties'] = fused_properties
        fused_features.append(base_geojson)
    
    fused_geojson = {
        'type': 'FeatureCollection',
        'features': fused_features
    }
    
    print(f"  Created fused GeoJSON with {len(fused_features)} features")
    print(f"  Sample fused properties: {fused_features[0]['properties']}")
    
    # Save fusion data
    fusion_output = {
        "fusion_data": fusion_data,
        "fused_geojson": fused_geojson,
        "channels": {
            "population": population_data,
            "environmental": environmental_data,
            "infrastructure": infrastructure_data
        }
    }
    
    output_file = output_dir / "04_multi_channel_fusion.json"
    with open(output_file, 'w') as f:
        json.dump(fusion_output, f, indent=2)
    print(f"✅ Saved multi-channel fusion data to {output_file}")


def demo_data_export_formats():
    """Demonstrate data export in multiple formats."""
    print("\n🔹 Data Export Formats")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create test dataset
    test_cells = [
        latlng_to_cell(37.7749, -122.4194, 9),  # San Francisco
        latlng_to_cell(40.7128, -74.0060, 9),   # New York
        latlng_to_cell(34.0522, -118.2437, 9),  # Los Angeles
    ]
    
    # Export to different formats
    print("Exporting to multiple formats:")
    
    export_data = {}
    
    # 1. GeoJSON
    geojson_output = cells_to_geojson(test_cells)
    print(f"  1. GeoJSON: {len(geojson_output['features'])} features")
    export_data["geojson"] = {
        "features_count": len(geojson_output['features']),
        "size": len(json.dumps(geojson_output))
    }
    
    # 2. CSV
    csv_output = cells_to_csv(test_cells)
    print(f"  2. CSV: {len(csv_output.splitlines())} lines")
    export_data["csv"] = {
        "lines": len(csv_output.splitlines()),
        "size": len(csv_output)
    }
    
    # 3. KML
    kml_output = cells_to_kml(test_cells)
    print(f"  3. KML: {len(kml_output)} characters")
    export_data["kml"] = {
        "size": len(kml_output)
    }
    
    # 4. Shapefile data
    shapefile_output = cells_to_shapefile_data(test_cells)
    print(f"  4. Shapefile data: {len(shapefile_output['geometries'])} geometries")
    export_data["shapefile"] = {
        "geometries": len(shapefile_output['geometries']),
        "properties": len(shapefile_output['properties'])
    }
    
    # 5. WKT
    wkt_output = cells_to_wkt(test_cells)
    print(f"  5. WKT: {len(wkt_output)} characters")
    export_data["wkt"] = {
        "size": len(wkt_output)
    }
    
    # Save export format data
    output_file = output_dir / "04_export_formats.json"
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    print(f"✅ Saved export format data to {output_file}")


def demo_spatial_data_analysis():
    """Demonstrate spatial data analysis with converted data."""
    print("\n🔹 Spatial Data Analysis")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create a larger dataset for analysis
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    analysis_cells = grid_disk(center_cell, 2)
    
    print(f"Analyzing {len(analysis_cells)} cells:")
    
    # Analyze distribution
    distribution = analyze_cell_distribution(analysis_cells)
    print(f"  Distribution analysis: {distribution}")
    
    # Calculate spatial statistics
    stats = calculate_spatial_statistics(analysis_cells)
    print(f"  Spatial statistics: {stats}")
    
    # Convert to GeoJSON for visualization
    geojson_output = cells_to_geojson(analysis_cells)
    print(f"  Converted to GeoJSON: {len(geojson_output['features'])} features")
    
    # Export to CSV for analysis
    csv_output = cells_to_csv(analysis_cells)
    print(f"  Converted to CSV: {len(csv_output.splitlines())} lines")
    
    # Save spatial analysis data
    analysis_data = {
        "center_cell": center_cell,
        "analysis_cells": analysis_cells,
        "distribution": distribution,
        "statistics": stats,
        "geojson_features": len(geojson_output['features']),
        "csv_lines": len(csv_output.splitlines())
    }
    
    output_file = output_dir / "04_spatial_data_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis_data, f, indent=2)
    print(f"✅ Saved spatial data analysis to {output_file}")


def main():
    """Run all data conversion demonstrations."""
    print("🌍 Data Conversion Example")
    print("=" * 50)
    print("Demonstrating data conversion and multi-channel fusion using tested H3 methods")
    print("=" * 50)
    
    demo_geojson_conversion()
    demo_wkt_conversion()
    demo_csv_conversion()
    demo_kml_conversion()
    demo_shapefile_data()
    demo_multi_channel_dataset_fusion()
    demo_data_export_formats()
    demo_spatial_data_analysis()
    
    print("\n✅ Data conversion demonstration completed!")
    print("📁 All outputs saved to the 'output' directory")


if __name__ == "__main__":
    main() 