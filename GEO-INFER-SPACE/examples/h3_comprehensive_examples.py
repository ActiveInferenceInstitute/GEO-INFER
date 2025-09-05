#!/usr/bin/env python3
"""
Comprehensive H3 Examples for GEO-INFER-SPACE.

This script demonstrates real-world applications of H3 hexagonal grid operations
with visualizations, analytics, and practical use cases using H3 v4 API.

Run with: python examples/h3_comprehensive_examples.py
"""

import sys
import os
import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from geo_infer_space.h3.core import H3Cell, H3Grid, H3Analytics, H3Visualizer, H3Validator
    from geo_infer_space.h3.operations import *
    from geo_infer_space.h3.visualization import H3MapVisualizer, H3StaticVisualizer, H3InteractiveVisualizer
    H3_MODULES_AVAILABLE = True
except ImportError as e:
    logger.error(f"H3 modules not available: {e}")
    H3_MODULES_AVAILABLE = False
    sys.exit(1)

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    logger.error("h3-py package not available. Install with 'pip install h3'")
    H3_AVAILABLE = False
    sys.exit(1)


def example_1_basic_h3_operations():
    """
    Example 1: Basic H3 Operations
    Demonstrates fundamental H3 operations with real coordinates.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: BASIC H3 OPERATIONS")
    print("="*60)
    
    # Real-world locations
    locations = {
        'San Francisco': (37.7749, -122.4194),
        'New York': (40.7128, -74.0060),
        'London': (51.5074, -0.1278),
        'Tokyo': (35.6762, 139.6503)
    }
    
    print("Converting coordinates to H3 cells at different resolutions:")
    print("-" * 60)
    
    for city, (lat, lng) in locations.items():
        print(f"\n{city}: ({lat}, {lng})")
        
        for resolution in [7, 8, 9, 10]:
            # Convert to H3 cell
            cell_index = coordinate_to_cell(lat, lng, resolution)
            
            # Get cell properties
            cell_lat, cell_lng = cell_to_coordinates(cell_index)
            area = cell_area(cell_index, 'km^2')
            
            print(f"  Resolution {resolution:2d}: {cell_index} | Area: {area:.6f} km²")
            
            # Validate cell
            validation = H3Validator.validate_h3_index(cell_index)
            assert validation['valid'], f"Invalid cell generated for {city}"
    
    print("\nTesting grid operations:")
    print("-" * 30)
    
    # Use San Francisco for grid operations
    sf_cell = coordinate_to_cell(37.7749, -122.4194, 9)
    print(f"SF Center Cell: {sf_cell}")
    
    # Get neighbors
    neighbors = neighbor_cells(sf_cell)
    print(f"Direct neighbors: {len(neighbors)} cells")
    
    # Get k-ring
    k2_ring = grid_disk(sf_cell, k=2)
    print(f"2-ring disk: {len(k2_ring)} cells")
    
    # Calculate total area
    total_area = cells_area(k2_ring, 'km^2')
    print(f"Total area of 2-ring: {total_area:.4f} km²")
    
    # Test distance calculation
    if neighbors:
        distance = grid_distance(sf_cell, neighbors[0])
        print(f"Distance to first neighbor: {distance} cells")
        
        # Test path finding
        path = grid_path(sf_cell, neighbors[0])
        print(f"Path to neighbor: {len(path)} cells")


def example_2_city_coverage_analysis():
    """
    Example 2: City Coverage Analysis
    Demonstrates H3 grid creation and analysis for urban areas.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: CITY COVERAGE ANALYSIS")
    print("="*60)
    
    # Define city boundaries (simplified polygons)
    cities = {
        'San Francisco': [
            (37.8044, -122.5144),  # Northwest
            (37.8044, -122.3549),  # Northeast
            (37.7049, -122.3549),  # Southeast
            (37.7049, -122.5144)   # Southwest
        ],
        'Manhattan': [
            (40.8176, -73.9442),   # North
            (40.8176, -73.9734),   # Northwest
            (40.7047, -73.9734),   # Southwest
            (40.7047, -73.9442)    # Southeast
        ]
    }
    
    for city_name, boundary in cities.items():
        print(f"\nAnalyzing {city_name}:")
        print("-" * 40)
        
        # Create H3 grids at different resolutions
        for resolution in [7, 8, 9]:
            grid = H3Grid.from_polygon(boundary, resolution, name=f"{city_name}_Res{resolution}")
            
            print(f"Resolution {resolution}: {len(grid.cells)} cells")
            
            # Analyze grid
            analytics = H3Analytics(grid)
            stats = analytics.basic_statistics()
            
            print(f"  Total area: {stats['total_area_km2']:.2f} km²")
            print(f"  Average cell area: {stats['mean_area_km2']:.6f} km²")
            
            # Connectivity analysis
            connectivity = analytics.connectivity_analysis()
            print(f"  Connectivity ratio: {connectivity.get('connectivity_ratio', 0):.3f}")
            print(f"  Isolated cells: {connectivity.get('isolated_cells', 0)}")
            
            # Test compaction
            compacted = grid.compact()
            print(f"  Compacted to: {len(compacted.cells)} cells")
        
        print()


