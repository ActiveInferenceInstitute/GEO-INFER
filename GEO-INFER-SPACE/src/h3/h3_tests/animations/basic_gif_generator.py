#!/usr/bin/env python3
"""
Basic H3 GIF Animation Generator

Creates animated GIF files from H3 animation data using a simple PNG-to-GIF approach.
Avoids matplotlib canvas issues by saving frames as temporary files.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import os
from typing import Dict, List, Tuple, Any, Optional
import h3
import imageio


class BasicH3GIFGenerator:
    """
    Basic GIF generator that saves frames as PNG files first.
    More reliable than direct canvas manipulation.
    """
    
    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialize the GIF generator."""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up matplotlib style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (10, 8)
        plt.rcParams['figure.dpi'] = 100
        
    def load_animation_data(self, filename: str) -> Dict[str, Any]:
        """Load animation data from JSON file."""
        file_path = self.input_dir / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def create_basic_resolution_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a basic resolution transition GIF."""
        frames = animation_data['frames']
        location = animation_data['location']
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            
            for i, frame in enumerate(frames):
                # Create figure
                fig, ax = plt.subplots(figsize=(10, 8))
                
                resolution = frame['resolution']
                center = frame['center']
                boundary = frame['boundary']
                area = frame['area_km2']
                
                # Plot cell boundary
                boundary_coords = np.array(boundary)
                ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'b-', linewidth=2)
                ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.3, color='blue')
                
                # Plot center point
                ax.plot(center[1], center[0], 'ro', markersize=8)
                
                # Set title and labels
                ax.set_title(f'H3 Resolution Transition - {location.title()}\n'
                            f'Resolution: {resolution}, Area: {area:.2f} km²', 
                            fontsize=12, fontweight='bold')
                ax.set_xlabel('Longitude', fontsize=10)
                ax.set_ylabel('Latitude', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Set aspect ratio
                ax.set_aspect('equal')
                
                # Save frame as PNG
                frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                fig.savefig(frame_path, dpi=100, bbox_inches='tight')
                frame_files.append(frame_path)
                
                plt.close(fig)
            
            # Create GIF from PNG files
            gif_path = self.output_dir / output_filename
            images = [imageio.imread(frame_file) for frame_file in frame_files]
            imageio.mimsave(gif_path, images, fps=2, duration=0.5)
        
        print(f"✅ Created resolution animation: {output_filename}")
    
    def create_basic_grid_expansion_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a basic grid expansion GIF."""
        frames = animation_data['frames']
        location = animation_data['location']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            
            for i, frame in enumerate(frames):
                fig, ax = plt.subplots(figsize=(10, 8))
                
                radius = frame['radius']
                cells = frame['cells']
                base_cell_center = frame['base_cell_center']
                total_area = frame['total_area_km2']
                
                # Plot all cells
                colors = plt.cm.viridis(np.linspace(0, 1, len(cells)))
                
                for j, cell in enumerate(cells):
                    try:
                        boundary = h3.cell_to_boundary(cell)
                        boundary_coords = np.array(boundary)
                        color = colors[j]
                        
                        ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 
                               color=color, linewidth=1.5)
                        ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], 
                               color=color, alpha=0.4)
                    except:
                        pass
                
                # Plot base cell center
                ax.plot(base_cell_center[1], base_cell_center[0], 'ro', markersize=10)
                
                # Set title and labels
                ax.set_title(f'H3 Grid Expansion - {location.title()}\n'
                            f'Radius: {radius}, Cells: {len(cells)}, Area: {total_area:.2f} km²', 
                            fontsize=12, fontweight='bold')
                ax.set_xlabel('Longitude', fontsize=10)
                ax.set_ylabel('Latitude', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Set aspect ratio
                ax.set_aspect('equal')
                
                # Save frame as PNG
                frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                fig.savefig(frame_path, dpi=100, bbox_inches='tight')
                frame_files.append(frame_path)
                
                plt.close(fig)
            
            # Create GIF from PNG files
            gif_path = self.output_dir / output_filename
            images = [imageio.imread(frame_file) for frame_file in frame_files]
            imageio.mimsave(gif_path, images, fps=1.5, duration=0.67)
        
        print(f"✅ Created grid expansion animation: {output_filename}")
    
    def create_basic_path_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a basic path finding GIF."""
        frames = animation_data['frames']
        start_location = animation_data['start_location']
        end_location = animation_data['end_location']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            
            for i, frame in enumerate(frames):
                fig, ax = plt.subplots(figsize=(10, 8))
                
                center = frame['center']
                boundary = frame['boundary']
                progress = frame['path_progress']
                
                # Plot current cell
                boundary_coords = np.array(boundary)
                ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'b-', linewidth=2)
                ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.6, color='blue')
                
                # Plot center point
                ax.plot(center[1], center[0], 'ro', markersize=8)
                
                # Plot path progress
                if i > 0:
                    for j in range(i):
                        prev_frame = frames[j]
                        prev_center = prev_frame['center']
                        ax.plot(prev_center[1], prev_center[0], 'go', markersize=4, alpha=0.5)
                
                # Set title and labels
                ax.set_title(f'H3 Path Finding - {start_location.title()} to {end_location.title()}\n'
                            f'Progress: {progress:.1%}', 
                            fontsize=12, fontweight='bold')
                ax.set_xlabel('Longitude', fontsize=10)
                ax.set_ylabel('Latitude', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Set aspect ratio
                ax.set_aspect('equal')
                
                # Save frame as PNG
                frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                fig.savefig(frame_path, dpi=100, bbox_inches='tight')
                frame_files.append(frame_path)
                
                plt.close(fig)
            
            # Create GIF from PNG files
            gif_path = self.output_dir / output_filename
            images = [imageio.imread(frame_file) for frame_file in frame_files]
            imageio.mimsave(gif_path, images, fps=2, duration=0.5)
        
        print(f"✅ Created path animation: {output_filename}")
    
    def create_basic_hierarchy_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a basic hierarchy GIF."""
        frames = animation_data['frames']
        location = animation_data['location']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            
            for i, frame in enumerate(frames):
                fig, ax = plt.subplots(figsize=(10, 8))
                
                hierarchy_type = frame.get('hierarchy_type', 'parent')
                
                if hierarchy_type == 'parent':
                    # Single parent cell
                    center = frame['center']
                    boundary = frame['boundary']
                    area = frame['area_km2']
                    
                    boundary_coords = np.array(boundary)
                    ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'r-', linewidth=3)
                    ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.4, color='red')
                    ax.plot(center[1], center[0], 'ro', markersize=10)
                    
                    title = f'H3 Hierarchy - {location.title()} (Parent)\nArea: {area:.2f} km²'
                    
                else:
                    # Multiple child cells
                    cells = frame['cells']
                    centers = frame['centers']
                    areas = frame['areas_km2']
                    
                    colors = plt.cm.Set3(np.linspace(0, 1, len(cells)))
                    
                    for j, cell in enumerate(cells):
                        try:
                            boundary = h3.cell_to_boundary(cell)
                            boundary_coords = np.array(boundary)
                            color = colors[j]
                            
                            ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 
                                   color=color, linewidth=2)
                            ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], 
                                   color=color, alpha=0.3)
                            ax.plot(centers[j][1], centers[j][0], 'o', 
                                   color=color, markersize=6)
                        except:
                            pass
                    
                    title = f'H3 Hierarchy - {location.title()} (Children)\nCells: {len(cells)}, Total Area: {sum(areas):.2f} km²'
                
                # Set title and labels
                ax.set_title(title, fontsize=12, fontweight='bold')
                ax.set_xlabel('Longitude', fontsize=10)
                ax.set_ylabel('Latitude', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Set aspect ratio
                ax.set_aspect('equal')
                
                # Save frame as PNG
                frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                fig.savefig(frame_path, dpi=100, bbox_inches='tight')
                frame_files.append(frame_path)
                
                plt.close(fig)
            
            # Create GIF from PNG files
            gif_path = self.output_dir / output_filename
            images = [imageio.imread(frame_file) for frame_file in frame_files]
            imageio.mimsave(gif_path, images, fps=1.2, duration=0.83)
        
        print(f"✅ Created hierarchy animation: {output_filename}")
    
    def create_basic_spatial_distribution_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a basic spatial distribution GIF."""
        frames = animation_data['frames']
        location = animation_data['location']
        pattern = animation_data['pattern']
        
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            
            for i, frame in enumerate(frames):
                fig, ax = plt.subplots(figsize=(10, 8))
                
                cells = frame['cells']
                centers = frame['centers']
                areas = frame['areas_km2']
                pattern_type = frame['pattern']
                
                # Plot cells with color based on area
                if cells:
                    max_area = max(areas) if areas else 1
                    colors = plt.cm.plasma([area/max_area for area in areas])
                    
                    for j, cell in enumerate(cells):
                        try:
                            boundary = h3.cell_to_boundary(cell)
                            boundary_coords = np.array(boundary)
                            color = colors[j]
                            
                            ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 
                                   color=color, linewidth=1.5)
                            ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], 
                                   color=color, alpha=0.4)
                            ax.plot(centers[j][1], centers[j][0], 'o', 
                                   color=color, markersize=4)
                        except:
                            pass
                
                # Set title and labels
                ax.set_title(f'H3 Spatial Distribution - {location.title()} ({pattern_type.title()})\n'
                            f'Cells: {len(cells)}, Total Area: {sum(areas):.2f} km²', 
                            fontsize=12, fontweight='bold')
                ax.set_xlabel('Longitude', fontsize=10)
                ax.set_ylabel('Latitude', fontsize=10)
                ax.grid(True, alpha=0.3)
                
                # Set aspect ratio
                ax.set_aspect('equal')
                
                # Save frame as PNG
                frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                fig.savefig(frame_path, dpi=100, bbox_inches='tight')
                frame_files.append(frame_path)
                
                plt.close(fig)
            
            # Create GIF from PNG files
            gif_path = self.output_dir / output_filename
            images = [imageio.imread(frame_file) for frame_file in frame_files]
            imageio.mimsave(gif_path, images, fps=2, duration=0.5)
        
        print(f"✅ Created spatial distribution animation: {output_filename}")
    
    def generate_all_gifs(self) -> None:
        """Generate GIF animations for all available JSON files."""
        print("🎬 Generating H3 Animation GIFs (Basic Method)...")
        
        # Find all JSON animation files
        json_files = list(self.input_dir.glob('*.json'))
        
        # Filter out summary files
        animation_files = [f for f in json_files if not f.name.startswith(('animation_summary', 'comprehensive'))]
        
        gifs_created = 0
        
        for json_file in animation_files:
            try:
                # Load animation data
                animation_data = self.load_animation_data(json_file.name)
                animation_type = animation_data.get('animation_type', 'unknown')
                
                # Generate appropriate GIF based on animation type
                gif_filename = json_file.stem + '.gif'
                
                if animation_type == 'resolution_transition':
                    self.create_basic_resolution_gif(animation_data, gif_filename)
                    gifs_created += 1
                    
                elif animation_type == 'grid_expansion':
                    self.create_basic_grid_expansion_gif(animation_data, gif_filename)
                    gifs_created += 1
                    
                elif animation_type == 'path_finding':
                    self.create_basic_path_gif(animation_data, gif_filename)
                    gifs_created += 1
                    
                elif animation_type == 'hierarchy':
                    self.create_basic_hierarchy_gif(animation_data, gif_filename)
                    gifs_created += 1
                    
                elif animation_type == 'spatial_distribution':
                    self.create_basic_spatial_distribution_gif(animation_data, gif_filename)
                    gifs_created += 1
                    
            except Exception as e:
                print(f"❌ Error processing {json_file.name}: {e}")
        
        print(f"🎉 Generated {gifs_created} GIF animations!")
        
        # Create a summary of generated GIFs
        self._create_gif_summary()
    
    def _create_gif_summary(self) -> None:
        """Create a summary of generated GIF files."""
        gif_files = list(self.output_dir.glob('*.gif'))
        
        summary = {
            'total_gifs_generated': len(gif_files),
            'gif_files': [f.name for f in gif_files],
            'animation_types': {
                'resolution_transition': len([f for f in gif_files if 'resolution' in f.name]),
                'grid_expansion': len([f for f in gif_files if 'grid_expansion' in f.name]),
                'path_finding': len([f for f in gif_files if 'path' in f.name]),
                'hierarchy': len([f for f in gif_files if 'hierarchy' in f.name]),
                'spatial_distribution': len([f for f in gif_files if 'spatial_distribution' in f.name])
            },
            'total_size_mb': sum(f.stat().st_size for f in gif_files) / (1024 * 1024)
        }
        
        # Save JSON summary
        with open(self.output_dir / 'gif_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Create markdown summary
        md_content = f"""# H3 Animation GIFs Summary

Generated: {len(gif_files)} GIF animations

## Animation Types
- **Resolution Transitions**: {summary['animation_types']['resolution_transition']} GIFs
- **Grid Expansions**: {summary['animation_types']['grid_expansion']} GIFs
- **Path Finding**: {summary['animation_types']['path_finding']} GIFs
- **Hierarchy**: {summary['animation_types']['hierarchy']} GIFs
- **Spatial Distribution**: {summary['animation_types']['spatial_distribution']} GIFs

## Files Generated
{chr(10).join([f'- {f.name}' for f in gif_files])}

## Statistics
- **Total GIFs**: {len(gif_files)}
- **Total Size**: {summary['total_size_mb']:.2f} MB
- **Average Size**: {summary['total_size_mb']/len(gif_files):.2f} MB per GIF

## Usage
These GIF files can be used for:
- Presentations and demonstrations
- Documentation and tutorials
- Web applications and dashboards
- Educational materials
"""
        
        with open(self.output_dir / 'gif_summary.md', 'w') as f:
            f.write(md_content)
        
        print(f"📊 Created GIF summary: {len(gif_files)} GIFs, {summary['total_size_mb']:.2f} MB total")


def main():
    """Main function to generate all GIF animations."""
    input_dir = Path('outputs/animations')
    output_dir = Path('outputs/animations/gifs')
    
    generator = BasicH3GIFGenerator(input_dir, output_dir)
    generator.generate_all_gifs()


if __name__ == '__main__':
    main() 