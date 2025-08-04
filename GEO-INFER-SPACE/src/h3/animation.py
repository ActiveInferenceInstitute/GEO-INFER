#!/usr/bin/env python3
"""
H3 Animation Module

Provides animated visualization capabilities for H3 geospatial data.
Generates GIFs, videos, and animated plots using matplotlib and imageio.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend to avoid Qt issues

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np
import json
import imageio
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional, Callable
import time

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    get_resolution, is_valid_cell
)

from traversal import (
    grid_disk, grid_ring, grid_path_cells
)

from constants import (
    MAX_H3_RES, MIN_H3_RES
)


def _fig_to_image(fig):
    """Convert matplotlib figure to numpy array image."""
    fig.canvas.draw()
    try:
        # Try the standard method first
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    except AttributeError:
        # For Agg backend, use buffer_rgba() and convert to RGB
        buf = fig.canvas.buffer_rgba()
        image = np.frombuffer(buf, dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        image = image[:, :, :3]  # Remove alpha channel
    return image


def create_grid_expansion_animation(cells: List[str],
                                  center_cell: str,
                                  max_radius: int = 5,
                                  title: str = "H3 Grid Expansion Animation",
                                  output_path: Optional[Path] = None,
                                  duration: float = 2.0,
                                  fps: int = 10) -> Dict[str, Any]:
    """
    Create an animation showing grid expansion from a center cell.
    
    Args:
        cells: List of H3 cell indices
        center_cell: Center cell for the animation
        max_radius: Maximum radius for the expansion
        title: Title for the animation
        output_path: Path to save the GIF (optional)
        duration: Duration of the animation in seconds
        fps: Frames per second
        
    Returns:
        Dictionary with animation metadata
    """
    frames = []
    frame_data = []
    
    # Calculate frames per radius
    total_frames = int(duration * fps)
    frames_per_radius = max(1, total_frames // max_radius)
    
    print(f"Creating grid expansion animation with {total_frames} frames...")
    
    for radius in range(max_radius + 1):
        # Get cells for this radius
        current_cells = grid_disk(center_cell, radius)
        
        # Create frame for this radius
        for frame_idx in range(frames_per_radius):
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Colors for different resolutions
            colors = plt.cm.Set3(np.linspace(0, 1, MAX_H3_RES + 1))
            
            # Plot each cell
            for cell in current_cells:
                if not is_valid_cell(cell):
                    continue
                    
                boundary = cell_to_boundary(cell)
                resolution = get_resolution(cell)
                
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
            
            # Set plot limits
            if current_cells:
                all_lats = []
                all_lngs = []
                for cell in current_cells:
                    if is_valid_cell(cell):
                        boundary = cell_to_boundary(cell)
                        all_lats.extend([coord[0] for coord in boundary])
                        all_lngs.extend([coord[1] for coord in boundary])
                
                if all_lats and all_lngs:
                    ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
                    ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title(f"{title} - Radius {radius}")
            ax.grid(True, alpha=0.3)
            
            # Convert plot to image
            image = _fig_to_image(fig)
            frames.append(image)
            frame_data.append({
                'radius': radius,
                'frame_idx': frame_idx,
                'cell_count': len(current_cells),
                'total_area': sum(cell_area(cell, 'km^2') for cell in current_cells if is_valid_cell(cell))
            })
            
            plt.close(fig)
    
    # Save as GIF
    if output_path and frames:
        imageio.mimsave(output_path, frames, fps=fps)
        print(f"✅ Saved grid expansion animation to {output_path}")
    
    # Get animation data
    animation_data = {
        'title': title,
        'center_cell': center_cell,
        'max_radius': max_radius,
        'total_frames': len(frames),
        'duration': duration,
        'fps': fps,
        'frame_data': frame_data
    }
    
    return animation_data


def create_resolution_transition_animation(cells: List[str],
                                        start_resolution: int = 6,
                                        end_resolution: int = 12,
                                        title: str = "H3 Resolution Transition Animation",
                                        output_path: Optional[Path] = None,
                                        duration: float = 3.0,
                                        fps: int = 10) -> Dict[str, Any]:
    """
    Create an animation showing transitions between H3 resolutions.
    
    Args:
        cells: List of H3 cell indices
        start_resolution: Starting resolution
        end_resolution: Ending resolution
        title: Title for the animation
        output_path: Path to save the GIF (optional)
        duration: Duration of the animation in seconds
        fps: Frames per second
        
    Returns:
        Dictionary with animation metadata
    """
    frames = []
    frame_data = []
    
    # Calculate frames per resolution
    total_frames = int(duration * fps)
    resolutions = list(range(start_resolution, end_resolution + 1))
    frames_per_resolution = max(1, total_frames // len(resolutions))
    
    print(f"Creating resolution transition animation with {total_frames} frames...")
    
    # Get center coordinates from first cell
    if cells:
        center_lat, center_lng = cell_to_latlng(cells[0])
    else:
        center_lat, center_lng = 37.7749, -122.4194  # San Francisco
    
    for resolution in resolutions:
        # Get cell for this resolution
        current_cell = latlng_to_cell(center_lat, center_lng, resolution)
        
        # Create frame for this resolution
        for frame_idx in range(frames_per_resolution):
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Plot the cell
            if is_valid_cell(current_cell):
                boundary = cell_to_boundary(current_cell)
                area = cell_area(current_cell, 'km^2')
                
                # Convert boundary to plotting coordinates
                lats = [coord[0] for coord in boundary]
                lngs = [coord[1] for coord in boundary]
                
                # Create polygon patch
                polygon = patches.Polygon(list(zip(lngs, lats)), 
                                        facecolor='lightblue', 
                                        edgecolor='navy', 
                                        linewidth=2,
                                        alpha=0.8)
                ax.add_patch(polygon)
                
                # Add cell info
                ax.text(center_lng, center_lat, f'R{resolution}\n{area:.4f} km²', 
                       fontsize=12, ha='center', va='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
            
            # Set plot limits
            if is_valid_cell(current_cell):
                boundary = cell_to_boundary(current_cell)
                lats = [coord[0] for coord in boundary]
                lngs = [coord[1] for coord in boundary]
                
                ax.set_xlim(min(lngs) - 0.01, max(lngs) + 0.01)
                ax.set_ylim(min(lats) - 0.01, max(lats) + 0.01)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title(f"{title} - Resolution {resolution}")
            ax.grid(True, alpha=0.3)
            
            # Convert plot to image
            image = _fig_to_image(fig)
            frames.append(image)
            frame_data.append({
                'resolution': resolution,
                'frame_idx': frame_idx,
                'cell': current_cell,
                'area_km2': cell_area(current_cell, 'km^2') if is_valid_cell(current_cell) else 0
            })
            
            plt.close(fig)
    
    # Save as GIF
    if output_path and frames:
        imageio.mimsave(output_path, frames, fps=fps)
        print(f"✅ Saved resolution transition animation to {output_path}")
    
    # Get animation data
    animation_data = {
        'title': title,
        'start_resolution': start_resolution,
        'end_resolution': end_resolution,
        'total_frames': len(frames),
        'duration': duration,
        'fps': fps,
        'frame_data': frame_data
    }
    
    return animation_data


def create_path_animation(start_cell: str,
                        end_cell: str,
                        title: str = "H3 Path Animation",
                        output_path: Optional[Path] = None,
                        duration: float = 2.0,
                        fps: int = 10) -> Dict[str, Any]:
    """
    Create an animation showing a path between two H3 cells.
    
    Args:
        start_cell: Starting cell
        end_cell: Ending cell
        title: Title for the animation
        output_path: Path to save the GIF (optional)
        duration: Duration of the animation in seconds
        fps: Frames per second
        
    Returns:
        Dictionary with animation metadata
    """
    frames = []
    frame_data = []
    
    try:
        # Get path between cells
        path_cells = grid_path_cells(start_cell, end_cell)
        
        # Calculate frames per cell
        total_frames = int(duration * fps)
        frames_per_cell = max(1, total_frames // len(path_cells))
        
        print(f"Creating path animation with {total_frames} frames...")
        
        for i, cell in enumerate(path_cells):
            # Create frame for this cell
            for frame_idx in range(frames_per_cell):
                # Create the plot
                fig, ax = plt.subplots(figsize=(10, 8))
                
                # Plot all path cells up to current position
                for j, path_cell in enumerate(path_cells[:i+1]):
                    if not is_valid_cell(path_cell):
                        continue
                        
                    boundary = cell_to_boundary(path_cell)
                    
                    # Convert boundary to plotting coordinates
                    lats = [coord[0] for coord in boundary]
                    lngs = [coord[1] for coord in boundary]
                    
                    # Color based on position in path
                    if j == i:  # Current cell
                        color = 'red'
                        alpha = 0.9
                    else:  # Previous cells
                        color = 'lightblue'
                        alpha = 0.5
                    
                    # Create polygon patch
                    polygon = patches.Polygon(list(zip(lngs, lats)), 
                                            facecolor=color, 
                                            edgecolor='navy', 
                                            linewidth=1,
                                            alpha=alpha)
                    ax.add_patch(polygon)
                
                # Set plot limits
                if path_cells:
                    all_lats = []
                    all_lngs = []
                    for path_cell in path_cells:
                        if is_valid_cell(path_cell):
                            boundary = cell_to_boundary(path_cell)
                            all_lats.extend([coord[0] for coord in boundary])
                            all_lngs.extend([coord[1] for coord in boundary])
                    
                    if all_lats and all_lngs:
                        ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
                        ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
                
                ax.set_xlabel('Longitude')
                ax.set_ylabel('Latitude')
                ax.set_title(f"{title} - Progress {i+1}/{len(path_cells)}")
                ax.grid(True, alpha=0.3)
                
                # Convert plot to image
                image = _fig_to_image(fig)
                frames.append(image)
                frame_data.append({
                    'path_index': i,
                    'frame_idx': frame_idx,
                    'current_cell': cell,
                    'progress': (i + 1) / len(path_cells)
                })
                
                plt.close(fig)
        
    except Exception as e:
        print(f"Path animation failed: {e}")
        # Create a simple animation with just start and end cells
        fig, ax = plt.subplots(figsize=(10, 8))
        
        for cell in [start_cell, end_cell]:
            if is_valid_cell(cell):
                boundary = cell_to_boundary(cell)
                lats = [coord[0] for coord in boundary]
                lngs = [coord[1] for coord in boundary]
                
                color = 'red' if cell == start_cell else 'blue'
                polygon = patches.Polygon(list(zip(lngs, lats)), 
                                        facecolor=color, 
                                        edgecolor='black', 
                                        linewidth=2,
                                        alpha=0.8)
                ax.add_patch(polygon)
        
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(f"{title} - Start/End Cells")
        ax.grid(True, alpha=0.3)
        
        fig.canvas.draw()
        image = _fig_to_image(fig)
        
        frames = [image] * 10  # Repeat frame
        frame_data = [{'error': str(e)}] * 10
        
        plt.close(fig)
    
    # Save as GIF
    if output_path and frames:
        imageio.mimsave(output_path, frames, fps=fps)
        print(f"✅ Saved path animation to {output_path}")
    
    # Get animation data
    animation_data = {
        'title': title,
        'start_cell': start_cell,
        'end_cell': end_cell,
        'total_frames': len(frames),
        'duration': duration,
        'fps': fps,
        'frame_data': frame_data
    }
    
    return animation_data


def create_temporal_animation(cells: List[str],
                            time_data: List[Dict[str, Any]],
                            title: str = "H3 Temporal Animation",
                            output_path: Optional[Path] = None,
                            duration: float = 3.0,
                            fps: int = 10) -> Dict[str, Any]:
    """
    Create an animation showing temporal changes in H3 data.
    
    Args:
        cells: List of H3 cell indices
        time_data: List of temporal data dictionaries
        title: Title for the animation
        output_path: Path to save the GIF (optional)
        duration: Duration of the animation in seconds
        fps: Frames per second
        
    Returns:
        Dictionary with animation metadata
    """
    frames = []
    frame_data = []
    
    # Calculate frames per time step
    total_frames = int(duration * fps)
    frames_per_step = max(1, total_frames // len(time_data))
    
    print(f"Creating temporal animation with {total_frames} frames...")
    
    for i, time_step in enumerate(time_data):
        # Create frame for this time step
        for frame_idx in range(frames_per_step):
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Plot cells with temporal properties
            for cell in cells:
                if not is_valid_cell(cell):
                    continue
                    
                boundary = cell_to_boundary(cell)
                resolution = get_resolution(cell)
                
                # Get temporal properties
                activity_level = time_step.get('activity_level', 0.5)
                time_value = time_step.get('time', i)
                
                # Color based on activity level
                color = plt.cm.Reds(activity_level)
                
                # Convert boundary to plotting coordinates
                lats = [coord[0] for coord in boundary]
                lngs = [coord[1] for coord in boundary]
                
                # Create polygon patch
                polygon = patches.Polygon(list(zip(lngs, lats)), 
                                        facecolor=color, 
                                        edgecolor='black', 
                                        linewidth=0.5,
                                        alpha=0.7)
                ax.add_patch(polygon)
            
            # Set plot limits
            if cells:
                all_lats = []
                all_lngs = []
                for cell in cells:
                    if is_valid_cell(cell):
                        boundary = cell_to_boundary(cell)
                        all_lats.extend([coord[0] for coord in boundary])
                        all_lngs.extend([coord[1] for coord in boundary])
                
                if all_lats and all_lngs:
                    ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
                    ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title(f"{title} - Time {time_value}")
            ax.grid(True, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(0, 1))
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label('Activity Level')
            
            # Convert plot to image
            image = _fig_to_image(fig)
            frames.append(image)
            frame_data.append({
                'time_step': i,
                'frame_idx': frame_idx,
                'time_value': time_value,
                'activity_level': activity_level
            })
            
            plt.close(fig)
    
    # Save as GIF
    if output_path and frames:
        imageio.mimsave(output_path, frames, fps=fps)
        print(f"✅ Saved temporal animation to {output_path}")
    
    # Get animation data
    animation_data = {
        'title': title,
        'total_frames': len(frames),
        'duration': duration,
        'fps': fps,
        'time_steps': len(time_data),
        'frame_data': frame_data
    }
    
    return animation_data


def create_animated_heatmap(cells: List[str],
                           center_cell: str,
                           radius: int = 3,
                           title: str = "H3 Animated Heatmap",
                           output_path: Optional[Path] = None,
                           duration: float = 2.0,
                           fps: int = 10) -> Dict[str, Any]:
    """
    Create an animated heatmap showing changing density patterns.
    
    Args:
        cells: List of H3 cell indices
        center_cell: Center cell for the heatmap
        radius: Radius for the heatmap
        title: Title for the animation
        output_path: Path to save the GIF (optional)
        duration: Duration of the animation in seconds
        fps: Frames per second
        
    Returns:
        Dictionary with animation metadata
    """
    from traversal import grid_disk
    
    frames = []
    frame_data = []
    
    # Create a grid around the center cell
    grid_cells = grid_disk(center_cell, radius)
    
    # Calculate frames
    total_frames = int(duration * fps)
    frames_per_pattern = max(1, total_frames // 4)  # 4 different patterns
    
    print(f"Creating animated heatmap with {total_frames} frames...")
    
    # Create different density patterns
    patterns = [
        lambda x, y: np.sin(x * 2) * np.cos(y * 2),  # Wave pattern
        lambda x, y: np.exp(-(x**2 + y**2) / 2),     # Gaussian pattern
        lambda x, y: np.abs(x) + np.abs(y),           # Manhattan pattern
        lambda x, y: np.sin(x + y)                    # Diagonal pattern
    ]
    
    for pattern_idx, pattern_func in enumerate(patterns):
        for frame_idx in range(frames_per_pattern):
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Calculate density for each cell in the grid
            for cell in grid_cells:
                if not is_valid_cell(cell):
                    continue
                    
                center_lat, center_lng = cell_to_latlng(cell)
                
                # Normalize coordinates for pattern
                x = (center_lng + 180) / 360  # Normalize longitude
                y = (center_lat + 90) / 180   # Normalize latitude
                
                # Calculate density using pattern function
                density = max(0, min(1, pattern_func(x, y)))
                
                boundary = cell_to_boundary(cell)
                lats = [coord[0] for coord in boundary]
                lngs = [coord[1] for coord in boundary]
                
                # Color based on density
                color = plt.cm.Reds(density)
                
                polygon = patches.Polygon(list(zip(lngs, lats)), 
                                        facecolor=color, 
                                        edgecolor='black', 
                                        linewidth=0.5,
                                        alpha=0.8)
                ax.add_patch(polygon)
                
                # Add density label
                ax.text(center_lng, center_lat, f'{density:.2f}', 
                       fontsize=6, ha='center', va='center', 
                       color='white' if density > 0.5 else 'black')
            
            # Set plot limits
            if grid_cells:
                all_lats = []
                all_lngs = []
                for cell in grid_cells:
                    if is_valid_cell(cell):
                        boundary = cell_to_boundary(cell)
                        all_lats.extend([coord[0] for coord in boundary])
                        all_lngs.extend([coord[1] for coord in boundary])
                
                if all_lats and all_lngs:
                    ax.set_xlim(min(all_lngs) - 0.01, max(all_lngs) + 0.01)
                    ax.set_ylim(min(all_lats) - 0.01, max(all_lats) + 0.01)
            
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.set_title(f"{title} - Pattern {pattern_idx + 1}")
            ax.grid(True, alpha=0.3)
            
            # Add colorbar
            sm = plt.cm.ScalarMappable(cmap=plt.cm.Reds, norm=plt.Normalize(0, 1))
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label('Density')
            
            # Convert plot to image
            image = _fig_to_image(fig)
            frames.append(image)
            frame_data.append({
                'pattern_idx': pattern_idx,
                'frame_idx': frame_idx,
                'pattern_func': pattern_func.__name__ if hasattr(pattern_func, '__name__') else 'unknown'
            })
            
            plt.close(fig)
    
    # Save as GIF
    if output_path and frames:
        imageio.mimsave(output_path, frames, fps=fps)
        print(f"✅ Saved animated heatmap to {output_path}")
    
    # Get animation data
    animation_data = {
        'title': title,
        'center_cell': center_cell,
        'radius': radius,
        'total_frames': len(frames),
        'duration': duration,
        'fps': fps,
        'patterns': len(patterns),
        'frame_data': frame_data
    }
    
    return animation_data


def generate_animation_report(cells: List[str],
                            output_dir: Path,
                            title: str = "H3 Animation Report") -> Dict[str, Any]:
    """
    Generate a comprehensive animation report for H3 cells.
    
    Args:
        cells: List of H3 cell indices
        output_dir: Directory to save animations
        title: Title for the report
        
    Returns:
        Dictionary with report metadata
    """
    output_dir.mkdir(exist_ok=True)
    
    report_data = {
        'title': title,
        'total_cells': len(cells),
        'animations': {}
    }
    
    if cells:
        center_cell = cells[0]
        
        # Generate grid expansion animation
        expansion_path = output_dir / "grid_expansion.gif"
        expansion_data = create_grid_expansion_animation(
            cells, center_cell, output_path=expansion_path
        )
        report_data['animations']['grid_expansion'] = expansion_data
        
        # Generate resolution transition animation
        transition_path = output_dir / "resolution_transition.gif"
        transition_data = create_resolution_transition_animation(
            cells, output_path=transition_path
        )
        report_data['animations']['resolution_transition'] = transition_data
        
        # Generate path animation (if we have at least 2 cells)
        if len(cells) >= 2:
            path_path = output_dir / "path_animation.gif"
            path_data = create_path_animation(
                cells[0], cells[-1], output_path=path_path
            )
            report_data['animations']['path_animation'] = path_data
        
        # Generate animated heatmap
        heatmap_path = output_dir / "animated_heatmap.gif"
        heatmap_data = create_animated_heatmap(
            cells, center_cell, output_path=heatmap_path
        )
        report_data['animations']['animated_heatmap'] = heatmap_data
    
    # Save report metadata
    report_path = output_dir / "animation_report.json"
    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"✅ Generated animation report with {len(report_data['animations'])} animations")
    return report_data