def example_3_transportation_corridor():
    """
    Example 3: Transportation Corridor Analysis
    Demonstrates H3 for transportation network analysis.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: TRANSPORTATION CORRIDOR ANALYSIS")
    print("="*60)
    
    # Define transportation corridors
    corridors = {
        'SF_to_Oakland': {
            'start': (37.7749, -122.4194),  # San Francisco
            'end': (37.8044, -122.2712),    # Oakland
            'name': 'SF-Oakland Corridor'
        },
        'Manhattan_to_Brooklyn': {
            'start': (40.7831, -73.9712),   # Manhattan
            'end': (40.6782, -73.9442),     # Brooklyn
            'name': 'Manhattan-Brooklyn Corridor'
        }
    }
    
    for corridor_id, corridor_data in corridors.items():
        print(f"\nAnalyzing {corridor_data['name']}:")
        print("-" * 50)
        
        start_coords = corridor_data['start']
        end_coords = corridor_data['end']
        
        # Create cells for start and end points
        start_cell = coordinate_to_cell(*start_coords, 9)
        end_cell = coordinate_to_cell(*end_coords, 9)
        
        print(f"Start cell: {start_cell}")
        print(f"End cell: {end_cell}")
        
        # Calculate direct distance
        direct_distance = grid_distance(start_cell, end_cell)
        print(f"Grid distance: {direct_distance} cells")
        
        # Find path
        try:
            path_cells = grid_path(start_cell, end_cell)
            print(f"Path length: {len(path_cells)} cells")
            
            # Create corridor with buffer
            corridor_cells = set()
            for cell in path_cells:
                # Add cell and its neighbors (1km buffer approximation)
                buffer_cells = grid_disk(cell, k=2)
                corridor_cells.update(buffer_cells)
            
            # Create grid
            h3_cells = [H3Cell(index=idx, resolution=9) for idx in corridor_cells]
            corridor_grid = H3Grid(cells=h3_cells, name=corridor_data['name'])
            
            # Analyze corridor
            analytics = H3Analytics(corridor_grid)
            stats = analytics.basic_statistics()
            
            print(f"Corridor cells (with buffer): {len(corridor_grid.cells)}")
            print(f"Total corridor area: {stats['total_area_km2']:.2f} km²")
            print(f"Corridor bounds: {corridor_grid.bounds()}")
            
        except Exception as e:
            print(f"Path finding failed: {e}")


def example_4_retail_catchment_analysis():
    """
    Example 4: Retail Catchment Analysis
    Demonstrates H3 for retail location analysis and market coverage.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: RETAIL CATCHMENT ANALYSIS")
    print("="*60)
    
    # Define store locations in San Francisco
    stores = {
        'Downtown_SF': {
            'location': (37.7749, -122.4194),
            'type': 'flagship',
            'catchment_km': 3
        },
        'Mission_District': {
            'location': (37.7599, -122.4148),
            'type': 'neighborhood',
            'catchment_km': 2
        },
        'North_Beach': {
            'location': (37.8067, -122.4104),
            'type': 'neighborhood', 
            'catchment_km': 2
        },
        'Castro': {
            'location': (37.7609, -122.4350),
            'type': 'specialty',
            'catchment_km': 1.5
        }
    }
    
    store_grids = {}
    all_catchment_cells = []
    
    print("Creating catchment areas for stores:")
    print("-" * 40)
    
    for store_id, store_data in stores.items():
        lat, lng = store_data['location']
        catchment_km = store_data['catchment_km']
        
        # Estimate k-ring for catchment (rough approximation)
        # Resolution 9 cells are ~0.1 km², so k=3 ≈ 1km radius
        k_ring = max(1, int(catchment_km * 3))
        
        # Create catchment grid
        catchment_grid = H3Grid.from_center(
            lat, lng, 
            resolution=9, 
            k=k_ring, 
            name=f"{store_id}_Catchment"
        )
        
        # Add store properties to cells
        for cell in catchment_grid.cells:
            cell.properties['store_id'] = store_id
            cell.properties['store_type'] = store_data['type']
            cell.properties['distance_to_store'] = grid_distance(
                coordinate_to_cell(lat, lng, 9), 
                cell.index
            )
        
        store_grids[store_id] = catchment_grid
        all_catchment_cells.extend([cell.index for cell in catchment_grid.cells])
        
        # Analyze catchment
        analytics = H3Analytics(catchment_grid)
        stats = analytics.basic_statistics()
        
        print(f"{store_id}:")
        print(f"  Location: ({lat:.4f}, {lng:.4f})")
        print(f"  Catchment cells: {len(catchment_grid.cells)}")
        print(f"  Catchment area: {stats['total_area_km2']:.2f} km²")
        print(f"  Store type: {store_data['type']}")
    
    # Analyze market coverage and overlap
    print("\nMarket Coverage Analysis:")
    print("-" * 30)
    
    unique_cells = set(all_catchment_cells)
    total_cells = len(all_catchment_cells)
    unique_count = len(unique_cells)
    
    overlap_cells = total_cells - unique_count
    overlap_ratio = overlap_cells / total_cells if total_cells > 0 else 0
    
    print(f"Total catchment cells: {total_cells}")
    print(f"Unique cells: {unique_count}")
    print(f"Overlapping cells: {overlap_cells}")
    print(f"Overlap ratio: {overlap_ratio:.3f}")
    
    # Find coverage gaps (simplified)
    # Create overall market area
    all_store_locations = [store['location'] for store in stores.values()]
    
    # Calculate market bounds
    lats = [loc[0] for loc in all_store_locations]
    lngs = [loc[1] for loc in all_store_locations]
    
    market_polygon = [
        (min(lats) - 0.01, min(lngs) - 0.01),
        (min(lats) - 0.01, max(lngs) + 0.01),
        (max(lats) + 0.01, max(lngs) + 0.01),
        (max(lats) + 0.01, min(lngs) - 0.01)
    ]
    
    market_grid = H3Grid.from_polygon(market_polygon, resolution=9, name="Market_Area")
    market_cells = set(cell.index for cell in market_grid.cells)
    
    uncovered_cells = market_cells - unique_cells
    coverage_ratio = (len(market_cells) - len(uncovered_cells)) / len(market_cells)
    
    print(f"Market area cells: {len(market_cells)}")
    print(f"Uncovered cells: {len(uncovered_cells)}")
    print(f"Coverage ratio: {coverage_ratio:.3f}")


