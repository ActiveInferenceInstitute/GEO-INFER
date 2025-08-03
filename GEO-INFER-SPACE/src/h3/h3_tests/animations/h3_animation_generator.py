#!/usr/bin/env python3
"""
H3 Animation Generator

Generates comprehensive H3-based animations using real H3 methods.
Creates resolution transitions, grid expansions, path animations,
and hierarchical animations with full geometric data.

Author: GEO-INFER Framework
Version: 4.3.0
License: Apache-2.0
"""

import json
import math
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import h3


class H3AnimationGenerator:
    """
    Comprehensive H3 animation generator using real H3 methods.
    
    Generates various types of H3 animations including:
    - Resolution transitions (zooming in/out)
    - Grid expansion animations
    - Path finding animations
    - Hierarchical animations
    - Spatial distribution animations
    """
    
    def __init__(self, output_dir: Path):
        """Initialize the animation generator."""
        self.output_dir = output_dir / "animations"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Base locations for animations
        self.locations = {
            'san_francisco': {'lat': 37.7749, 'lng': -122.4194},
            'new_york': {'lat': 40.7128, 'lng': -74.0060},
            'los_angeles': {'lat': 34.0522, 'lng': -118.2437},
            'chicago': {'lat': 41.8781, 'lng': -87.6298},
            'miami': {'lat': 25.7617, 'lng': -80.1918}
        }
        
        # Animation limits for testing
        self.max_frames = 100
        self.max_path_length = 50
    
    def _limit_frames(self, frames: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Limit the number of frames to prevent excessive animation size."""
        if len(frames) <= self.max_frames:
            return frames
        
        # Sample frames to keep animation reasonable
        step = len(frames) // self.max_frames
        limited_frames = frames[::step]
        
        # Always include the last frame
        if limited_frames[-1] != frames[-1]:
            limited_frames.append(frames[-1])
        
        return limited_frames
    
    def generate_resolution_animation(self, location: str, start_res: int = 5, end_res: int = 12) -> Dict[str, Any]:
        """
        Generate resolution transition animation (zoom in/out effect).
        
        Args:
            location: Location name from self.locations
            start_res: Starting resolution
            end_res: Ending resolution
            
        Returns:
            Animation data with frames showing resolution transitions
        """
        coords = self.locations[location]
        frames = []
        
        for res in range(start_res, end_res + 1):
            cell = h3.latlng_to_cell(coords['lat'], coords['lng'], res)
            center = h3.cell_to_latlng(cell)
            boundary = h3.cell_to_boundary(cell)
            area = h3.cell_area(cell, unit='km^2')
            edge_length = h3.average_hexagon_edge_length(res, unit='km')
            
            # Get neighbors for context
            neighbors = h3.grid_disk(cell, 1)
            
            frame = {
                'frame': len(frames),
                'resolution': res,
                'cell': cell,
                'center': list(center),
                'area_km2': area,
                'edge_length_km': edge_length,
                'boundary': [list(point) for point in boundary],
                'neighbors': neighbors,
                'neighbor_count': len(neighbors),
                'is_pentagon': h3.is_pentagon(cell),
                'is_res_class_iii': h3.is_res_class_III(cell),
                'base_cell_number': h3.get_base_cell_number(cell),
                'icosahedron_faces': list(h3.get_icosahedron_faces(cell))
            }
            frames.append(frame)
        
        return {
            'animation_type': 'resolution_transition',
            'location': location,
            'coordinates': coords,
            'start_resolution': start_res,
            'end_resolution': end_res,
            'total_frames': len(frames),
            'frames': frames,
            'metadata': {
                'description': f'Resolution transition from {start_res} to {end_res}',
                'location': location,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def generate_grid_expansion_animation(self, location: str, resolution: int = 9, max_radius: int = 5) -> Dict[str, Any]:
        """
        Generate grid expansion animation (growing disk effect).
        
        Args:
            location: Location name from self.locations
            resolution: H3 resolution to use
            max_radius: Maximum expansion radius
            
        Returns:
            Animation data with frames showing grid expansion
        """
        coords = self.locations[location]
        base_cell = h3.latlng_to_cell(coords['lat'], coords['lng'], resolution)
        frames = []
        
        for radius in range(max_radius + 1):
            # Get cells at this radius
            if radius == 0:
                cells = [base_cell]
            else:
                cells = h3.grid_ring(base_cell, radius)
            
            # Calculate properties for all cells
            total_area = sum(h3.cell_area(cell, unit='km^2') for cell in cells)
            avg_edge_length = h3.average_hexagon_edge_length(resolution, unit='km')
            
            # Get boundary of all cells
            all_boundaries = []
            for cell in cells:
                boundary = h3.cell_to_boundary(cell)
                all_boundaries.extend([list(point) for point in boundary])
            
            frame = {
                'frame': len(frames),
                'radius': radius,
                'cell_count': len(cells),
                'cells': cells,
                'total_area_km2': total_area,
                'avg_edge_length_km': avg_edge_length,
                'boundaries': all_boundaries,
                'base_cell': base_cell,
                'base_cell_center': list(h3.cell_to_latlng(base_cell))
            }
            frames.append(frame)
        
        return {
            'animation_type': 'grid_expansion',
            'location': location,
            'coordinates': coords,
            'resolution': resolution,
            'max_radius': max_radius,
            'total_frames': len(frames),
            'frames': frames,
            'metadata': {
                'description': f'Grid expansion animation with radius 0 to {max_radius}',
                'location': location,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def generate_path_animation(self, start_location: str, end_location: str, resolution: int = 9) -> Dict[str, Any]:
        """
        Generate path finding animation between two locations.
        
        Args:
            start_location: Starting location name
            end_location: Ending location name
            resolution: H3 resolution to use
            
        Returns:
            Animation data with frames showing path progression
        """
        start_coords = self.locations[start_location]
        end_coords = self.locations[end_location]
        
        start_cell = h3.latlng_to_cell(start_coords['lat'], start_coords['lng'], resolution)
        end_cell = h3.latlng_to_cell(end_coords['lat'], end_coords['lng'], resolution)
        
        # Get path between cells with reasonable limits
        try:
            path_cells = h3.grid_path_cells(start_cell, end_cell)
            # Limit path length to prevent excessive frames
            if len(path_cells) > self.max_path_length:
                # Sample the path to keep it reasonable
                step = len(path_cells) // self.max_path_length
                path_cells = path_cells[::step] + [path_cells[-1]]
        except Exception:
            # If path finding fails, create a simple path using grid_disk
            path_cells = [start_cell]
            # Add some intermediate cells for visualization
            intermediate_cells = h3.grid_disk(start_cell, 2)
            path_cells.extend(intermediate_cells[:5])  # Take first 5 cells
            path_cells.append(end_cell)
        
        frames = []
        
        for i, cell in enumerate(path_cells):
            center = h3.cell_to_latlng(cell)
            boundary = h3.cell_to_boundary(cell)
            area = h3.cell_area(cell, unit='km^2')
            
            # Calculate progress along path
            progress = i / (len(path_cells) - 1) if len(path_cells) > 1 else 0
            
            frame = {
                'frame': len(frames),
                'cell': cell,
                'center': list(center),
                'area_km2': area,
                'boundary': [list(point) for point in boundary],
                'path_progress': progress,
                'distance_from_start': i,
                'distance_to_end': len(path_cells) - i - 1,
                'is_pentagon': h3.is_pentagon(cell),
                'is_res_class_iii': h3.is_res_class_III(cell)
            }
            frames.append(frame)
        
        # Safety check: limit total frames to prevent excessive animation size
        frames = self._limit_frames(frames)
        
        return {
            'animation_type': 'path_finding',
            'start_location': start_location,
            'end_location': end_location,
            'start_coordinates': start_coords,
            'end_coordinates': end_coords,
            'resolution': resolution,
            'total_frames': len(frames),
            'frames': frames,
            'path_length': len(path_cells),
            'metadata': {
                'description': f'Path animation from {start_location} to {end_location}',
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def generate_hierarchy_animation(self, location: str, base_resolution: int = 9, levels: int = 3) -> Dict[str, Any]:
        """
        Generate hierarchical animation showing parent-child relationships.
        
        Args:
            location: Location name from self.locations
            base_resolution: Base resolution to start from
            levels: Number of hierarchy levels to show
            
        Returns:
            Animation data with frames showing hierarchy levels
        """
        coords = self.locations[location]
        base_cell = h3.latlng_to_cell(coords['lat'], coords['lng'], base_resolution)
        frames = []
        
        for level in range(levels):
            # Get cells at different resolutions
            parent_res = base_resolution - level
            child_res = base_resolution + level
            
            if parent_res >= 0:
                parent_cell = h3.cell_to_parent(base_cell, parent_res)
                parent_center = h3.cell_to_latlng(parent_cell)
                parent_area = h3.cell_area(parent_cell, unit='km^2')
                parent_boundary = h3.cell_to_boundary(parent_cell)
                
                parent_frame = {
                    'frame': len(frames),
                    'level': level,
                    'resolution': parent_res,
                    'cell': parent_cell,
                    'center': list(parent_center),
                    'area_km2': parent_area,
                    'boundary': [list(point) for point in parent_boundary],
                    'hierarchy_type': 'parent',
                    'is_pentagon': h3.is_pentagon(parent_cell)
                }
                frames.append(parent_frame)
            
            if child_res <= 15:
                child_cells = h3.cell_to_children(base_cell, child_res)
                child_centers = [h3.cell_to_latlng(cell) for cell in child_cells]
                child_areas = [h3.cell_area(cell, unit='km^2') for cell in child_cells]
                child_boundaries = [h3.cell_to_boundary(cell) for cell in child_cells]
                
                child_frame = {
                    'frame': len(frames),
                    'level': level,
                    'resolution': child_res,
                    'cells': child_cells,
                    'centers': [list(center) for center in child_centers],
                    'areas_km2': child_areas,
                    'boundaries': [[list(point) for point in boundary] for boundary in child_boundaries],
                    'hierarchy_type': 'children',
                    'child_count': len(child_cells),
                    'total_area_km2': sum(child_areas)
                }
                frames.append(child_frame)
        
        return {
            'animation_type': 'hierarchy',
            'location': location,
            'coordinates': coords,
            'base_resolution': base_resolution,
            'levels': levels,
            'total_frames': len(frames),
            'frames': frames,
            'metadata': {
                'description': f'Hierarchy animation with {levels} levels',
                'location': location,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def generate_spatial_distribution_animation(self, location: str, resolution: int = 9, pattern: str = 'spiral') -> Dict[str, Any]:
        """
        Generate spatial distribution animation with different patterns.
        
        Args:
            location: Location name from self.locations
            resolution: H3 resolution to use
            pattern: Distribution pattern ('spiral', 'random', 'grid')
            
        Returns:
            Animation data with frames showing spatial distribution
        """
        coords = self.locations[location]
        base_cell = h3.latlng_to_cell(coords['lat'], coords['lng'], resolution)
        frames = []
        
        if pattern == 'spiral':
            # Create spiral pattern
            max_radius = 8
            for radius in range(max_radius + 1):
                cells = h3.grid_disk(base_cell, radius)
                frame = self._create_distribution_frame(cells, radius, 'spiral')
                frames.append(frame)
        
        elif pattern == 'random':
            # Create random distribution
            all_cells = h3.grid_disk(base_cell, 5)
            np.random.shuffle(all_cells)
            
            batch_size = max(1, len(all_cells) // 10)
            for i in range(0, len(all_cells), batch_size):
                batch = all_cells[i:i + batch_size]
                frame = self._create_distribution_frame(batch, i // batch_size, 'random')
                frames.append(frame)
        
        elif pattern == 'grid':
            # Create grid pattern
            for radius in range(0, 6, 2):
                cells = h3.grid_ring(base_cell, radius)
                frame = self._create_distribution_frame(cells, radius, 'grid')
                frames.append(frame)
        
        # Limit frames to prevent excessive animation size
        frames = self._limit_frames(frames)
        
        return {
            'animation_type': 'spatial_distribution',
            'location': location,
            'coordinates': coords,
            'resolution': resolution,
            'pattern': pattern,
            'total_frames': len(frames),
            'frames': frames,
            'metadata': {
                'description': f'Spatial distribution animation with {pattern} pattern',
                'location': location,
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def _create_distribution_frame(self, cells: List[str], frame_index: int, pattern: str) -> Dict[str, Any]:
        """Create a distribution frame with cell properties."""
        if not cells:
            return {
                'frame': frame_index,
                'cells': [],
                'centers': [],
                'areas_km2': [],
                'boundaries': [],
                'pattern': pattern,
                'cell_count': 0,
                'total_area_km2': 0.0
            }
        
        centers = [h3.cell_to_latlng(cell) for cell in cells]
        areas = [h3.cell_area(cell, unit='km^2') for cell in cells]
        boundaries = [h3.cell_to_boundary(cell) for cell in cells]
        
        return {
            'frame': frame_index,
            'cells': cells,
            'centers': [list(center) for center in centers],
            'areas_km2': areas,
            'boundaries': [[list(point) for point in boundary] for boundary in boundaries],
            'pattern': pattern,
            'cell_count': len(cells),
            'total_area_km2': sum(areas),
            'avg_area_km2': sum(areas) / len(cells) if cells else 0.0
        }
    
    def generate_comprehensive_animation_suite(self) -> Dict[str, Any]:
        """
        Generate a comprehensive suite of all animation types.
        
        Returns:
            Complete animation suite with all animation types
        """
        animations = {}
        
        # Generate resolution animations for all locations
        for location in self.locations:
            animations[f'resolution_{location}'] = self.generate_resolution_animation(location)
        
        # Generate grid expansion animations
        for location in ['san_francisco', 'new_york']:
            animations[f'grid_expansion_{location}'] = self.generate_grid_expansion_animation(location)
        
        # Generate path animations between major cities
        path_pairs = [
            ('san_francisco', 'new_york'),
            ('los_angeles', 'chicago'),
            ('miami', 'san_francisco')
        ]
        
        for start, end in path_pairs:
            animations[f'path_{start}_to_{end}'] = self.generate_path_animation(start, end)
        
        # Generate hierarchy animations
        for location in ['san_francisco', 'new_york']:
            animations[f'hierarchy_{location}'] = self.generate_hierarchy_animation(location)
        
        # Generate spatial distribution animations
        patterns = ['spiral', 'random', 'grid']
        for pattern in patterns:
            animations[f'spatial_distribution_{pattern}'] = self.generate_spatial_distribution_animation('san_francisco', pattern=pattern)
        
        return {
            'animation_suite': animations,
            'total_animations': len(animations),
            'animation_types': list(set(anim['animation_type'] for anim in animations.values())),
            'locations_used': list(self.locations.keys()),
            'metadata': {
                'description': 'Comprehensive H3 animation suite',
                'generated_at': datetime.now().isoformat(),
                'total_frames': sum(anim['total_frames'] for anim in animations.values())
            }
        }
    
    def save_animation_data(self, animation_data: Dict[str, Any], filename: str) -> None:
        """Save animation data to JSON file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(animation_data, f, indent=2)
    
    def generate_all_animations(self) -> None:
        """Generate all animation types and save them."""
        print("Generating comprehensive H3 animation suite...")
        
        # Generate individual animations
        for location in self.locations:
            # Resolution animation
            res_anim = self.generate_resolution_animation(location)
            self.save_animation_data(res_anim, f'resolution_animation_{location}.json')
            
            # Grid expansion animation
            grid_anim = self.generate_grid_expansion_animation(location)
            self.save_animation_data(grid_anim, f'grid_expansion_{location}.json')
            
            # Hierarchy animation
            hierarchy_anim = self.generate_hierarchy_animation(location)
            self.save_animation_data(hierarchy_anim, f'hierarchy_{location}.json')
        
        # Generate path animations
        path_pairs = [
            ('san_francisco', 'new_york'),
            ('los_angeles', 'chicago'),
            ('miami', 'san_francisco'),
            ('new_york', 'chicago'),
            ('chicago', 'miami')
        ]
        
        for start, end in path_pairs:
            path_anim = self.generate_path_animation(start, end)
            self.save_animation_data(path_anim, f'path_{start}_to_{end}.json')
        
        # Generate spatial distribution animations
        for pattern in ['spiral', 'random', 'grid']:
            spatial_anim = self.generate_spatial_distribution_animation('san_francisco', pattern=pattern)
            self.save_animation_data(spatial_anim, f'spatial_distribution_{pattern}.json')
        
        # Generate comprehensive suite
        suite = self.generate_comprehensive_animation_suite()
        self.save_animation_data(suite, 'comprehensive_animation_suite.json')
        
        # Generate summary
        self._generate_animation_summary()
        
        print(f"Generated {len(suite['animation_suite'])} animations with {suite['metadata']['total_frames']} total frames")
    
    def _generate_animation_summary(self) -> None:
        """Generate a summary of all animations."""
        summary = {
            'animation_types': {
                'resolution_transition': 'Zoom in/out between resolutions',
                'grid_expansion': 'Growing disk expansion',
                'path_finding': 'Path between two locations',
                'hierarchy': 'Parent-child relationships',
                'spatial_distribution': 'Spatial pattern distribution'
            },
            'locations': list(self.locations.keys()),
            'total_animations_generated': 0,
            'total_frames_generated': 0,
            'generated_at': datetime.now().isoformat()
        }
        
        # Count files and frames
        json_files = list(self.output_dir.glob('*.json'))
        summary['total_animations_generated'] = len(json_files)
        
        # Calculate total frames
        total_frames = 0
        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    if 'total_frames' in data:
                        total_frames += data['total_frames']
                    elif 'frames' in data:
                        total_frames += len(data['frames'])
            except:
                pass
        
        summary['total_frames_generated'] = total_frames
        
        # Save summary
        summary_file = self.output_dir / 'animation_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate markdown summary
        md_summary = f"""# H3 Animation Suite Summary

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Animation Types
- **Resolution Transitions**: {len([f for f in json_files if 'resolution' in f.name])} animations
- **Grid Expansions**: {len([f for f in json_files if 'grid_expansion' in f.name])} animations  
- **Path Finding**: {len([f for f in json_files if 'path' in f.name])} animations
- **Hierarchy**: {len([f for f in json_files if 'hierarchy' in f.name])} animations
- **Spatial Distribution**: {len([f for f in json_files if 'spatial_distribution' in f.name])} animations

## Statistics
- **Total Animations**: {summary['total_animations_generated']}
- **Total Frames**: {summary['total_frames_generated']}
- **Locations**: {', '.join(summary['locations'])}

## Files Generated
{chr(10).join([f'- {f.name}' for f in json_files])}
"""
        
        md_file = self.output_dir / 'animation_summary.md'
        with open(md_file, 'w') as f:
            f.write(md_summary)


def main():
    """Main function to generate all animations."""
    output_dir = Path('outputs/animations')
    generator = H3AnimationGenerator(output_dir)
    generator.generate_all_animations()


if __name__ == '__main__':
    main() 