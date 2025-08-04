#!/usr/bin/env python3
"""
Comprehensive H3 Workflow Example

Demonstrates a complete H3 analysis pipeline using all tested methods.
Shows end-to-end workflow from data input to visualization output.

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

# Import from our local H3 framework
from core import (
    latlng_to_cell, cell_to_latlng, cell_to_boundary, cell_area,
    get_resolution, is_valid_cell, is_pentagon
)

from indexing import (
    cell_to_center_child, cell_to_children, cell_to_parent
)

from traversal import (
    grid_disk, grid_ring, grid_path_cells, grid_distance,
    great_circle_distance, grid_neighbors
)

from hierarchy import (
    get_hierarchy_path, get_ancestors, get_descendants
)

from conversion import (
    cells_to_geojson, cells_to_csv, cells_to_shapefile_data, cells_to_kml, cells_to_wkt
)

from analysis import (
    analyze_cell_distribution, calculate_spatial_statistics,
    find_nearest_cell, calculate_cell_density, analyze_resolution_distribution
)


def ensure_output_dir():
    """Ensure the output directory exists."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    return output_dir


class H3Workflow:
    """Complete H3 analysis workflow."""
    
    def __init__(self):
        """Initialize the workflow."""
        self.results = {}
        self.start_time = time.time()
        self.output_dir = ensure_output_dir()
        
    def step_1_data_ingestion(self):
        """Step 1: Data ingestion and validation."""
        print("🔹 Step 1: Data Ingestion and Validation")
        print("-" * 50)
        
        # Define input data
        self.input_data = {
            'locations': [
                {"name": "San Francisco", "lat": 37.7749, "lng": -122.4194, "population": 873965},
                {"name": "New York", "lat": 40.7128, "lng": -74.0060, "population": 8336817},
                {"name": "Los Angeles", "lat": 34.0522, "lng": -118.2437, "population": 3979576},
                {"name": "Chicago", "lat": 41.8781, "lng": -87.6298, "population": 2693976},
                {"name": "Miami", "lat": 25.7617, "lng": -80.1918, "population": 454279}
            ],
            'analysis_resolution': 9,
            'coverage_radius': 3
        }
        
        # Validate and convert to H3 cells
        self.cells = {}
        for location in self.input_data['locations']:
            cell = latlng_to_cell(location['lat'], location['lng'], self.input_data['analysis_resolution'])
            
            # Validate cell
            if not is_valid_cell(cell):
                raise ValueError(f"Invalid cell generated for {location['name']}")
            
            self.cells[location['name']] = {
                'cell': cell,
                'coordinates': (location['lat'], location['lng']),
                'population': location['population'],
                'area': cell_area(cell, 'km^2')
            }
            
            print(f"  {location['name']}: {cell} ({location['lat']:.4f}, {location['lng']:.4f})")
        
        self.results['step_1'] = {
            'status': 'completed',
            'cells_processed': len(self.cells),
            'validation_passed': True
        }
        
        print(f"  ✅ Validated {len(self.cells)} locations")
        
        # Save step 1 data
        step1_data = {
            "input_data": self.input_data,
            "cells": self.cells,
            "results": self.results['step_1']
        }
        
        output_file = self.output_dir / "06_step1_data_ingestion.json"
        with open(output_file, 'w') as f:
            json.dump(step1_data, f, indent=2)
        print(f"✅ Saved step 1 data to {output_file}")
    
    def step_2_spatial_analysis(self):
        """Step 2: Spatial analysis and statistics."""
        print("\n🔹 Step 2: Spatial Analysis and Statistics")
        print("-" * 50)
        
        # Collect all cells for analysis
        all_cells = [data['cell'] for data in self.cells.values()]
        
        # Analyze cell distribution
        distribution = analyze_cell_distribution(all_cells)
        print(f"  Distribution Analysis:")
        print(f"    Total cells: {distribution['total_cells']}")
        print(f"    Total area: {distribution['total_area_km2']:.6f} km²")
        print(f"    Average area: {distribution['avg_area_km2']:.6f} km²")
        print(f"    Pentagons: {distribution['pentagons']}")
        print(f"    Class III cells: {distribution['class_iii_cells']}")
        
        # Calculate spatial statistics
        stats = calculate_spatial_statistics(all_cells)
        print(f"  Spatial Statistics:")
        print(f"    Centroid: {stats['centroid']}")
        print(f"    Compactness: {stats['compactness']:.4f}")
        
        # Analyze resolution distribution
        res_analysis = analyze_resolution_distribution(all_cells)
        print(f"  Resolution Analysis:")
        print(f"    Min resolution: {res_analysis['min_resolution']}")
        print(f"    Max resolution: {res_analysis['max_resolution']}")
        print(f"    Average resolution: {res_analysis['avg_resolution']:.2f}")
        
        self.results['step_2'] = {
            'status': 'completed',
            'distribution': distribution,
            'statistics': stats,
            'resolution_analysis': res_analysis
        }
        
        # Save step 2 data
        step2_data = {
            "all_cells": all_cells,
            "distribution": distribution,
            "statistics": stats,
            "resolution_analysis": res_analysis,
            "results": self.results['step_2']
        }
        
        output_file = self.output_dir / "06_step2_spatial_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(step2_data, f, indent=2)
        print(f"✅ Saved step 2 data to {output_file}")
    
    def step_3_hierarchical_analysis(self):
        """Step 3: Hierarchical analysis and relationships."""
        print("\n🔹 Step 3: Hierarchical Analysis and Relationships")
        print("-" * 50)
        
        # Analyze parent-child relationships
        sf_cell = self.cells['San Francisco']['cell']
        
        # Get hierarchy path
        hierarchy_path = get_hierarchy_path(sf_cell, 6)
        print(f"  Hierarchy Path (SF to Res 6):")
        for i, cell in enumerate(hierarchy_path):
            res = get_resolution(cell)
            area = cell_area(cell, 'km^2')
            print(f"    Res {res}: {cell} - {area:.6f} km²")
        
        # Get ancestors and descendants
        ancestors = get_ancestors(sf_cell, 3)
        descendants = get_descendants(sf_cell, 5)
        
        print(f"  Ancestors: {len(ancestors)} cells")
        print(f"  Descendants: {len(descendants)} cells")
        
        self.results['step_3'] = {
            'status': 'completed',
            'hierarchy_path_length': len(hierarchy_path),
            'ancestors_count': len(ancestors),
            'descendants_count': len(descendants)
        }
        
        # Save step 3 data
        step3_data = {
            "sf_cell": sf_cell,
            "hierarchy_path": hierarchy_path,
            "ancestors": ancestors,
            "descendants": descendants,
            "results": self.results['step_3']
        }
        
        output_file = self.output_dir / "06_step3_hierarchical_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(step3_data, f, indent=2)
        print(f"✅ Saved step 3 data to {output_file}")
    
    def step_4_grid_operations(self):
        """Step 4: Grid operations and spatial relationships."""
        print("\n🔹 Step 4: Grid Operations and Spatial Relationships")
        print("-" * 50)
        
        # Analyze grid operations for each location
        grid_analysis = {}
        
        for name, data in self.cells.items():
            cell = data['cell']
            
            # Grid disk analysis
            disk_cells = grid_disk(cell, self.input_data['coverage_radius'])
            disk_area = sum(cell_area(c, 'km^2') for c in disk_cells)
            
            # Grid ring analysis
            ring_cells = grid_ring(cell, 1)
            
            # Neighbor analysis
            neighbors = grid_neighbors(cell)
            
            grid_analysis[name] = {
                'disk_cells': len(disk_cells),
                'disk_area': disk_area,
                'ring_cells': len(ring_cells),
                'neighbors': len(neighbors)
            }
            
            print(f"  {name}:")
            print(f"    Disk (r={self.input_data['coverage_radius']}): {len(disk_cells)} cells, {disk_area:.6f} km²")
            print(f"    Ring (r=1): {len(ring_cells)} cells")
            print(f"    Neighbors: {len(neighbors)} cells")
        
        # Calculate distances between all pairs
        print(f"  Distance Analysis:")
        locations = list(self.cells.keys())
        distance_analysis = []
        for i, loc1 in enumerate(locations):
            for j, loc2 in enumerate(locations[i+1:], i+1):
                cell1 = self.cells[loc1]['cell']
                cell2 = self.cells[loc2]['cell']
                
                # Great circle distance
                lat1, lng1 = self.cells[loc1]['coordinates']
                lat2, lng2 = self.cells[loc2]['coordinates']
                gc_distance = great_circle_distance(lat1, lng1, lat2, lng2, 'km')
                
                # Grid distance
                try:
                    grid_dist = grid_distance(cell1, cell2)
                except Exception:
                    grid_dist = None
                
                print(f"    {loc1} -> {loc2}: {gc_distance:.1f} km (grid: {grid_dist if grid_dist is not None else 'too far'})")
                
                distance_analysis.append({
                    "from": loc1,
                    "to": loc2,
                    "cell1": cell1,
                    "cell2": cell2,
                    "great_circle_distance_km": gc_distance,
                    "grid_distance": grid_dist
                })
        
        self.results['step_4'] = {
            'status': 'completed',
            'grid_analysis': grid_analysis,
            'distance_analysis': distance_analysis
        }
        
        # Save step 4 data
        step4_data = {
            "grid_analysis": grid_analysis,
            "distance_analysis": distance_analysis,
            "results": self.results['step_4']
        }
        
        output_file = self.output_dir / "06_step4_grid_operations.json"
        with open(output_file, 'w') as f:
            json.dump(step4_data, f, indent=2)
        print(f"✅ Saved step 4 data to {output_file}")
    
    def step_5_data_conversion(self):
        """Step 5: Data conversion and export."""
        print("\n🔹 Step 5: Data Conversion and Export")
        print("-" * 50)
        
        # Collect all cells for conversion
        all_cells = [data['cell'] for data in self.cells.values()]
        
        # Convert to different formats
        conversions = {}
        
        # 1. GeoJSON
        geojson_output = cells_to_geojson(all_cells)
        conversions['geojson'] = {
            'type': 'FeatureCollection',
            'features_count': len(geojson_output['features']),
            'size': len(json.dumps(geojson_output))
        }
        
        # 2. CSV
        csv_output = cells_to_csv(all_cells)
        conversions['csv'] = {
            'lines': len(csv_output.splitlines()),
            'size': len(csv_output)
        }
        
        # 3. KML
        kml_output = cells_to_kml(all_cells)
        conversions['kml'] = {
            'size': len(kml_output)
        }
        
        # 4. Shapefile data
        shapefile_data = cells_to_shapefile_data(all_cells)
        conversions['shapefile'] = {
            'geometries': len(shapefile_data['geometries']),
            'properties': len(shapefile_data['properties'])
        }
        
        # 5. WKT
        wkt_output = cells_to_wkt(all_cells)
        conversions['wkt'] = {
            'size': len(wkt_output)
        }
        
        print(f"  Conversion Results:")
        for format_name, data in conversions.items():
            print(f"    {format_name.upper()}: {data}")
        
        self.results['step_5'] = {
            'status': 'completed',
            'conversions': conversions
        }
        
        # Save step 5 data
        step5_data = {
            "all_cells": all_cells,
            "conversions": conversions,
            "geojson_output": geojson_output,
            "csv_output": csv_output,
            "kml_output": kml_output,
            "shapefile_data": shapefile_data,
            "wkt_output": wkt_output,
            "results": self.results['step_5']
        }
        
        output_file = self.output_dir / "06_step5_data_conversion.json"
        with open(output_file, 'w') as f:
            json.dump(step5_data, f, indent=2)
        print(f"✅ Saved step 5 data to {output_file}")
        
        # Also save the actual files
        geojson_file = self.output_dir / "06_workflow_cells.geojson"
        with open(geojson_file, 'w') as f:
            json.dump(geojson_output, f, indent=2)
        print(f"✅ Saved workflow GeoJSON to {geojson_file}")
        
        csv_file = self.output_dir / "06_workflow_cells.csv"
        with open(csv_file, 'w') as f:
            f.write(csv_output)
        print(f"✅ Saved workflow CSV to {csv_file}")
    
    def step_6_advanced_analysis(self):
        """Step 6: Advanced analysis and multi-resolution operations."""
        print("\n🔹 Step 6: Advanced Analysis and Multi-Resolution Operations")
        print("-" * 50)
        
        # Multi-resolution analysis
        sf_coords = self.cells['San Francisco']['coordinates']
        multi_res_analysis = {}
        
        for resolution in [6, 8, 10, 12]:
            cell = latlng_to_cell(sf_coords[0], sf_coords[1], resolution)
            area = cell_area(cell, 'km^2')
            
            # Get children and parent
            if resolution < 12:
                children = cell_to_children(cell, resolution + 1)
                children_count = len(children)
            else:
                children_count = 0
            
            if resolution > 6:
                parent = cell_to_parent(cell, resolution - 1)
                parent_area = cell_area(parent, 'km^2')
            else:
                parent_area = 0
            
            multi_res_analysis[resolution] = {
                'cell': cell,
                'area': area,
                'children_count': children_count,
                'parent_area': parent_area
            }
            
            print(f"  Resolution {resolution}:")
            print(f"    Cell: {cell}")
            print(f"    Area: {area:.6f} km²")
            print(f"    Children: {children_count}")
            print(f"    Parent area: {parent_area:.6f} km²")
        
        # Density analysis
        density_analysis = {}
        for name, data in self.cells.items():
            cell = data['cell']
            disk_cells = grid_disk(cell, 2)
            density = calculate_cell_density(disk_cells)
            
            density_analysis[name] = {
                'density': density,
                'coverage_cells': len(disk_cells)
            }
            
            print(f"  {name} density: {density:.2f} cells/km²")
        
        # Nearest neighbor analysis
        reference_cells = [data['cell'] for data in self.cells.values()]
        test_points = [
            (37.7849, -122.4094),  # Near SF
            (40.7228, -73.9960),   # Near NY
            (39.7392, -104.9903),  # Denver (far)
        ]
        
        nearest_analysis = []
        for i, (lat, lng) in enumerate(test_points):
            nearest_cell, distance = find_nearest_cell(lat, lng, reference_cells)
            nearest_lat, nearest_lng = cell_to_latlng(nearest_cell)
            
            nearest_analysis.append({
                'test_point': (lat, lng),
                'nearest_cell': nearest_cell,
                'nearest_coordinates': (nearest_lat, nearest_lng),
                'distance': distance
            })
            
            print(f"  Test point {i+1} ({lat:.4f}, {lng:.4f}):")
            print(f"    Nearest: {nearest_cell} ({nearest_lat:.4f}, {nearest_lng:.4f})")
            print(f"    Distance: {distance:.6f} km")
        
        self.results['step_6'] = {
            'status': 'completed',
            'multi_res_analysis': multi_res_analysis,
            'density_analysis': density_analysis,
            'nearest_analysis': nearest_analysis
        }
        
        # Save step 6 data
        step6_data = {
            "multi_res_analysis": multi_res_analysis,
            "density_analysis": density_analysis,
            "nearest_analysis": nearest_analysis,
            "results": self.results['step_6']
        }
        
        output_file = self.output_dir / "06_step6_advanced_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(step6_data, f, indent=2)
        print(f"✅ Saved step 6 data to {output_file}")
    
    def step_7_visualization_preparation(self):
        """Step 7: Visualization preparation and output generation."""
        print("\n🔹 Step 7: Visualization Preparation and Output Generation")
        print("-" * 50)
        
        # Prepare visualization data
        viz_data = {
            'static': {},
            'animated': {},
            'interactive': {}
        }
        
        # Static visualization data
        for name, data in self.cells.items():
            cell = data['cell']
            disk_cells = grid_disk(cell, 2)
            
            viz_data['static'][name] = {
                'center_cell': cell,
                'coverage_cells': disk_cells,
                'geojson': cells_to_geojson(disk_cells),
                'statistics': {
                    'cell_count': len(disk_cells),
                    'total_area': sum(cell_area(c, 'km^2') for c in disk_cells),
                    'population': data['population']
                }
            }
        
        # Animated visualization data
        sf_cell = self.cells['San Francisco']['cell']
        animation_frames = []
        
        for k in range(0, 4):
            frame_cells = grid_disk(sf_cell, k)
            frame_data = {
                'frame': k,
                'cells': frame_cells,
                'geojson': cells_to_geojson(frame_cells),
                'statistics': {
                    'cell_count': len(frame_cells),
                    'total_area': sum(cell_area(c, 'km^2') for c in frame_cells)
                }
            }
            animation_frames.append(frame_data)
        
        viz_data['animated']['grid_expansion'] = animation_frames
        
        # Interactive visualization data
        interactive_features = []
        for name, data in self.cells.items():
            cell = data['cell']
            geojson = cells_to_geojson([cell])
            feature = geojson['features'][0]
            
            # Add interactive properties
            feature['properties'].update({
                'city': name,
                'population': data['population'],
                'area': data['area'],
                'clickable': True
            })
            
            interactive_features.append(feature)
        
        viz_data['interactive']['cities'] = {
            'type': 'FeatureCollection',
            'features': interactive_features
        }
        
        print(f"  Visualization Data Prepared:")
        print(f"    Static visualizations: {len(viz_data['static'])}")
        print(f"    Animated frames: {len(viz_data['animated']['grid_expansion'])}")
        print(f"    Interactive features: {len(interactive_features)}")
        
        self.results['step_7'] = {
            'status': 'completed',
            'visualization_data': viz_data
        }
        
        # Save step 7 data
        step7_data = {
            "visualization_data": viz_data,
            "results": self.results['step_7']
        }
        
        output_file = self.output_dir / "06_step7_visualization_preparation.json"
        with open(output_file, 'w') as f:
            json.dump(step7_data, f, indent=2)
        print(f"✅ Saved step 7 data to {output_file}")
        
        # Also save the interactive GeoJSON
        interactive_file = self.output_dir / "06_interactive_cities.geojson"
        with open(interactive_file, 'w') as f:
            json.dump(viz_data['interactive']['cities'], f, indent=2)
        print(f"✅ Saved interactive cities GeoJSON to {interactive_file}")
    
    def generate_summary_report(self):
        """Generate comprehensive summary report."""
        print("\n🔹 Workflow Summary Report")
        print("=" * 50)
        
        total_time = time.time() - self.start_time
        
        summary = {
            'workflow_status': 'completed',
            'total_time_seconds': total_time,
            'steps_completed': len(self.results),
            'cells_processed': len(self.cells),
            'locations_analyzed': list(self.cells.keys()),
            'results': self.results
        }
        
        print(f"  Workflow completed in {total_time:.2f} seconds")
        print(f"  Steps completed: {len(self.results)}")
        print(f"  Cells processed: {len(self.cells)}")
        print(f"  Locations analyzed: {', '.join(self.cells.keys())}")
        
        # Step-by-step summary
        print(f"\n  Step Summary:")
        for step_name, step_result in self.results.items():
            status = step_result['status']
            print(f"    {step_name}: {status}")
        
        # Save summary report
        output_file = self.output_dir / "06_workflow_summary.json"
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Saved workflow summary to {output_file}")
        
        return summary


def main():
    """Run the comprehensive H3 workflow."""
    print("🌍 Comprehensive H3 Workflow Example")
    print("=" * 60)
    print("Demonstrating complete H3 analysis pipeline using tested methods")
    print("=" * 60)
    
    # Initialize workflow
    workflow = H3Workflow()
    
    try:
        # Execute workflow steps
        workflow.step_1_data_ingestion()
        workflow.step_2_spatial_analysis()
        workflow.step_3_hierarchical_analysis()
        workflow.step_4_grid_operations()
        workflow.step_5_data_conversion()
        workflow.step_6_advanced_analysis()
        workflow.step_7_visualization_preparation()
        
        # Generate summary report
        summary = workflow.generate_summary_report()
        
        print("\n✅ Comprehensive workflow completed successfully!")
        print("📁 All outputs saved to the 'output' directory")
        
    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        raise


if __name__ == "__main__":
    main() 