def example_5_environmental_monitoring():
    """
    Example 5: Environmental Monitoring Grid
    Demonstrates H3 for environmental data collection and analysis.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: ENVIRONMENTAL MONITORING GRID")
    print("="*60)
    
    # Define monitoring area (San Francisco Bay)
    bay_area_polygon = [
        (37.9, -122.6),   # Northwest
        (37.9, -121.9),   # Northeast
        (37.3, -121.9),   # Southeast
        (37.3, -122.6)    # Southwest
    ]
    
    print("Creating environmental monitoring grids:")
    print("-" * 45)
    
    # Create monitoring grids at different resolutions
    monitoring_grids = {}
    
    for resolution in [6, 7, 8]:
        grid = H3Grid.from_polygon(
            bay_area_polygon, 
            resolution, 
            name=f"Bay_Monitoring_Res{resolution}"
        )
        monitoring_grids[resolution] = grid
        
        print(f"Resolution {resolution}: {len(grid.cells)} monitoring stations")
        
        # Simulate environmental data
        np.random.seed(42)  # For reproducible results
        
        for cell in grid.cells:
            # Simulate air quality data
            cell.properties['pm25'] = np.random.normal(15, 5)  # PM2.5 levels
            cell.properties['ozone'] = np.random.normal(0.08, 0.02)  # Ozone levels
            cell.properties['temperature'] = np.random.normal(18, 3)  # Temperature
            cell.properties['humidity'] = np.random.normal(65, 10)  # Humidity
            
            # Add monitoring station info
            cell.properties['station_id'] = f"STATION_{cell.index[:8]}"
            cell.properties['last_updated'] = datetime.now().isoformat()
        
        # Analyze environmental data
        analytics = H3Analytics(grid)
        stats = analytics.basic_statistics()
        
        print(f"  Grid area: {stats['total_area_km2']:.0f} km²")
        print(f"  Station density: {len(grid.cells) / stats['total_area_km2']:.3f} stations/km²")
        
        # Calculate environmental statistics
        pm25_values = [cell.properties['pm25'] for cell in grid.cells]
        ozone_values = [cell.properties['ozone'] for cell in grid.cells]
        
        print(f"  PM2.5 range: {min(pm25_values):.1f} - {max(pm25_values):.1f} μg/m³")
        print(f"  Ozone range: {min(ozone_values):.3f} - {max(ozone_values):.3f} ppm")
    
    # Demonstrate data aggregation across resolutions
    print("\nData Aggregation Analysis:")
    print("-" * 30)
    
    # Aggregate data from high resolution to low resolution
    high_res_grid = monitoring_grids[8]
    low_res_grid = monitoring_grids[6]
    
    # For each low-res cell, find overlapping high-res cells
    for low_res_cell in low_res_grid.cells:
        # Get children at high resolution
        try:
            children = cell_to_children(low_res_cell.index, 8)
            
            # Find matching high-res cells
            matching_cells = [cell for cell in high_res_grid.cells if cell.index in children]
            
            if matching_cells:
                # Aggregate environmental data
                avg_pm25 = np.mean([cell.properties['pm25'] for cell in matching_cells])
                avg_ozone = np.mean([cell.properties['ozone'] for cell in matching_cells])
                
                low_res_cell.properties['aggregated_pm25'] = avg_pm25
                low_res_cell.properties['aggregated_ozone'] = avg_ozone
                low_res_cell.properties['source_stations'] = len(matching_cells)
                
        except Exception as e:
            logger.warning(f"Aggregation failed for cell {low_res_cell.index}: {e}")
    
    # Report aggregation results
    aggregated_cells = [cell for cell in low_res_grid.cells if 'aggregated_pm25' in cell.properties]
    print(f"Successfully aggregated data for {len(aggregated_cells)} low-res cells")
    
    if aggregated_cells:
        avg_stations_per_cell = np.mean([cell.properties['source_stations'] for cell in aggregated_cells])
        print(f"Average stations per aggregated cell: {avg_stations_per_cell:.1f}")


def example_6_disaster_response_planning():
    """
    Example 6: Disaster Response Planning
    Demonstrates H3 for emergency response and evacuation planning.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: DISASTER RESPONSE PLANNING")
    print("="*60)
    
    # Emergency response center
    emergency_center = (37.7749, -122.4194)  # San Francisco City Hall
    
    print(f"Emergency Response Center: ({emergency_center[0]}, {emergency_center[1]})")
    print("-" * 60)
    
    # Define response zones
    response_zones = {
        'immediate': {
            'k': 2,
            'response_time_min': 5,
            'description': 'First responders, critical infrastructure'
        },
        'primary': {
            'k': 5,
            'response_time_min': 15,
            'description': 'Emergency services, hospitals'
        },
        'secondary': {
            'k': 8,
            'response_time_min': 30,
            'description': 'Support services, evacuation centers'
        },
        'extended': {
            'k': 12,
            'response_time_min': 60,
            'description': 'Regional coordination, resource staging'
        }
    }
    
    zone_grids = {}
    
    for zone_name, zone_config in response_zones.items():
        print(f"\n{zone_name.upper()} RESPONSE ZONE:")
        print("-" * 30)
        
        # Create response zone grid
        zone_grid = H3Grid.from_center(
            *emergency_center,
            resolution=8,
            k=zone_config['k'],
            name=f"Emergency_{zone_name.title()}_Zone"
        )
        
        zone_grids[zone_name] = zone_grid
        
        # Add zone properties to cells
        for cell in zone_grid.cells:
            cell.properties['zone'] = zone_name
            cell.properties['response_time_min'] = zone_config['response_time_min']
            cell.properties['description'] = zone_config['description']
            
            # Calculate distance from emergency center
            center_cell = coordinate_to_cell(*emergency_center, 8)
            cell.properties['distance_from_center'] = grid_distance(center_cell, cell.index)
        
        # Analyze zone
        analytics = H3Analytics(zone_grid)
        stats = analytics.basic_statistics()
        
        print(f"Zone cells: {len(zone_grid.cells)}")
        print(f"Coverage area: {stats['total_area_km2']:.1f} km²")
        print(f"Response time: {zone_config['response_time_min']} minutes")
        print(f"Description: {zone_config['description']}")
        
        # Calculate zone statistics
        distances = [cell.properties['distance_from_center'] for cell in zone_grid.cells]
        print(f"Distance range: {min(distances)} - {max(distances)} cells from center")
    
    # Analyze zone coverage and overlaps
    print("\nZONE COVERAGE ANALYSIS:")
    print("-" * 30)
    
    zone_names = list(response_zones.keys())
    for i in range(len(zone_names) - 1):
        current_zone = zone_names[i]
        next_zone = zone_names[i + 1]
        
        current_cells = set(cell.index for cell in zone_grids[current_zone].cells)
        next_cells = set(cell.index for cell in zone_grids[next_zone].cells)
        
        # Current zone should be subset of next zone
        coverage_ratio = len(current_cells.intersection(next_cells)) / len(current_cells)
        print(f"{current_zone} -> {next_zone} coverage: {coverage_ratio:.3f}")
    
    # Simulate evacuation scenario
    print("\nEVACUATION SCENARIO SIMULATION:")
    print("-" * 35)
    
    # Define evacuation points
    evacuation_points = [
        (37.7849, -122.4094),  # North evacuation point
        (37.7649, -122.4294),  # South evacuation point
        (37.7749, -122.3894)   # East evacuation point
    ]
    
    # For each evacuation point, analyze accessibility
    for i, evac_point in enumerate(evacuation_points):
        print(f"\nEvacuation Point {i+1}: ({evac_point[0]:.4f}, {evac_point[1]:.4f})")
        
        # Create evacuation catchment
        evac_grid = H3Grid.from_center(*evac_point, resolution=8, k=6, name=f"Evacuation_Point_{i+1}")
        
        # Calculate accessibility from emergency zones
        evac_cells = set(cell.index for cell in evac_grid.cells)
        
        for zone_name, zone_grid in zone_grids.items():
            zone_cells = set(cell.index for cell in zone_grid.cells)
            accessible_cells = zone_cells.intersection(evac_cells)
            accessibility_ratio = len(accessible_cells) / len(zone_cells) if zone_cells else 0
            
            print(f"  {zone_name} zone accessibility: {accessibility_ratio:.3f}")


