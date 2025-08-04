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
import csv
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area
)

from traversal import (
    grid_disk, grid_ring, grid_path_cells, grid_distance
)

from conversion import (
    cells_to_geojson, cells_to_csv
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics
)

from visualization import (
    create_cell_map, create_resolution_chart, create_area_distribution_plot,
    create_density_heatmap, create_comparison_plot, generate_visualization_report
)

from animation import (
    create_grid_expansion_animation, create_resolution_transition_animation,
    create_path_animation, create_temporal_animation, create_animated_heatmap,
    generate_animation_report
)

from interactive import (
    create_interactive_map, create_simple_html_map, create_interactive_dashboard,
    create_zoomable_map, create_interactive_report
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def demo_static_visualization():
    """Demonstrate static visualization outputs."""
    print("🔹 Static Visualization")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create test dataset
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    cells = grid_disk(center_cell, 3)
    
    print(f"Creating static visualization for {len(cells)} cells:")
    
    # 1. Generate cell map
    map_path = output_dir / "05_static_visualization_map.png"
    create_cell_map(cells, title="Static H3 Cell Map", output_path=map_path)
    print(f"  1. Cell Map: {map_path}")
    
    # 2. Generate resolution chart
    chart_path = output_dir / "05_static_resolution_chart.png"
    create_resolution_chart(cells, title="Resolution Distribution", output_path=chart_path)
    print(f"  2. Resolution Chart: {chart_path}")
    
    # 3. Generate area distribution plot
    plot_path = output_dir / "05_static_area_distribution.png"
    create_area_distribution_plot(cells, title="Area Distribution", output_path=plot_path)
    print(f"  3. Area Distribution Plot: {plot_path}")
    
    # 4. Generate density heatmap
    heatmap_path = output_dir / "05_static_density_heatmap.png"
    create_density_heatmap(cells, center_cell, radius=3, 
                          title="Density Heatmap", output_path=heatmap_path)
    print(f"  4. Density Heatmap: {heatmap_path}")
    
    # 5. Generate summary statistics
    distribution = analyze_cell_distribution(cells)
    stats = calculate_spatial_statistics(cells)
    
    print(f"  5. Summary Statistics:")
    print(f"     Total cells: {distribution['total_cells']}")
    print(f"     Total area: {distribution['total_area_km2']:.6f} km²")
    print(f"     Average area: {distribution['avg_area_km2']:.6f} km²")
    print(f"     Centroid: {stats['centroid']}")
    print(f"     Compactness: {stats['compactness']:.4f}")
    
    # Save static visualization data
    static_data = {
        "center_cell": center_cell,
        "cells": cells,
        "distribution": distribution,
        "statistics": stats,
        "visualization_files": [
            str(map_path),
            str(chart_path),
            str(plot_path),
            str(heatmap_path)
        ]
    }
    
    output_file = output_dir / "05_static_visualization.json"
    with open(output_file, 'w') as f:
        json.dump(static_data, f, indent=2)
    print(f"✅ Saved static visualization data to {output_file}")


def demo_animated_visualization():
    """Demonstrate animated visualization outputs."""
    print("\n🔹 Animated Visualization")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create animation frames
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    
    print("Creating animation frames:")
    
    # 1. Grid expansion animation
    expansion_path = output_dir / "05_grid_expansion_animation.gif"
    create_grid_expansion_animation([center_cell], center_cell, max_radius=4,
                                  title="Grid Expansion Animation", output_path=expansion_path)
    print(f"  1. Grid Expansion Animation: {expansion_path}")
    
    # 2. Resolution transition animation
    transition_path = output_dir / "05_resolution_transition_animation.gif"
    create_resolution_transition_animation([center_cell], start_resolution=6, end_resolution=12,
                                        title="Resolution Transition Animation", output_path=transition_path)
    print(f"  2. Resolution Transition Animation: {transition_path}")
    
    # 3. Path animation
    end_cell = latlng_to_cell(37.7849, -122.4094, 9)  # Closer to San Francisco
    path_path = output_dir / "05_path_animation.gif"
    create_path_animation(center_cell, end_cell, title="Path Animation", output_path=path_path)
    print(f"  3. Path Animation: {path_path}")
    
    # 4. Animated heatmap
    heatmap_path = output_dir / "05_animated_heatmap.gif"
    create_animated_heatmap([center_cell], center_cell, radius=3,
                           title="Animated Heatmap", output_path=heatmap_path)
    print(f"  4. Animated Heatmap: {heatmap_path}")
    
    # Generate animation report
    animation_report_path = output_dir / "05_animation_report.json"
    generate_animation_report([center_cell], output_dir / "animations", title="Animation Report")
    print(f"  5. Animation Report: {animation_report_path}")
    
    # Save animation data
    animation_data = {
        "center_cell": center_cell,
        "end_cell": end_cell,
        "animation_files": [
            str(expansion_path),
            str(transition_path),
            str(path_path),
            str(heatmap_path)
        ]
    }
    
    output_file = output_dir / "05_animated_visualization.json"
    with open(output_file, 'w') as f:
        json.dump(animation_data, f, indent=2)
    print(f"✅ Saved animated visualization data to {output_file}")


def demo_interactive_visualization():
    """Demonstrate interactive visualization outputs."""
    print("\n🔹 Interactive Visualization")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create interactive dataset
    locations = [
        ("San Francisco", 37.7749, -122.4194),
        ("New York", 40.7128, -74.0060),
        ("Los Angeles", 34.0522, -118.2437),
        ("Chicago", 41.8781, -87.6298),
        ("Miami", 25.7617, -80.1918)
    ]
    
    print("Creating interactive visualization data:")
    
    # Convert locations to cells
    cells = []
    for city, lat, lng in locations:
        cell = latlng_to_cell(lat, lng, 9)
        cells.append(cell)
    
    # 1. Generate interactive map
    map_path = output_dir / "05_interactive_map.html"
    create_interactive_map(cells, title="Interactive H3 Map", output_path=map_path)
    print(f"  1. Interactive Map: {map_path}")
    
    # 2. Generate interactive dashboard
    dashboard_path = output_dir / "05_interactive_dashboard.html"
    create_interactive_dashboard(cells, title="Interactive H3 Dashboard", output_path=dashboard_path)
    print(f"  2. Interactive Dashboard: {dashboard_path}")
    
    # 3. Generate zoomable map
    zoomable_path = output_dir / "05_zoomable_map.html"
    create_zoomable_map(cells, title="Zoomable H3 Map", output_path=zoomable_path)
    print(f"  3. Zoomable Map: {zoomable_path}")
    
    # 4. Generate simple HTML map
    simple_path = output_dir / "05_simple_html_map.html"
    create_simple_html_map(cells, title="Simple HTML Map", output_path=simple_path)
    print(f"  4. Simple HTML Map: {simple_path}")
    
    # Generate interactive report
    interactive_report_path = output_dir / "05_interactive_report.json"
    create_interactive_report(cells, output_dir / "interactive", title="Interactive Report")
    print(f"  5. Interactive Report: {interactive_report_path}")
    
    # Save interactive visualization data
    interactive_data = {
        "locations": locations,
        "cells": cells,
        "interactive_files": [
            str(map_path),
            str(dashboard_path),
            str(zoomable_path),
            str(simple_path)
        ]
    }
    
    output_file = output_dir / "05_interactive_visualization.json"
    with open(output_file, 'w') as f:
        json.dump(interactive_data, f, indent=2)
    print(f"✅ Saved interactive visualization data to {output_file}")


def demo_heatmap_visualization():
    """Demonstrate heatmap visualization outputs."""
    print("\n🔹 Heatmap Visualization")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create heatmap data
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    heatmap_cells = grid_disk(center_cell, 4)
    
    print(f"Creating heatmap for {len(heatmap_cells)} cells:")
    
    # Generate density heatmap
    heatmap_path = output_dir / "05_heatmap_visualization.png"
    create_density_heatmap(heatmap_cells, center_cell, radius=4,
                          title="H3 Cell Density Heatmap", output_path=heatmap_path)
    print(f"  1. Density Heatmap: {heatmap_path}")
    
    # Generate animated heatmap
    animated_heatmap_path = output_dir / "05_animated_heatmap_visualization.gif"
    create_animated_heatmap(heatmap_cells, center_cell, radius=4,
                           title="Animated Heatmap Visualization", output_path=animated_heatmap_path)
    print(f"  2. Animated Heatmap: {animated_heatmap_path}")
    
    # Save heatmap visualization data
    heatmap_data = {
        "center_cell": center_cell,
        "heatmap_cells": heatmap_cells,
        "cell_count": len(heatmap_cells),
        "heatmap_files": [
            str(heatmap_path),
            str(animated_heatmap_path)
        ]
    }
    
    output_file = output_dir / "05_heatmap_visualization.json"
    with open(output_file, 'w') as f:
        json.dump(heatmap_data, f, indent=2)
    print(f"✅ Saved heatmap visualization data to {output_file}")


def demo_temporal_visualization():
    """Demonstrate temporal visualization outputs."""
    print("\n🔹 Temporal Visualization")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create temporal data
    base_cell = latlng_to_cell(37.7749, -122.4194, 9)
    
    print("Creating temporal visualization data:")
    
    # Generate time series data
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
    
    # Create temporal animation
    temporal_path = output_dir / "05_temporal_visualization.gif"
    create_temporal_animation([base_cell], time_series, title="Temporal Visualization", output_path=temporal_path)
    print(f"  1. Temporal Animation: {temporal_path}")
    
    # Save temporal visualization data
    temporal_data = {
        "base_cell": base_cell,
        "time_series": time_series,
        "temporal_files": [str(temporal_path)]
    }
    
    output_file = output_dir / "05_temporal_visualization.json"
    with open(output_file, 'w') as f:
        json.dump(temporal_data, f, indent=2)
    print(f"✅ Saved temporal visualization data to {output_file}")


def demo_export_formats():
    """Demonstrate export formats for visualizations."""
    print("\n🔹 Export Formats")
    print("-" * 40)
    
    output_dir = ensure_output_dir()
    
    # Create sample dataset
    center_cell = latlng_to_cell(37.7749, -122.4194, 9)
    cells = grid_disk(center_cell, 2)
    
    print("Exporting visualization data in multiple formats:")
    
    # 1. Generate comprehensive visualization report
    viz_report_path = output_dir / "05_visualization_report.json"
    generate_visualization_report(cells, output_dir / "visualizations", title="Visualization Report")
    print(f"  1. Visualization Report: {viz_report_path}")
    
    # 2. Generate comprehensive animation report
    anim_report_path = output_dir / "05_animation_report.json"
    generate_animation_report(cells, output_dir / "animations", title="Animation Report")
    print(f"  2. Animation Report: {anim_report_path}")
    
    # 3. Generate comprehensive interactive report
    int_report_path = output_dir / "05_interactive_report.json"
    create_interactive_report(cells, output_dir / "interactive", title="Interactive Report")
    print(f"  3. Interactive Report: {int_report_path}")
    
    # 4. Generate comparison plots
    comparison_path = output_dir / "05_export_comparison.png"
    create_comparison_plot([cells], ["Sample Dataset"], title="Export Comparison", output_path=comparison_path)
    print(f"  4. Comparison Plot: {comparison_path}")
    
    # Save export format data
    export_data = {
        "center_cell": center_cell,
        "cells": cells,
        "cell_count": len(cells),
        "export_files": [
            str(viz_report_path),
            str(anim_report_path),
            str(int_report_path),
            str(comparison_path)
        ]
    }
    
    output_file = output_dir / "05_export_formats.json"
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2)
    print(f"✅ Saved export format data to {output_file}")


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
    print("📁 All outputs saved to the 'output' directory")
    print("📊 Generated visualizations, animations, and interactive outputs:")
    print("   Static Visualizations:")
    print("   - 05_static_visualization_map.png")
    print("   - 05_static_resolution_chart.png")
    print("   - 05_static_area_distribution.png")
    print("   - 05_static_density_heatmap.png")
    print("   Animations:")
    print("   - 05_grid_expansion_animation.gif")
    print("   - 05_resolution_transition_animation.gif")
    print("   - 05_path_animation.gif")
    print("   - 05_animated_heatmap.gif")
    print("   - 05_temporal_visualization.gif")
    print("   Interactive Outputs:")
    print("   - 05_interactive_map.html")
    print("   - 05_interactive_dashboard.html")
    print("   - 05_zoomable_map.html")
    print("   - 05_simple_html_map.html")
    print("   Heatmaps:")
    print("   - 05_heatmap_visualization.png")
    print("   - 05_animated_heatmap_visualization.gif")
    print("   Reports:")
    print("   - 05_visualization_report.json")
    print("   - 05_animation_report.json")
    print("   - 05_interactive_report.json")
    print("   - 05_export_comparison.png")


if __name__ == "__main__":
    main() 