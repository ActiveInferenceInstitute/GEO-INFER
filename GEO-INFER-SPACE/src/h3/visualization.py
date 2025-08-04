#!/usr/bin/env python3
"""
H3 Visualization Module

Provides static visualization capabilities for H3 geospatial data.
Generates maps, charts, and plots using matplotlib and other libraries.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid Qt issues

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import contextlib

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    get_resolution, is_valid_cell
)

from conversion import (
    cells_to_geojson, cells_to_csv
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics
)

from constants import (
    MAX_H3_RES, MIN_H3_RES, H3_AREA_KM2
)


def create_cell_map(cells: List[str], 
                   title: str = "H3 Cell Map",
                   output_path: Optional[Path] = None,
                   figsize: Tuple[int, int] = (12, 8),
                   dpi: int = 300) -> Dict[str, Any]:
    """
    Create a static map visualization of H3 cells.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the map
        output_path: Path to save the image (optional)
        figsize: Figure size (width, height)
        dpi: DPI for the output image
        
    Returns:
        Dictionary with visualization metadata
    """
    # Set up the plot
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=figsize)
    
    # Colors for different resolutions
    colors = plt.cm.Set3(np.linspace(0, 1, MAX_H3_RES + 1))
    
    # Plot each cell
    cell_data = []
    center_lat, center_lng = 0.0, 0.0  # Initialize with default values
    
    for cell in cells:
        if not is_valid_cell(cell):
            continue
            
        # Get cell boundary
        boundary = cell_to_boundary(cell)
        resolution = get_resolution(cell)
        area = cell_area(cell, 'km^2')
        
        # Convert boundary to plotting coordinates
        lats = [coord[0] for coord in boundary]
        lngs = [coord[1] for coord in boundary]
        
        # Create polygon patch
        polygon = patches.Polygon(list(zip(lngs, lats)), 
                                facecolor=colors[resolution], 
                                edgecolor='black', 
                                linewidth=0.5,
                                alpha=0.7)
        ax.add_patch(polygon)
        
        # Add cell center label for small datasets
        if len(cells) <= 20:
            cell_center_lat, cell_center_lng = cell_to_latlng(cell)
            ax.text(cell_center_lng, cell_center_lat, f'R{resolution}', 
                   fontsize=8, ha='center', va='center')
        
        # Store cell data
        cell_center_lat, cell_center_lng = cell_to_latlng(cell)
        cell_data.append({
            'cell': cell,
            'resolution': resolution,
            'area_km2': area,
            'center': (cell_center_lat, cell_center_lng),
            'boundary': boundary
        })
        
        # Update center coordinates for the first valid cell
        if len(cell_data) == 1:
            center_lat, center_lng = cell_center_lat, cell_center_lng
    
    # Set plot limits and labels
    if cell_data:
        all_lats = [coord[0] for cell in cell_data for coord in cell['boundary']]
        all_lngs = [coord[1] for cell in cell_data for coord in cell['boundary']]
        
        ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
        ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
    
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Add legend for resolutions
    legend_elements = []
    resolutions = list(set(cell['resolution'] for cell in cell_data))
    for res in sorted(resolutions):
        legend_elements.append(patches.Patch(color=colors[res], 
                                           label=f'Resolution {res}'))
    
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right')
    
    # Save the plot
    if output_path:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
        print(f"✅ Saved cell map to {output_path}")
    
    # Get plot data
    plot_data = {
        'title': title,
        'cell_count': len(cells),
        'resolutions': list(set(cell['resolution'] for cell in cell_data)),
        'total_area_km2': sum(cell['area_km2'] for cell in cell_data),
        'cell_data': cell_data
    }
    
    plt.close()
    return plot_data


def create_resolution_chart(cells: List[str],
                          title: str = "H3 Resolution Distribution",
                          output_path: Optional[Path] = None,
                          figsize: Tuple[int, int] = (10, 6)) -> Dict[str, Any]:
    """
    Create a chart showing the distribution of H3 resolutions.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the chart
        output_path: Path to save the image (optional)
        figsize: Figure size (width, height)
        
    Returns:
        Dictionary with chart metadata
    """
    # Count cells by resolution
    resolution_counts = {}
    resolution_areas = {}
    
    for cell in cells:
        if not is_valid_cell(cell):
            continue
            
        resolution = get_resolution(cell)
        area = cell_area(cell, 'km^2')
        
        resolution_counts[resolution] = resolution_counts.get(resolution, 0) + 1
        resolution_areas[resolution] = resolution_areas.get(resolution, 0) + area
    
    # Create the chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Cell count chart
    resolutions = sorted(resolution_counts.keys())
    counts = [resolution_counts[res] for res in resolutions]
    
    bars1 = ax1.bar(resolutions, counts, color='skyblue', edgecolor='navy')
    ax1.set_xlabel('Resolution')
    ax1.set_ylabel('Number of Cells')
    ax1.set_title('Cell Count by Resolution')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, count in zip(bars1, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom')
    
    # Area chart
    areas = [resolution_areas[res] for res in resolutions]
    
    bars2 = ax2.bar(resolutions, areas, color='lightcoral', edgecolor='darkred')
    ax2.set_xlabel('Resolution')
    ax2.set_ylabel('Total Area (km²)')
    ax2.set_title('Total Area by Resolution')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, area in zip(bars2, areas):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{area:.2f}', ha='center', va='bottom')
    
    plt.suptitle(title)
    plt.tight_layout()
    
    # Save the chart
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved resolution chart to {output_path}")
    
    # Get chart data
    chart_data = {
        'title': title,
        'resolution_counts': resolution_counts,
        'resolution_areas': resolution_areas,
        'total_cells': sum(resolution_counts.values()),
        'total_area_km2': sum(resolution_areas.values())
    }
    
    plt.close()
    return chart_data


def create_area_distribution_plot(cells: List[str],
                                title: str = "H3 Cell Area Distribution",
                                output_path: Optional[Path] = None,
                                figsize: Tuple[int, int] = (10, 6)) -> Dict[str, Any]:
    """
    Create a plot showing the distribution of H3 cell areas.
    
    Args:
        cells: List of H3 cell indices
        title: Title for the plot
        output_path: Path to save the image (optional)
        figsize: Figure size (width, height)
        
    Returns:
        Dictionary with plot metadata
    """
    # Calculate areas for each cell
    areas = []
    resolutions = []
    
    for cell in cells:
        if not is_valid_cell(cell):
            continue
            
        area = cell_area(cell, 'km^2')
        resolution = get_resolution(cell)
        
        areas.append(area)
        resolutions.append(resolution)
    
    if not areas:
        return {'error': 'No valid cells provided'}
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Histogram
    ax1.hist(areas, bins=20, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
    ax1.set_xlabel('Area (km²)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Area Distribution Histogram')
    ax1.grid(True, alpha=0.3)
    
    # Box plot by resolution
    resolution_areas = {}
    for res, area in zip(resolutions, areas):
        if res not in resolution_areas:
            resolution_areas[res] = []
        resolution_areas[res].append(area)
    
    if resolution_areas:
        box_data = [resolution_areas[res] for res in sorted(resolution_areas.keys())]
        box_labels = [f'R{res}' for res in sorted(resolution_areas.keys())]
        
        bp = ax2.boxplot(box_data, labels=box_labels, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        
        ax2.set_ylabel('Area (km²)')
        ax2.set_title('Area Distribution by Resolution')
        ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title)
    plt.tight_layout()
    
    # Save the plot
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved area distribution plot to {output_path}")
    
    # Get plot data
    plot_data = {
        'title': title,
        'total_cells': len(areas),
        'min_area': min(areas),
        'max_area': max(areas),
        'mean_area': np.mean(areas),
        'median_area': np.median(areas),
        'std_area': np.std(areas),
        'resolution_areas': resolution_areas
    }
    
    plt.close()
    return plot_data


def create_density_heatmap(cells: List[str],
                          center_cell: str,
                          radius: int = 3,
                          title: str = "H3 Cell Density Heatmap",
                          output_path: Optional[Path] = None,
                          figsize: Tuple[int, int] = (12, 8)) -> Dict[str, Any]:
    """
    Create a heatmap showing cell density around a center cell.
    
    Args:
        cells: List of H3 cell indices
        center_cell: Center cell for the heatmap
        radius: Radius for the heatmap
        title: Title for the heatmap
        output_path: Path to save the image (optional)
        figsize: Figure size (width, height)
        
    Returns:
        Dictionary with heatmap metadata
    """
    from traversal import grid_disk
    
    # Create a grid around the center cell
    grid_cells = grid_disk(center_cell, radius)
    
    # Calculate density for each cell in the grid
    density_data = {}
    for cell in grid_cells:
        # Count how many of our cells are in this grid cell
        # For simplicity, we'll use a distance-based density
        center_lat, center_lng = cell_to_latlng(cell)
        density = 0
        
        for target_cell in cells:
            if not is_valid_cell(target_cell):
                continue
                
            target_lat, target_lng = cell_to_latlng(target_cell)
            # Simple distance calculation
            distance = ((center_lat - target_lat)**2 + (center_lng - target_lng)**2)**0.5
            if distance < 0.1:  # Within ~10km
                density += 1
        
        density_data[cell] = density
    
    # Create the heatmap
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each cell with color based on density
    max_density = max(density_data.values()) if density_data else 1
    colors = plt.cm.Reds(np.linspace(0, 1, max_density + 1))
    
    for cell, density in density_data.items():
        boundary = cell_to_boundary(cell)
        lats = [coord[0] for coord in boundary]
        lngs = [coord[1] for coord in boundary]
        
        color_idx = min(density, len(colors) - 1)
        polygon = patches.Polygon(list(zip(lngs, lats)), 
                                facecolor=colors[color_idx], 
                                edgecolor='black', 
                                linewidth=0.5,
                                alpha=0.8)
        ax.add_patch(polygon)
        
        # Add density label
        center_lat, center_lng = cell_to_latlng(cell)
        ax.text(center_lng, center_lat, str(density), 
               fontsize=8, ha='center', va='center', 
               color='white' if density > max_density/2 else 'black')
    
    # Set plot limits
    if density_data:
        all_lats = []
        all_lngs = []
        for cell in density_data.keys():
            boundary = cell_to_boundary(cell)
            all_lats.extend([coord[0] for coord in boundary])
            all_lngs.extend([coord[1] for coord in boundary])
        
        ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
        ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
    
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(0, max_density))
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Cell Density')
    
    # Save the heatmap
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved density heatmap to {output_path}")
    
    # Get heatmap data
    heatmap_data = {
        'title': title,
        'center_cell': center_cell,
        'radius': radius,
        'max_density': max_density,
        'total_grid_cells': len(density_data),
        'density_data': density_data
    }
    
    plt.close()
    return heatmap_data


def create_comparison_plot(cells_list: List[List[str]],
                          labels: List[str],
                          title: str = "H3 Cell Comparison",
                          output_path: Optional[Path] = None,
                          figsize: Tuple[int, int] = (15, 10)) -> Dict[str, Any]:
    """
    Create a comparison plot of multiple H3 cell datasets.
    
    Args:
        cells_list: List of cell lists to compare
        labels: Labels for each dataset
        title: Title for the comparison
        output_path: Path to save the image (optional)
        figsize: Figure size (width, height)
        
    Returns:
        Dictionary with comparison metadata
    """
    if len(cells_list) != len(labels):
        raise ValueError("Number of cell lists must match number of labels")
    
    # Calculate statistics for each dataset
    datasets_stats = []
    
    for cells in cells_list:
        if not cells:
            datasets_stats.append({
                'cell_count': 0,
                'resolutions': [],
                'total_area': 0,
                'avg_area': 0
            })
            continue
        
        # Calculate statistics
        resolutions = [get_resolution(cell) for cell in cells if is_valid_cell(cell)]
        areas = [cell_area(cell, 'km^2') for cell in cells if is_valid_cell(cell)]
        
        stats = {
            'cell_count': len([c for c in cells if is_valid_cell(c)]),
            'resolutions': list(set(resolutions)),
            'total_area': sum(areas),
            'avg_area': np.mean(areas) if areas else 0
        }
        datasets_stats.append(stats)
    
    # Create comparison plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
    
    # Cell count comparison
    counts = [stats['cell_count'] for stats in datasets_stats]
    bars1 = ax1.bar(labels, counts, color='lightblue', edgecolor='navy')
    ax1.set_ylabel('Number of Cells')
    ax1.set_title('Cell Count Comparison')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, count in zip(bars1, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}', ha='center', va='bottom')
    
    # Total area comparison
    areas = [stats['total_area'] for stats in datasets_stats]
    bars2 = ax2.bar(labels, areas, color='lightcoral', edgecolor='darkred')
    ax2.set_ylabel('Total Area (km²)')
    ax2.set_title('Total Area Comparison')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, area in zip(bars2, areas):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{area:.2f}', ha='center', va='bottom')
    
    # Average area comparison
    avg_areas = [stats['avg_area'] for stats in datasets_stats]
    bars3 = ax3.bar(labels, avg_areas, color='lightgreen', edgecolor='darkgreen')
    ax3.set_ylabel('Average Area (km²)')
    ax3.set_title('Average Area Comparison')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, avg_area in zip(bars3, avg_areas):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{avg_area:.4f}', ha='center', va='bottom')
    
    # Resolution distribution
    all_resolutions = set()
    for stats in datasets_stats:
        all_resolutions.update(stats['resolutions'])
    
    resolution_data = []
    for stats in datasets_stats:
        res_counts = {}
        for res in all_resolutions:
            res_counts[res] = stats['resolutions'].count(res)
        resolution_data.append(res_counts)
    
    if resolution_data:
        x = np.arange(len(labels))
        width = 0.8 / len(all_resolutions)
        
        for i, res in enumerate(sorted(all_resolutions)):
            counts = [data.get(res, 0) for data in resolution_data]
            ax4.bar(x + i * width, counts, width, label=f'R{res}')
        
        ax4.set_xlabel('Datasets')
        ax4.set_ylabel('Number of Cells')
        ax4.set_title('Resolution Distribution')
        ax4.set_xticks(x + width * (len(all_resolutions) - 1) / 2)
        ax4.set_xticklabels(labels)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    plt.suptitle(title)
    plt.tight_layout()
    
    # Save the comparison
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Saved comparison plot to {output_path}")
    
    # Get comparison data
    comparison_data = {
        'title': title,
        'labels': labels,
        'datasets_stats': datasets_stats,
        'total_datasets': len(cells_list)
    }
    
    plt.close()
    return comparison_data


def generate_visualization_report(cells: List[str],
                                output_dir: Path,
                                title: str = "H3 Visualization Report") -> Dict[str, Any]:
    """
    Generate a comprehensive visualization report for H3 cells.
    
    Args:
        cells: List of H3 cell indices
        output_dir: Directory to save visualizations
        title: Title for the report
        
    Returns:
        Dictionary with report metadata
    """
    output_dir.mkdir(exist_ok=True)
    
    report_data = {
        'title': title,
        'total_cells': len(cells),
        'visualizations': {}
    }
    
    # Generate cell map
    map_path = output_dir / "cell_map.png"
    map_data = create_cell_map(cells, title="H3 Cell Map", output_path=map_path)
    report_data['visualizations']['cell_map'] = map_data
    
    # Generate resolution chart
    chart_path = output_dir / "resolution_chart.png"
    chart_data = create_resolution_chart(cells, output_path=chart_path)
    report_data['visualizations']['resolution_chart'] = chart_data
    
    # Generate area distribution plot
    plot_path = output_dir / "area_distribution.png"
    plot_data = create_area_distribution_plot(cells, output_path=plot_path)
    report_data['visualizations']['area_distribution'] = plot_data
    
    # Generate density heatmap if we have a center cell
    if cells:
        center_cell = cells[0]
        heatmap_path = output_dir / "density_heatmap.png"
        heatmap_data = create_density_heatmap(cells, center_cell, output_path=heatmap_path)
        report_data['visualizations']['density_heatmap'] = heatmap_data
    
    # Save report metadata
    report_path = output_dir / "visualization_report.json"
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"✅ Generated visualization report with {len(report_data['visualizations'])} visualizations")
    return report_data
