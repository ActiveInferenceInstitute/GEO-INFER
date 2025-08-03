#!/usr/bin/env python3
"""
H3 Visual Test Generator

Generates comprehensive visual outputs including images, animations, and interactive plots.
Demonstrates H3 geospatial operations with visual confirmation.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Polygon
import seaborn as sns
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import h3


class H3VisualTestGenerator:
    """
    Comprehensive visual test generator for H3 operations.
    """
    
    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize the visual test generator.
        
        Args:
            output_dir: Directory for visual outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
    def generate_all_visuals(self):
        """Generate all visual outputs."""
        print("🎨 Generating Visual Test Outputs...")
        
        # Generate static images
        self._generate_h3_cell_visualizations()
        self._generate_grid_traversal_visualizations()
        self._generate_hierarchy_visualizations()
        self._generate_performance_visualizations()
        
        # Generate animations
        self._generate_resolution_animations()
        self._generate_traversal_animations()
        self._generate_hierarchy_animations()
        
        print("✅ All visual outputs generated!")
    
    def _generate_h3_cell_visualizations(self):
        """Generate H3 cell visualizations."""
        print("  📊 Generating H3 cell visualizations...")
        
        # Test coordinates
        lat, lng = 37.7749, -122.4194  # San Francisco
        resolutions = [0, 3, 6, 9, 12]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        for i, res in enumerate(resolutions):
            if i >= len(axes):
                break
                
            cell = h3.latlng_to_cell(lat, lng, res)
            boundary = h3.cell_to_boundary(cell)
            
            # Convert to plotting coordinates
            lngs, lats = zip(*boundary)
            
            # Plot cell
            axes[i].plot(lngs, lats, 'b-', linewidth=2)
            axes[i].fill(lngs, lats, alpha=0.3, color='blue')
            
            # Plot center
            center_lat, center_lng = h3.cell_to_latlng(cell)
            axes[i].plot(center_lng, center_lat, 'ro', markersize=8)
            
            axes[i].set_title(f'Resolution {res}\nCell: {cell}')
            axes[i].set_aspect('equal')
            axes[i].grid(True, alpha=0.3)
        
        # Remove extra subplot
        if len(resolutions) < len(axes):
            axes[-1].remove()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "h3_cells.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_grid_traversal_visualizations(self):
        """Generate grid traversal visualizations."""
        print("  🔄 Generating grid traversal visualizations...")
        
        # Test cell
        cell = '89283082e73ffff'
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Grid disk
        disk_cells = h3.grid_disk(cell, 2)
        self._plot_cells(disk_cells, axes[0], "Grid Disk (k=2)")
        
        # Grid ring
        ring_cells = h3.grid_ring(cell, 1)
        self._plot_cells(ring_cells, axes[1], "Grid Ring (k=1)")
        
        # Grid path
        target = '89283082e77ffff'
        path_cells = h3.grid_path_cells(cell, target)
        self._plot_cells(path_cells, axes[2], "Grid Path")
        
        # Neighbors
        neighbors = h3.grid_ring(cell, 1)
        self._plot_cells(neighbors, axes[3], "Neighbors")
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "grid_traversal.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_cells(self, cells: List[str], ax, title: str):
        """Plot H3 cells on an axis."""
        colors = plt.cm.Set3(np.linspace(0, 1, len(cells)))
        
        for i, cell in enumerate(cells):
            boundary = h3.cell_to_boundary(cell)
            lngs, lats = zip(*boundary)
            
            ax.plot(lngs, lats, color=colors[i], linewidth=1)
            ax.fill(lngs, lats, alpha=0.3, color=colors[i])
            
            # Plot center
            center_lat, center_lng = h3.cell_to_latlng(cell)
            ax.plot(center_lng, center_lat, 'ko', markersize=4)
        
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    def _generate_hierarchy_visualizations(self):
        """Generate hierarchy visualizations."""
        print("  🌳 Generating hierarchy visualizations...")
        
        # Test cell
        cell = '89283082e73ffff'
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        # Parent-child relationships
        parent = h3.cell_to_parent(cell, 8)
        children = h3.cell_to_children(cell, 10)
        
        # Plot parent
        self._plot_cells([parent], axes[0], "Parent")
        
        # Plot original cell
        self._plot_cells([cell], axes[1], "Original Cell")
        
        # Plot children
        self._plot_cells(children[:7], axes[2], "Children")
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "hierarchy.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_performance_visualizations(self):
        """Generate performance visualizations."""
        print("  ⚡ Generating performance visualizations...")
        
        # Test different resolutions
        resolutions = list(range(0, 16))
        operations = ['latlng_to_cell', 'cell_to_latlng', 'cell_area', 'grid_disk']
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        for i, op in enumerate(operations):
            times = []
            for res in resolutions:
                # Simple performance test
                start_time = time.time()
                for _ in range(100):
                    if op == 'latlng_to_cell':
                        h3.latlng_to_cell(37.7749, -122.4194, res)
                    elif op == 'cell_to_latlng':
                        cell = h3.latlng_to_cell(37.7749, -122.4194, res)
                        h3.cell_to_latlng(cell)
                    elif op == 'cell_area':
                        cell = h3.latlng_to_cell(37.7749, -122.4194, res)
                        h3.cell_area(cell)
                    elif op == 'grid_disk':
                        cell = h3.latlng_to_cell(37.7749, -122.4194, res)
                        h3.grid_disk(cell, 1)
                
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convert to ms
            
            axes[i].plot(resolutions, times, 'o-')
            axes[i].set_title(f'{op} Performance')
            axes[i].set_xlabel('Resolution')
            axes[i].set_ylabel('Time (ms)')
            axes[i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / "performance.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _generate_resolution_animations(self):
        """Generate resolution animations."""
        print("  🎬 Generating resolution animations...")
        
        lat, lng = 37.7749, -122.4194
        resolutions = list(range(0, 16))
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def animate(frame):
            ax.clear()
            
            res = resolutions[frame]
            cell = h3.latlng_to_cell(lat, lng, res)
            boundary = h3.cell_to_boundary(cell)
            
            lngs, lats = zip(*boundary)
            ax.plot(lngs, lats, 'b-', linewidth=2)
            ax.fill(lngs, lats, alpha=0.3, color='blue')
            
            center_lat, center_lng = h3.cell_to_latlng(cell)
            ax.plot(center_lng, center_lat, 'ro', markersize=8)
            
            ax.set_title(f'Resolution {res}\nCell: {cell}')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        anim = animation.FuncAnimation(fig, animate, frames=len(resolutions), 
                                     interval=500, repeat=True)
        anim.save(self.output_dir / "resolution_animation.gif", writer='pillow')
        plt.close()
    
    def _generate_traversal_animations(self):
        """Generate traversal animations."""
        print("  🎬 Generating traversal animations...")
        
        cell = '89283082e73ffff'
        max_k = 5
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def animate(frame):
            ax.clear()
            
            k = frame + 1
            disk_cells = h3.grid_disk(cell, k)
            
            colors = plt.cm.viridis(np.linspace(0, 1, len(disk_cells)))
            
            for i, disk_cell in enumerate(disk_cells):
                boundary = h3.cell_to_boundary(disk_cell)
                lngs, lats = zip(*boundary)
                
                ax.plot(lngs, lats, color=colors[i], linewidth=1)
                ax.fill(lngs, lats, alpha=0.3, color=colors[i])
            
            # Plot center
            center_lat, center_lng = h3.cell_to_latlng(cell)
            ax.plot(center_lng, center_lat, 'ro', markersize=10)
            
            ax.set_title(f'Grid Disk (k={k})\nCells: {len(disk_cells)}')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        anim = animation.FuncAnimation(fig, animate, frames=max_k, 
                                     interval=800, repeat=True)
        anim.save(self.output_dir / "traversal_animation.gif", writer='pillow')
        plt.close()
    
    def _generate_hierarchy_animations(self):
        """Generate hierarchy animations."""
        print("  🎬 Generating hierarchy animations...")
        
        cell = '89283082e73ffff'
        start_res = h3.get_resolution(cell)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        def animate(frame):
            ax.clear()
            
            target_res = start_res - 3 + frame
            if target_res < 0:
                target_res = 0
            
            if target_res < start_res:
                # Go up hierarchy
                current_cell = cell
                for res in range(start_res - 1, target_res - 1, -1):
                    current_cell = h3.cell_to_parent(current_cell, res)
            else:
                # Go down hierarchy
                current_cell = cell
                for res in range(start_res + 1, target_res + 1):
                    current_cell = h3.cell_to_center_child(current_cell, res)
            
            boundary = h3.cell_to_boundary(current_cell)
            lngs, lats = zip(*boundary)
            
            ax.plot(lngs, lats, 'b-', linewidth=2)
            ax.fill(lngs, lats, alpha=0.3, color='blue')
            
            center_lat, center_lng = h3.cell_to_latlng(current_cell)
            ax.plot(center_lng, center_lat, 'ro', markersize=8)
            
            ax.set_title(f'Resolution {target_res}\nCell: {current_cell}')
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
        
        anim = animation.FuncAnimation(fig, animate, frames=6, 
                                     interval=600, repeat=True)
        anim.save(self.output_dir / "hierarchy_animation.gif", writer='pillow')
        plt.close()


def main():
    """Main function to generate visual outputs."""
    generator = H3VisualTestGenerator()
    generator.generate_all_visuals()
    print("🎨 Visual test generation complete!")
    return 0


if __name__ == "__main__":
    import time
    sys.exit(main()) 