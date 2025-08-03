#!/usr/bin/env python3
"""
Visualization Outputs Example

Demonstrates static, animated, and interactive visualizations using tested H3 methods.
Shows various visualization techniques and output formats.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import json
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from h3 import (
    # Core operations
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    
    # Traversal operations
    grid_disk, grid_ring, grid_path_cells, grid_distance,
    
    # Conversion operations
    cells_to_geojson, cells_to_csv,
    
    # Analysis operations
    analyze_cell_distribution, calculate_spatial_statistics
)


def demo_static_visualization():
    """Demonstrate static visualization outputs."""
    print("🔹 Static Visualization")
    print("-" * 40)
    
    # Create test dataset
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    cells = grid_disk(center_cell, 3)
    
    print(f"Creating static visualization for {len(cells)} cells:")
    
    # 1. Generate GeoJSON for web mapping
    geojson_output = cells_to_geojson(cells)
    print(f"  1. GeoJSON: {len(geojson_output['features'])} features")
    
    # 2. Generate CSV for data analysis
    csv_output = cells_to_csv(cells)
    print(f"  2. CSV: {len(csv_output.splitlines())} lines")
    
    # 3. Generate summary statistics
    distribution = analyze_cell_distribution(cells)
    stats = calculate_spatial_statistics(cells)
    
    print(f"  3. Summary Statistics:")
    print(f"     Total cells: {distribution['total_cells']}")
    print(f"     Total area: {distribution['total_area_km2']:.6f} km²")
    print(f"     Average area: {distribution['avg_area_km2']:.6f} km²")
    print(f"     Centroid: {stats['centroid']}")
    print(f"     Compactness: {stats['compactness']:.4f}")
    
    # 4. Generate cell properties table
    print(f"  4. Cell Properties Table:")
    print(f"     Cell Index | Center Coordinates | Area (km²)")
    print(f"     {'-' * 50}")
    for i, cell in enumerate(cells[:10]):  # Show first 10
        lat, lng = cell_to_latlng(cell)
        area = cell_area(cell, 'km^2')
        print(f"     {cell} | ({lat:.4f}, {lng:.4f}) | {area:.6f}")
    
    if len(cells) > 10:
        print(f"     ... and {len(cells) - 10} more cells")


def demo_animated_visualization():
    """Demonstrate animated visualization outputs."""
    print("\n🔹 Animated Visualization")
    print("-" * 40)
    
    # Create animation frames
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    
    print("Creating animation frames:")
    
    # 1. Grid expansion animation
    print("  1. Grid Expansion Animation:")
    expansion_frames = []
    for k in range(0, 4):
        frame_cells = grid_disk(center_cell, k)
        frame_data = {
            'frame': k,
            'cells': frame_cells,
            'cell_count': len(frame_cells),
            'total_area': sum(cell_area(cell, 'km^2') for cell in frame_cells)
        }
        expansion_frames.append(frame_data)
        print(f"    Frame {k}: {len(frame_cells)} cells, {frame_data['total_area']:.6f} km²")
    
    # 2. Resolution transition animation
    print("  2. Resolution Transition Animation:")
    transition_frames = []
    for resolution in range(6, 12):
        frame_cell = latlng_to_cell(37.7749, -122.4194, resolution)
        frame_data = {
            'frame': resolution - 6,
            'resolution': resolution,
            'cell': frame_cell,
            'area': cell_area(frame_cell, 'km^2')
        }
        transition_frames.append(frame_data)
        print(f"    Frame {resolution-6}: Res {resolution}, {frame_cell}, {frame_data['area']:.6f} km²")
    
    # 3. Path animation
    print("  3. Path Animation:")
    end_cell = latlng_to_cell(40.7128, -74.0060, 9)  # New York
    path_cells = grid_path_cells(center_cell, end_cell)
    
    path_frames = []
    for i, cell in enumerate(path_cells[::5]):  # Sample every 5th cell
        frame_data = {
            'frame': i,
            'cell': cell,
            'progress': i / (len(path_cells) // 5),
            'coordinates': cell_to_latlng(cell)
        }
        path_frames.append(frame_data)
        print(f"    Frame {i}: {cell}, Progress: {frame_data['progress']:.2f}")
    
    # Generate animation data
    animation_data = {
        'expansion': expansion_frames,
        'transition': transition_frames,
        'path': path_frames
    }
    
    print(f"  Generated {len(expansion_frames)} expansion frames")
    print(f"  Generated {len(transition_frames)} transition frames")
    print(f"  Generated {len(path_frames)} path frames")


def demo_interactive_visualization():
    """Demonstrate interactive visualization outputs."""
    print("\n🔹 Interactive Visualization")
    print("-" * 40)
    
    # Create interactive dataset
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918)
    ]
    
    print("Creating interactive visualization data:")
    
    # 1. Generate interactive GeoJSON
    interactive_features = []
    for city, lat, lng in locations:
        cell = latlng_to_cell(lat, lng, 9)
        geojson = cells_to_geojson([cell])
        
        # Add interactive properties
        feature = geojson['features'][0]
        feature['properties'].update({
            'city': city,
            'population': {
                'San Francisco': 873965,
                'New York': 8336817,
                'Los Angeles': 3979576,
                'Chicago': 2693976,
                'Miami': 454279
            }.get(city, 0),
            'timezone': {
                'San Francisco': 'PST',
                'New York': 'EST',
                'Los Angeles': 'PST',
                'Chicago': 'CST',
                'Miami': 'EST'
            }.get(city, ''),
            'clickable': True,
            'zoom_level': 12
        })
        
        interactive_features.append(feature)
    
    interactive_geojson = {
        'type': 'FeatureCollection',
        'features': interactive_features
    }
    
    print(f"  1. Interactive GeoJSON: {len(interactive_features)} features")
    
    # 2. Generate interactive data table
    print("  2. Interactive Data Table:")
    print(f"     City | Cell Index | Population | Timezone")
    print(f"     {'-' * 50}")
    for feature in interactive_features:
        props = feature['properties']
        print(f"     {props['city']:15s} | {feature['properties']['h3_index']} | {props['population']:10d} | {props['timezone']}")
    
    # 3. Generate zoom levels data
    print("  3. Zoom Levels Data:")
    zoom_data = {}
    for city, lat, lng in locations:
        zoom_data[city] = {}
        for resolution in [6, 8, 10, 12]:
            cell = latlng_to_cell(lat, lng, resolution)
            area = cell_area(cell, 'km^2')
            zoom_data[city][resolution] = {
                'cell': cell,
                'area': area,
                'zoom_level': 15 - resolution
            }
            print(f"    {city} Res {resolution}: {cell}, {area:.6f} km², Zoom {15-resolution}")
    
    # 4. Generate click handlers data
    print("  4. Click Handlers Data:")
    click_handlers = {}
    for feature in interactive_features:
        city = feature['properties']['city']
        cell = feature['properties']['h3_index']
        
        # Generate disk cells for click expansion
        disk_cells = grid_disk(cell, 2)
        disk_geojson = cells_to_geojson(disk_cells)
        
        click_handlers[city] = {
            'cell': cell,
            'disk_cells': disk_cells,
            'disk_geojson': disk_geojson,
            'cell_count': len(disk_cells),
            'total_area': sum(cell_area(c, 'km^2') for c in disk_cells)
        }
        
        print(f"    {city}: {len(disk_cells)} disk cells, {click_handlers[city]['total_area']:.6f} km²")


def demo_heatmap_visualization():
    """Demonstrate heatmap visualization outputs."""
    print("\n🔹 Heatmap Visualization")
    print("-" * 40)
    
    # Create heatmap data
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    heatmap_cells = grid_disk(center_cell, 4)
    
    print(f"Creating heatmap for {len(heatmap_cells)} cells:")
    
    # 1. Generate heatmap data with intensity values
    heatmap_data = []
    for i, cell in enumerate(heatmap_cells):
        # Simulate intensity based on distance from center
        distance = grid_distance(center_cell, cell)
        intensity = max(0, 1 - distance / 4)  # Intensity decreases with distance
        
        heatmap_data.append({
            'cell': cell,
            'coordinates': cell_to_latlng(cell),
            'intensity': intensity,
            'distance': distance,
            'area': cell_area(cell, 'km^2')
        })
    
    print(f"  1. Heatmap Data: {len(heatmap_data)} data points")
    print(f"     Intensity range: {min(d['intensity'] for d in heatmap_data):.3f} - {max(d['intensity'] for d in heatmap_data):.3f}")
    
    # 2. Generate intensity categories
    intensity_categories = {
        'high': [d for d in heatmap_data if d['intensity'] > 0.7],
        'medium': [d for d in heatmap_data if 0.3 <= d['intensity'] <= 0.7],
        'low': [d for d in heatmap_data if d['intensity'] < 0.3]
    }
    
    print(f"  2. Intensity Categories:")
    for category, data in intensity_categories.items():
        print(f"    {category.capitalize()}: {len(data)} cells")
    
    # 3. Generate color-coded GeoJSON
    color_coded_features = []
    for data in heatmap_data:
        geojson = cells_to_geojson([data['cell']])
        feature = geojson['features'][0]
        
        # Add heatmap properties
        feature['properties'].update({
            'intensity': data['intensity'],
            'distance': data['distance'],
            'color': f"rgb({int(255 * (1 - data['intensity']))}, {int(255 * data['intensity'])}, 0)",
            'opacity': data['intensity']
        })
        
        color_coded_features.append(feature)
    
    color_coded_geojson = {
        'type': 'FeatureCollection',
        'features': color_coded_features
    }
    
    print(f"  3. Color-coded GeoJSON: {len(color_coded_features)} features")


def demo_temporal_visualization():
    """Demonstrate temporal visualization outputs."""
    print("\n🔹 Temporal Visualization")
    print("-" * 40)
    
    # Create temporal data
    base_cell = latlng_to_cell(37.7749, -122.4194, 9)
    
    print("Creating temporal visualization data:")
    
    # 1. Generate time series data
    time_series = []
    for hour in range(0, 24, 2):  # Every 2 hours
        # Simulate temporal changes (e.g., traffic, activity)
        activity_level = 0.5 + 0.3 * abs(12 - hour) / 12  # Peak at noon/midnight
        
        frame_data = {
            'time': hour,
            'activity_level': activity_level,
            'cells': grid_disk(base_cell, int(activity_level * 3)),
            'cell_count': len(grid_disk(base_cell, int(activity_level * 3))),
            'total_area': sum(cell_area(c, 'km^2') for c in grid_disk(base_cell, int(activity_level * 3)))
        }
        time_series.append(frame_data)
        print(f"  Hour {hour:02d}: Activity {activity_level:.2f}, {frame_data['cell_count']} cells")
    
    # 2. Generate temporal heatmap
    temporal_heatmap = []
    for hour in range(24):
        activity_level = 0.5 + 0.3 * abs(12 - hour) / 12
        temporal_heatmap.append({
            'hour': hour,
            'activity': activity_level,
            'color': f"rgb({int(255 * (1 - activity_level))}, {int(255 * activity_level)}, 0)"
        })
    
    print(f"  2. Temporal Heatmap: {len(temporal_heatmap)} time points")
    
    # 3. Generate animation frames
    animation_frames = []
    for i, frame in enumerate(time_series):
        frame_geojson = cells_to_geojson(frame['cells'])
        
        # Add temporal properties
        for feature in frame_geojson['features']:
            feature['properties'].update({
                'time': frame['time'],
                'activity_level': frame['activity_level'],
                'frame': i
            })
        
        animation_frames.append({
            'frame': i,
            'time': frame['time'],
            'geojson': frame_geojson,
            'activity_level': frame['activity_level']
        })
    
    print(f"  3. Animation Frames: {len(animation_frames)} frames")


def demo_export_formats():
    """Demonstrate export formats for visualizations."""
    print("\n🔹 Export Formats")
    print("-" * 40)
    
    # Create sample dataset
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    cells = grid_disk(center_cell, 2)
    
    print("Exporting visualization data in multiple formats:")
    
    # 1. GeoJSON for web mapping
    geojson_output = cells_to_geojson(cells)
    print(f"  1. GeoJSON: {len(geojson_output)} characters")
    
    # 2. CSV for data analysis
    csv_output = cells_to_csv(cells)
    print(f"  2. CSV: {len(csv_output)} characters")
    
    # 3. JSON for JavaScript applications
    json_data = {
        'cells': cells,
        'metadata': {
            'center_cell': center_cell,
            'cell_count': len(cells),
            'total_area': sum(cell_area(c, 'km^2') for c in cells),
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    json_output = json.dumps(json_data, indent=2)
    print(f"  3. JSON: {len(json_output)} characters")
    
    # 4. Summary statistics
    distribution = analyze_cell_distribution(cells)
    stats = calculate_spatial_statistics(cells)
    
    summary_data = {
        'distribution': distribution,
        'statistics': stats,
        'visualization_info': {
            'type': 'grid_disk',
            'radius': 2,
            'center_coordinates': cell_to_latlng(center_cell)
        }
    }
    
    print(f"  4. Summary: {len(json.dumps(summary_data))} characters")


def main():
    """Run all visualization demonstrations."""
    print("🌍 Visualization Outputs Example")
    print("=" * 50)
    print("Demonstrating static, animated, and interactive visualizations")
    print("using tested H3 methods")
    print("=" * 50)
    
    demo_static_visualization()
    demo_animated_visualization()
    demo_interactive_visualization()
    demo_heatmap_visualization()
    demo_temporal_visualization()
    demo_export_formats()
    
    print("\n✅ Visualization outputs demonstration completed!")


if __name__ == "__main__":
    main() 