def example_7_visualization_showcase():
    """
    Example 7: Visualization Showcase
    Demonstrates various H3 visualization capabilities.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: VISUALIZATION SHOWCASE")
    print("="*60)
    
    # Create sample grid with data
    center_coords = (37.7749, -122.4194)  # San Francisco
    sample_grid = H3Grid.from_center(*center_coords, resolution=9, k=3, name="Visualization_Demo")
    
    # Add sample data to cells
    np.random.seed(42)
    for i, cell in enumerate(sample_grid.cells):
        cell.properties['value'] = np.random.normal(100, 20)
        cell.properties['category'] = ['A', 'B', 'C'][i % 3]
        cell.properties['intensity'] = np.random.uniform(0, 1)
        cell.properties['population'] = np.random.randint(50, 500)
    
    print(f"Created sample grid with {len(sample_grid.cells)} cells")
    print("Sample cell properties:", list(sample_grid.cells[0].properties.keys()))
    
    # Create output directory
    output_dir = Path("output/h3_visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving visualizations to: {output_dir}")
    
    # 1. GeoJSON Export
    print("\n1. Exporting to GeoJSON...")
    geojson_path = output_dir / "sample_grid.geojson"
    
    visualizer = H3Visualizer(sample_grid)
    visualizer.save_geojson(str(geojson_path))
    print(f"   Saved: {geojson_path}")
    
    # 2. DataFrame Export
    print("\n2. Exporting to DataFrame...")
    df = sample_grid.to_dataframe()
    csv_path = output_dir / "sample_grid.csv"
    df.to_csv(csv_path, index=False)
    print(f"   Saved: {csv_path}")
    print(f"   DataFrame shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    # 3. Static Visualizations
    print("\n3. Creating static visualizations...")
    try:
        static_viz = H3StaticVisualizer(sample_grid)
        
        # Grid overview
        overview_fig = static_viz.plot_grid_overview(figsize=(15, 10))
        overview_path = output_dir / "grid_overview.png"
        overview_fig.savefig(overview_path, dpi=300, bbox_inches='tight')
        print(f"   Saved: {overview_path}")
        
        # Hexagon grid plot
        hex_fig = static_viz.plot_hexagon_grid(value_column='value', figsize=(12, 10))
        hex_path = output_dir / "hexagon_grid.png"
        hex_fig.savefig(hex_path, dpi=300, bbox_inches='tight')
        print(f"   Saved: {hex_path}")
        
        # Connectivity analysis
        conn_fig = static_viz.plot_connectivity_analysis(figsize=(12, 6))
        conn_path = output_dir / "connectivity_analysis.png"
        conn_fig.savefig(conn_path, dpi=300, bbox_inches='tight')
        print(f"   Saved: {conn_path}")
        
    except Exception as e:
        print(f"   Static visualization error: {e}")
    
    # 4. Interactive Visualizations
    print("\n4. Creating interactive visualizations...")
    try:
        # Folium map
        map_viz = H3MapVisualizer(sample_grid)
        folium_map = map_viz.create_folium_map(
            value_column='value',
            color_scheme='viridis',
            zoom_start=12
        )
        
        folium_path = output_dir / "interactive_map.html"
        folium_map.save(str(folium_path))
        print(f"   Saved: {folium_path}")
        
        # Heatmap
        heatmap = map_viz.create_heatmap(value_column='intensity', zoom_start=12)
        heatmap_path = output_dir / "heatmap.html"
        heatmap.save(str(heatmap_path))
        print(f"   Saved: {heatmap_path}")
        
    except ImportError:
        print("   Folium not available - skipping interactive maps")
    except Exception as e:
        print(f"   Interactive visualization error: {e}")
    
    # 5. Plotly Visualizations
    print("\n5. Creating Plotly visualizations...")
    try:
        plotly_viz = H3InteractiveVisualizer(sample_grid)
        
        # Interactive map
        plotly_map = plotly_viz.create_plotly_map(value_column='value')
        plotly_path = output_dir / "plotly_map.html"
        plotly_map.write_html(str(plotly_path))
        print(f"   Saved: {plotly_path}")
        
        # Dashboard
        dashboard = plotly_viz.create_dashboard()
        dashboard_path = output_dir / "dashboard.html"
        dashboard.write_html(str(dashboard_path))
        print(f"   Saved: {dashboard_path}")
        
    except ImportError:
        print("   Plotly not available - skipping Plotly visualizations")
    except Exception as e:
        print(f"   Plotly visualization error: {e}")
    
    print(f"\nVisualization showcase complete! Check {output_dir} for outputs.")


def example_8_performance_benchmarks():
    """
    Example 8: Performance Benchmarks
    Demonstrates H3 performance with large datasets.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: PERFORMANCE BENCHMARKS")
    print("="*60)
    
    import time
    
    # Performance test configurations
    test_configs = [
        {'name': 'Small Grid', 'k': 5, 'resolution': 8, 'expected_cells': 91},
        {'name': 'Medium Grid', 'k': 10, 'resolution': 8, 'expected_cells': 331},
        {'name': 'Large Grid', 'k': 15, 'resolution': 7, 'expected_cells': 721},
    ]
    
    center_coords = (37.7749, -122.4194)
    
    print("Grid Creation Performance:")
    print("-" * 30)
    
    for config in test_configs:
        print(f"\n{config['name']} (k={config['k']}, res={config['resolution']}):")
        
        # Time grid creation
        start_time = time.time()
        grid = H3Grid.from_center(*center_coords, resolution=config['resolution'], k=config['k'])
        creation_time = time.time() - start_time
        
        print(f"  Cells created: {len(grid.cells)} (expected: {config['expected_cells']})")
        print(f"  Creation time: {creation_time:.4f} seconds")
        
        # Time analytics
        start_time = time.time()
        analytics = H3Analytics(grid)
        stats = analytics.basic_statistics()
        analytics_time = time.time() - start_time
        
        print(f"  Analytics time: {analytics_time:.4f} seconds")
        print(f"  Total area: {stats['total_area_km2']:.2f} km²")
        
        # Time connectivity analysis
        start_time = time.time()
        connectivity = analytics.connectivity_analysis()
        connectivity_time = time.time() - start_time
        
        print(f"  Connectivity time: {connectivity_time:.4f} seconds")
        print(f"  Connectivity ratio: {connectivity.get('connectivity_ratio', 0):.3f}")
        
        # Performance metrics
        cells_per_second = len(grid.cells) / creation_time if creation_time > 0 else 0
        print(f"  Performance: {cells_per_second:.0f} cells/second")
    
    # Batch operations performance
    print("\nBatch Operations Performance:")
    print("-" * 35)
    
    # Create large set of cells for batch testing
    test_cells = []
    for lat in np.linspace(37.7, 37.8, 20):
        for lng in np.linspace(-122.5, -122.4, 20):
            cell = coordinate_to_cell(lat, lng, 8)
            test_cells.append(cell)
    
    print(f"Testing with {len(test_cells)} cells:")
    
    # Test batch area calculation
    start_time = time.time()
    total_area = cells_area(test_cells)
    area_time = time.time() - start_time
    
    print(f"  Batch area calculation: {area_time:.4f} seconds")
    print(f"  Total area: {total_area:.2f} km²")
    
    # Test batch statistics
    start_time = time.time()
    batch_stats = grid_statistics(test_cells)
    stats_time = time.time() - start_time
    
    print(f"  Batch statistics: {stats_time:.4f} seconds")
    print(f"  Valid cells: {batch_stats['valid_cells']}")
    
    # Test compaction
    start_time = time.time()
    compacted = compact_cells(test_cells)
    compact_time = time.time() - start_time
    
    print(f"  Compaction: {compact_time:.4f} seconds")
    print(f"  Compacted to: {len(compacted)} cells")
    
    # Memory usage estimation
    import sys
    
    single_cell_size = sys.getsizeof(H3Cell(index=test_cells[0], resolution=8))
    estimated_memory_mb = (single_cell_size * len(test_cells)) / (1024 * 1024)
    
    print(f"  Estimated memory usage: {estimated_memory_mb:.2f} MB")


def main():
    """Run all H3 examples."""
    print("H3 COMPREHENSIVE EXAMPLES FOR GEO-INFER-SPACE")
    print("=" * 60)
    print("Demonstrating real-world H3 hexagonal grid operations")
    print("Using H3 v4 API with comprehensive analytics and visualizations")
    print("=" * 60)
    
    if not H3_MODULES_AVAILABLE:
        print("ERROR: H3 modules not available. Please check installation.")
        return 1
    
    if not H3_AVAILABLE:
        print("ERROR: h3-py package not available. Install with 'pip install h3'")
        return 1
    
    try:
        # Run all examples
        example_1_basic_h3_operations()
        example_2_city_coverage_analysis()
        example_3_transportation_corridor()
        example_4_retail_catchment_analysis()
        example_5_environmental_monitoring()
        example_6_disaster_response_planning()
        example_7_visualization_showcase()
        example_8_performance_benchmarks()
        
        print("\n" + "="*60)
        print("ALL H3 EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Check the 'output/h3_visualizations/' directory for generated files.")
        print("Open the HTML files in a web browser to view interactive maps.")
        print("="*60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
