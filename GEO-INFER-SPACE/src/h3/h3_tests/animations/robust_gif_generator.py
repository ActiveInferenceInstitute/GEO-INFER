#!/usr/bin/env python3
"""
Robust H3 GIF Animation Generator

Creates animated GIF files from H3 animation data with consistent frame sizes.
Handles all animation types and ensures reliable generation.

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
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import h3
import imageio.v2 as imageio
from PIL import Image


class RobustH3GIFGenerator:
    """
    Robust GIF generator that ensures consistent frame sizes.
    Handles all animation types with proper error handling.
    """
    
    def __init__(self, input_dir: Path, output_dir: Path):
        """Initialize the GIF generator."""
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up matplotlib style with consistent dimensions
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 10)
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.bbox'] = 'tight'
        plt.rcParams['savefig.pad_inches'] = 0.1
        
    def load_animation_data(self, filename: str) -> Dict[str, Any]:
        """Load animation data from JSON file."""
        file_path = self.input_dir / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def create_robust_gif(self, animation_data: Dict[str, Any], output_filename: str) -> None:
        """Create a robust GIF with consistent frame sizes and timing information."""
        import time
        
        start_time = time.time()
        frames = animation_data['frames']
        animation_type = animation_data.get('animation_type', 'unknown')
        
        # Optimize for long-distance animations
        is_long_distance = False
        if animation_type == 'path_finding':
            start_loc = animation_data.get('start_location', '')
            end_loc = animation_data.get('end_location', '')
            if 'new_york' in start_loc.lower() and 'chicago' in end_loc.lower():
                is_long_distance = True
                print(f"🛣️  Processing long-distance animation: {start_loc} to {end_loc}")
        
        # Create temporary directory for frames
        with tempfile.TemporaryDirectory() as temp_dir:
            frame_files = []
            frame_start_time = time.time()
            
            for i, frame in enumerate(frames):
                frame_time = time.time()
                try:
                    # Create figure with consistent size
                    fig, ax = plt.subplots(figsize=(12, 10))
                    
                    # Generate frame content based on animation type
                    self._plot_frame_content(ax, frame, animation_data, animation_type)
                    
                    # Set consistent title and labels
                    self._set_frame_labels(ax, frame, animation_data, animation_type)
                    
                    # Set consistent aspect ratio and grid
                    ax.set_aspect('equal')
                    ax.grid(True, alpha=0.3)
                    
                    # Save frame as PNG with consistent dimensions
                    frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                    fig.savefig(frame_path, dpi=100, bbox_inches='tight', pad_inches=0.1)
                    frame_files.append(frame_path)
                    
                    plt.close(fig)
                    
                    # Progress reporting for long animations
                    if is_long_distance and i % 10 == 0:
                        elapsed = time.time() - frame_start_time
                        remaining_frames = len(frames) - i - 1
                        if elapsed > 0:
                            fps = i / elapsed
                            eta = remaining_frames / fps if fps > 0 else 0
                            print(f"   📊 Frame {i}/{len(frames)} ({i/len(frames)*100:.1f}%) - ETA: {eta:.1f}s")
                    
                except Exception as e:
                    print(f"⚠️ Warning: Error in frame {i}: {e}")
                    # Create a blank frame as fallback
                    fig, ax = plt.subplots(figsize=(12, 10))
                    ax.text(0.5, 0.5, f'Frame {i}\nError: {str(e)[:50]}', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    frame_path = os.path.join(temp_dir, f'frame_{i:03d}.png')
                    fig.savefig(frame_path, dpi=100, bbox_inches='tight', pad_inches=0.1)
                    frame_files.append(frame_path)
                    plt.close(fig)
            
            frame_generation_time = time.time() - frame_start_time
            
            # Ensure all frames have the same size
            normalize_start = time.time()
            self._normalize_frame_sizes(frame_files)
            normalize_time = time.time() - normalize_start
            
            # Create GIF from normalized frames
            gif_start = time.time()
            gif_path = self.output_dir / output_filename
            try:
                images = [imageio.imread(frame_file) for frame_file in frame_files]
                imageio.mimsave(gif_path, images, fps=2, duration=0.5)
                gif_creation_time = time.time() - gif_start
                total_time = time.time() - start_time
                
                # Print detailed timing information
                print(f"✅ Created {animation_type} animation: {output_filename}")
                print(f"   ⏱️  Frame generation: {frame_generation_time:.2f}s")
                print(f"   🔧 Frame normalization: {normalize_time:.2f}s")
                print(f"   🎬 GIF creation: {gif_creation_time:.2f}s")
                print(f"   📊 Total time: {total_time:.2f}s")
                print(f"   📁 File size: {gif_path.stat().st_size / (1024*1024):.2f} MB")
                
                # Save timing data
                timing_data = {
                    'animation_type': animation_type,
                    'filename': output_filename,
                    'frame_count': len(frames),
                    'frame_generation_time': frame_generation_time,
                    'normalization_time': normalize_time,
                    'gif_creation_time': gif_creation_time,
                    'total_time': total_time,
                    'file_size_mb': gif_path.stat().st_size / (1024*1024),
                    'is_long_distance': is_long_distance,
                    'timestamp': datetime.now().isoformat()
                }
                
                timing_file = self.output_dir / f"{Path(output_filename).stem}_timing.json"
                with open(timing_file, 'w') as f:
                    json.dump(timing_data, f, indent=2)
                    
            except Exception as e:
                print(f"❌ Error creating GIF {output_filename}: {e}")
    
    def _plot_frame_content(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any], animation_type: str) -> None:
        """Plot frame content based on animation type."""
        if animation_type == 'resolution_transition':
            self._plot_resolution_frame(ax, frame, animation_data)
        elif animation_type == 'grid_expansion':
            self._plot_grid_expansion_frame(ax, frame, animation_data)
        elif animation_type == 'path_finding':
            self._plot_path_frame(ax, frame, animation_data)
        elif animation_type == 'hierarchy':
            self._plot_hierarchy_frame(ax, frame, animation_data)
        elif animation_type == 'spatial_distribution':
            self._plot_spatial_distribution_frame(ax, frame, animation_data)
        else:
            # Default plotting for unknown types
            self._plot_generic_frame(ax, frame)
    
    def _plot_resolution_frame(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any]) -> None:
        """Plot resolution transition frame."""
        try:
            center = frame['center']
            boundary = frame['boundary']
            resolution = frame['resolution']
            area = frame['area_km2']
            
            # Plot cell boundary
            boundary_coords = np.array(boundary)
            ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'b-', linewidth=3)
            ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.3, color='blue')
            
            # Plot center point
            ax.plot(center[1], center[0], 'ro', markersize=10)
            
        except Exception as e:
            print(f"⚠️ Error plotting resolution frame: {e}")
    
    def _plot_grid_expansion_frame(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any]) -> None:
        """Plot grid expansion frame."""
        try:
            cells = frame['cells']
            base_cell_center = frame['base_cell_center']
            
            # Plot all cells
            colors = plt.cm.viridis(np.linspace(0, 1, len(cells)))
            
            for j, cell in enumerate(cells):
                try:
                    boundary = h3.cell_to_boundary(cell)
                    boundary_coords = np.array(boundary)
                    color = colors[j]
                    
                    ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 
                           color=color, linewidth=2)
                    ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], 
                           color=color, alpha=0.4)
                except:
                    pass
            
            # Plot base cell center
            ax.plot(base_cell_center[1], base_cell_center[0], 'ro', markersize=12)
            
        except Exception as e:
            print(f"⚠️ Error plotting grid expansion frame: {e}")
    
    def _plot_path_frame(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any]) -> None:
        """Plot path finding frame."""
        try:
            center = frame['center']
            boundary = frame['boundary']
            
            # Plot current cell
            boundary_coords = np.array(boundary)
            ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'b-', linewidth=3)
            ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.6, color='blue')
            
            # Plot center point
            ax.plot(center[1], center[0], 'ro', markersize=10)
            
        except Exception as e:
            print(f"⚠️ Error plotting path frame: {e}")
    
    def _plot_hierarchy_frame(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any]) -> None:
        """Plot hierarchy frame."""
        try:
            hierarchy_type = frame.get('hierarchy_type', 'parent')
            
            if hierarchy_type == 'parent':
                # Single parent cell
                center = frame['center']
                boundary = frame['boundary']
                
                boundary_coords = np.array(boundary)
                ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'r-', linewidth=4)
                ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], alpha=0.4, color='red')
                ax.plot(center[1], center[0], 'ro', markersize=12)
                
            else:
                # Multiple child cells
                cells = frame['cells']
                centers = frame['centers']
                
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
                               color=color, markersize=8)
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ Error plotting hierarchy frame: {e}")
    
    def _plot_spatial_distribution_frame(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any]) -> None:
        """Plot spatial distribution frame."""
        try:
            cells = frame['cells']
            centers = frame['centers']
            areas = frame['areas_km2']
            
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
                               color=color, linewidth=2)
                        ax.fill(boundary_coords[:, 1], boundary_coords[:, 0], 
                               color=color, alpha=0.4)
                        ax.plot(centers[j][1], centers[j][0], 'o', 
                               color=color, markersize=6)
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ Error plotting spatial distribution frame: {e}")
    
    def _plot_generic_frame(self, ax, frame: Dict[str, Any]) -> None:
        """Plot generic frame for unknown animation types."""
        try:
            # Try to plot any available data
            if 'center' in frame:
                center = frame['center']
                ax.plot(center[1], center[0], 'ro', markersize=10)
            
            if 'boundary' in frame:
                boundary = frame['boundary']
                boundary_coords = np.array(boundary)
                ax.plot(boundary_coords[:, 1], boundary_coords[:, 0], 'b-', linewidth=2)
                
        except Exception as e:
            print(f"⚠️ Error plotting generic frame: {e}")
    
    def _set_frame_labels(self, ax, frame: Dict[str, Any], animation_data: Dict[str, Any], animation_type: str) -> None:
        """Set consistent labels and title for frame."""
        try:
            if animation_type == 'resolution_transition':
                location = animation_data['location']
                resolution = frame['resolution']
                area = frame['area_km2']
                title = f'H3 Resolution Transition - {location.title()}\nResolution: {resolution}, Area: {area:.2f} km²'
                
            elif animation_type == 'grid_expansion':
                location = animation_data['location']
                radius = frame['radius']
                cells = frame['cells']
                total_area = frame['total_area_km2']
                title = f'H3 Grid Expansion - {location.title()}\nRadius: {radius}, Cells: {len(cells)}, Area: {total_area:.2f} km²'
                
            elif animation_type == 'path_finding':
                start_location = animation_data['start_location']
                end_location = animation_data['end_location']
                progress = frame.get('path_progress', 0)
                title = f'H3 Path Finding - {start_location.title()} to {end_location.title()}\nProgress: {progress:.1%}'
                
            elif animation_type == 'hierarchy':
                location = animation_data['location']
                hierarchy_type = frame.get('hierarchy_type', 'parent')
                if hierarchy_type == 'parent':
                    area = frame['area_km2']
                    title = f'H3 Hierarchy - {location.title()} (Parent)\nArea: {area:.2f} km²'
                else:
                    cells = frame['cells']
                    areas = frame['areas_km2']
                    title = f'H3 Hierarchy - {location.title()} (Children)\nCells: {len(cells)}, Total Area: {sum(areas):.2f} km²'
                    
            elif animation_type == 'spatial_distribution':
                location = animation_data['location']
                pattern_type = frame['pattern']
                cells = frame['cells']
                areas = frame['areas_km2']
                title = f'H3 Spatial Distribution - {location.title()} ({pattern_type.title()})\nCells: {len(cells)}, Total Area: {sum(areas):.2f} km²'
                
            else:
                title = f'H3 Animation - {animation_type.title()}'
            
            ax.set_title(title, fontsize=12, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)
            
        except Exception as e:
            print(f"⚠️ Error setting frame labels: {e}")
            ax.set_title(f'H3 Animation - {animation_type.title()}', fontsize=12, fontweight='bold')
            ax.set_xlabel('Longitude', fontsize=10)
            ax.set_ylabel('Latitude', fontsize=10)
    
    def _normalize_frame_sizes(self, frame_files: List[str]) -> None:
        """Ensure all frames have the same size."""
        if not frame_files:
            return
        
        try:
            # Read first frame to get target size
            first_image = Image.open(frame_files[0])
            target_size = first_image.size
            first_image.close()
            
            # Resize all frames to match first frame
            for frame_file in frame_files:
                try:
                    img = Image.open(frame_file)
                    if img.size != target_size:
                        img = img.resize(target_size, Image.Resampling.LANCZOS)
                        img.save(frame_file)
                    img.close()
                except Exception as e:
                    print(f"⚠️ Warning: Could not normalize frame {frame_file}: {e}")
                    
        except Exception as e:
            print(f"⚠️ Warning: Could not normalize frame sizes: {e}")
    
    def generate_all_gifs(self) -> None:
        """Generate GIF animations for all available JSON files."""
        print("🎬 Generating H3 Animation GIFs (Robust Method)...")
        
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
                
                # Generate GIF
                gif_filename = json_file.stem + '.gif'
                self.create_robust_gif(animation_data, gif_filename)
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
    
    generator = RobustH3GIFGenerator(input_dir, output_dir)
    generator.generate_all_gifs()


if __name__ == '__main__':
    main() 