"""
H3 Integration Examples.

Examples showing H3 integration with other GEO-INFER-SPACE modules
for comprehensive spatial analysis workflows.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Core H3 functionality
from geo_infer_space.h3 import (
    H3Grid, H3Cell, H3Analytics,
    coordinate_to_cell, grid_disk, polygon_to_cells,
    H3SpatialAnalyzer, H3DensityAnalyzer, H3ClusterAnalyzer
)

# Integration with other SPACE modules
try:
    from geo_infer_space.analytics.vector import geometric_calculations, proximity_analysis
    from geo_infer_space.models.data_models import SpatialBounds
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False
    logging.warning("Vector analytics not available")

try:
    import geopandas as gpd
    import pandas as pd
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    logging.warning("GeoPandas not available")

try:
    from shapely.geometry import Point, Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    logging.warning("Shapely not available")

logger = logging.getLogger(__name__)


def example_h3_vector_integration():
    """
    Example: Integrate H3 with vector analytics.
    
    Shows how to use H3 hexagonal grids with traditional vector operations
    for comprehensive spatial analysis.
    """
    print("H3-Vector Integration Example")
    print("=" * 40)
    
    if not (VECTOR_AVAILABLE and GEOPANDAS_AVAILABLE and SHAPELY_AVAILABLE):
        print("Required dependencies not available. Skipping example.")
        return
    
    # Create H3 grid for San Francisco area
    sf_bounds = {
        'min_lat': 37.7, 'max_lat': 37.8,
        'min_lng': -122.5, 'max_lng': -122.4
    }
    
    # Generate H3 cells for the area
    polygon_coords = [
        (sf_bounds['min_lat'], sf_bounds['min_lng']),
        (sf_bounds['min_lat'], sf_bounds['max_lng']),
        (sf_bounds['max_lat'], sf_bounds['max_lng']),
        (sf_bounds['max_lat'], sf_bounds['min_lng'])
    ]
    
    h3_cells = polygon_to_cells(polygon_coords, resolution=9)
    print(f"Generated {len(h3_cells)} H3 cells for San Francisco area")
    
    # Create H3 grid with synthetic data
    grid = H3Grid()
    
    for i, cell_index in enumerate(list(h3_cells)[:20]):  # Limit for example
        cell = H3Cell(index=cell_index, resolution=9)
        
        # Add synthetic properties
        cell.properties.update({
            'population': 1000 + (i * 50),
            'poi_count': 5 + (i % 10),
            'crime_incidents': 2 + (i % 5),
            'avg_income': 50000 + (i * 1000)
        })
        
        grid.add_cell(cell)
    
    # Convert H3 grid to GeoDataFrame for vector operations
    geometries = []
    properties = []
    
    for cell in grid.cells:
        # Get cell boundary as polygon
        try:
            from geo_infer_space.h3.operations import cell_to_boundary
            boundary = cell_to_boundary(cell.index)
            polygon = Polygon([(lng, lat) for lat, lng in boundary])
            
            geometries.append(polygon)
            properties.append({
                'h3_index': cell.index,
                'population': cell.properties.get('population', 0),
                'poi_count': cell.properties.get('poi_count', 0),
                'crime_incidents': cell.properties.get('crime_incidents', 0)
            })
        except Exception as e:
            logger.warning(f"Failed to process cell {cell.index}: {e}")
    
    if geometries:
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(properties, geometry=geometries, crs='EPSG:4326')
        
        # Apply vector analytics
        gdf_with_calcs = geometric_calculations(gdf)
        print(f"Applied geometric calculations to {len(gdf_with_calcs)} hexagonal cells")
        
        # Calculate density metrics
        gdf_with_calcs['population_density'] = gdf_with_calcs['population'] / gdf_with_calcs['area']
        gdf_with_calcs['crime_rate'] = gdf_with_calcs['crime_incidents'] / gdf_with_calcs['population'] * 1000
        
        print(f"Average population density: {gdf_with_calcs['population_density'].mean():.2f}")
        print(f"Average crime rate: {gdf_with_calcs['crime_rate'].mean():.2f} per 1000 residents")
        
        # Find high-density areas using H3 spatial analysis
        analyzer = H3SpatialAnalyzer(grid)
        hotspots = analyzer.detect_hotspots('population', method='getis_ord')
        
        print(f"Detected {len(hotspots.get('hotspots', []))} population hotspots")
        print(f"Detected {len(hotspots.get('coldspots', []))} population coldspots")
    
    print("H3-Vector integration completed successfully\n")


def example_h3_density_clustering():
    """
    Example: H3 density analysis with clustering.
    
    Demonstrates density-based spatial analysis using H3 grids
    combined with clustering algorithms.
    """
    print("H3 Density-Clustering Analysis Example")
    print("=" * 40)
    
    # Create H3 grid with density patterns
    grid = H3Grid()
    
    # Simulate urban density patterns
    city_centers = [
        (37.7749, -122.4194),  # San Francisco
        (37.7849, -122.4094),  # North area
        (37.7649, -122.4294),  # South area
    ]
    
    cell_count = 0
    for center_lat, center_lng in city_centers:
        # Create density gradient around each center
        center_cell = coordinate_to_cell(center_lat, center_lng, 8)
        
        # Get cells within 3 rings of center
        area_cells = grid_disk(center_cell, 3)
        
        for cell_index in area_cells:
            if cell_count >= 50:  # Limit for example
                break
                
            cell = H3Cell(index=cell_index, resolution=8)
            
            # Calculate distance from center for density gradient
            try:
                from geo_infer_space.h3.operations import grid_distance
                distance = grid_distance(center_cell, cell_index)
                
                # Higher density closer to center
                base_density = 1000
                density = max(100, base_density - (distance * 150))
                
                cell.properties.update({
                    'population_density': density,
                    'business_count': max(5, 50 - (distance * 8)),
                    'traffic_volume': max(100, 1000 - (distance * 100)),
                    'center_distance': distance
                })
                
                grid.add_cell(cell)
                cell_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to process cell {cell_index}: {e}")
    
    print(f"Created H3 grid with {len(grid.cells)} cells")
    
    # Density analysis
    density_analyzer = H3DensityAnalyzer(grid)
    
    # Calculate kernel density
    density_result = density_analyzer.calculate_kernel_density(
        'population_density', 
        bandwidth_rings=2,
        kernel_type='gaussian'
    )
    
    print(f"Kernel density analysis completed:")
    stats = density_result['statistics']
    print(f"  Mean density: {stats['mean_density']:.2f}")
    print(f"  Max density: {stats['max_density']:.2f}")
    print(f"  Min density: {stats['min_density']:.2f}")
    
    # Pattern analysis
    patterns = density_analyzer.analyze_density_patterns('population_density')
    
    print(f"Density pattern analysis:")
    summary = patterns['pattern_summary']
    print(f"  High-density areas: {summary['n_high_density']}")
    print(f"  Low-density areas: {summary['n_low_density']}")
    print(f"  Significant gradients: {summary['n_significant_gradients']}")
    
    # Clustering analysis
    cluster_analyzer = H3ClusterAnalyzer(grid)
    
    # Density-based clustering
    clusters = cluster_analyzer.density_based_clustering(
        'population_density',
        eps_rings=1
    )
    
    print(f"Clustering analysis:")
    print(f"  Number of clusters: {clusters['n_clusters']}")
    print(f"  Noise points: {clusters['n_noise']}")
    print(f"  Total cells analyzed: {len(clusters['clusters'])}")
    
    print("H3 density-clustering analysis completed successfully\n")


def example_h3_temporal_analysis():
    """
    Example: H3 temporal pattern analysis.
    
    Shows temporal analysis of spatial data using H3 grids
    for time-series spatial analytics.
    """
    print("H3 Temporal Analysis Example")
    print("=" * 40)
    
    # Create H3 grid with temporal data
    grid = H3Grid()
    
    # Simulate 24 hours of activity data
    base_time = datetime(2023, 6, 15, 0, 0, 0)  # June 15, 2023
    sf_center = (37.7749, -122.4194)
    
    # Create cells around SF with hourly data
    center_cell = coordinate_to_cell(sf_center[0], sf_center[1], 9)
    area_cells = list(grid_disk(center_cell, 2))[:15]  # Limit for example
    
    for hour in range(24):
        for i, cell_index in enumerate(area_cells):
            cell = H3Cell(index=cell_index, resolution=9)
            
            # Create realistic temporal patterns
            if 7 <= hour <= 9:  # Morning rush
                activity_level = 80 + (i * 5)
            elif 17 <= hour <= 19:  # Evening rush
                activity_level = 90 + (i * 4)
            elif 12 <= hour <= 14:  # Lunch time
                activity_level = 60 + (i * 3)
            elif 22 <= hour or hour <= 5:  # Night
                activity_level = 10 + (i * 2)
            else:  # Regular hours
                activity_level = 40 + (i * 3)
            
            # Add some randomness
            import random
            activity_level += random.randint(-10, 10)
            activity_level = max(0, activity_level)
            
            timestamp = base_time + timedelta(hours=hour)
            
            cell.properties.update({
                'timestamp': timestamp.isoformat(),
                'activity_level': activity_level,
                'hour': hour,
                'trip_count': activity_level // 2,
                'cell_id': i
            })
            
            grid.add_cell(cell)
    
    print(f"Created temporal H3 grid with {len(grid.cells)} cell-time observations")
    
    # Temporal analysis
    from geo_infer_space.h3.analytics import H3TemporalAnalyzer
    temporal_analyzer = H3TemporalAnalyzer(grid)
    
    # Analyze temporal patterns
    patterns = temporal_analyzer.analyze_temporal_patterns(
        'timestamp', 
        'activity_level',
        'hour'
    )
    
    print("Temporal pattern analysis:")
    temporal_patterns = patterns['temporal_patterns']
    
    # Show peak periods
    peak_periods = temporal_patterns['peak_periods']
    print("Top 3 peak activity periods:")
    for i, period in enumerate(peak_periods[:3]):
        print(f"  {i+1}. {period['period_name']}: {period['mean_value']:.1f} avg activity")
    
    print(f"Pattern type: {temporal_patterns['pattern_type']}")
    print(f"Temporal variability: {temporal_patterns['temporal_variability']:.3f}")
    
    # Anomaly detection
    anomalies = temporal_analyzer.detect_temporal_anomalies(
        'timestamp',
        'activity_level',
        method='zscore',
        threshold=2.0
    )
    
    print(f"Anomaly detection:")
    print(f"  Total anomalies detected: {len(anomalies['anomalies'])}")
    print(f"  Anomaly rate: {anomalies['anomaly_rate']:.3f}")
    
    # Show some anomalies
    if anomalies['anomalies']:
        print("Sample anomalies:")
        for anomaly in anomalies['anomalies'][:3]:
            print(f"  Cell {anomaly['cell_index']}: {anomaly['value']:.1f} "
                  f"(z-score: {anomaly['zscore']:.2f}, type: {anomaly['anomaly_type']})")
    
    print("H3 temporal analysis completed successfully\n")


def example_h3_multi_resolution_analysis():
    """
    Example: Multi-resolution H3 analysis.
    
    Demonstrates analysis across multiple H3 resolutions
    for hierarchical spatial understanding.
    """
    print("H3 Multi-Resolution Analysis Example")
    print("=" * 40)
    
    # Define analysis area (San Francisco Bay Area)
    bay_area_bounds = [
        (37.4, -122.6),  # SW
        (37.4, -122.0),  # SE  
        (37.9, -122.0),  # NE
        (37.9, -122.6),  # NW
    ]
    
    # Analyze at multiple resolutions
    resolutions = [6, 7, 8, 9]
    resolution_results = {}
    
    for resolution in resolutions:
        print(f"Analyzing at resolution {resolution}...")
        
        # Get H3 cells for the area
        cells = polygon_to_cells(bay_area_bounds, resolution)
        
        # Create grid with synthetic data
        grid = H3Grid()
        
        for i, cell_index in enumerate(list(cells)[:min(50, len(cells))]):  # Limit for example
            cell = H3Cell(index=cell_index, resolution=resolution)
            
            # Simulate population data (higher resolution = more detailed)
            base_pop = 1000 if resolution <= 7 else 100
            population = base_pop + (i * (10 if resolution <= 7 else 5))
            
            cell.properties.update({
                'population': population,
                'area_km2': 10 / (2 ** (resolution - 6)),  # Approximate area scaling
                'density': population / (10 / (2 ** (resolution - 6)))
            })
            
            grid.add_cell(cell)
        
        # Calculate statistics
        total_population = sum(cell.properties.get('population', 0) for cell in grid.cells)
        total_area = sum(cell.properties.get('area_km2', 0) for cell in grid.cells)
        avg_density = total_population / total_area if total_area > 0 else 0
        
        # Spatial analysis
        analyzer = H3SpatialAnalyzer(grid)
        spatial_autocorr = analyzer.analyze_spatial_autocorrelation('population')
        
        resolution_results[resolution] = {
            'num_cells': len(grid.cells),
            'total_population': total_population,
            'total_area_km2': total_area,
            'avg_density': avg_density,
            'spatial_autocorrelation': spatial_autocorr.get('morans_i', 0),
            'grid': grid
        }
        
        print(f"  Resolution {resolution}: {len(grid.cells)} cells, "
              f"density: {avg_density:.1f} pop/km²")
    
    # Compare across resolutions
    print("\nMulti-resolution comparison:")
    print("Resolution | Cells | Avg Density | Spatial Autocorr")
    print("-" * 50)
    
    for res in resolutions:
        result = resolution_results[res]
        print(f"    {res:2d}     | {result['num_cells']:5d} | "
              f"{result['avg_density']:8.1f}  | {result['spatial_autocorrelation']:8.3f}")
    
    # Hierarchical analysis
    print("\nHierarchical relationships:")
    for i in range(len(resolutions) - 1):
        coarse_res = resolutions[i]
        fine_res = resolutions[i + 1]
        
        coarse_cells = resolution_results[coarse_res]['num_cells']
        fine_cells = resolution_results[fine_res]['num_cells']
        
        ratio = fine_cells / coarse_cells if coarse_cells > 0 else 0
        print(f"Resolution {coarse_res} -> {fine_res}: {ratio:.1f}x more cells")
    
    print("Multi-resolution analysis completed successfully\n")


def example_h3_orchestration_workflow():
    """
    Example: Complete H3 orchestration workflow.
    
    Demonstrates a complete spatial analysis workflow using H3
    integrated with multiple SPACE modules.
    """
    print("H3 Orchestration Workflow Example")
    print("=" * 40)
    
    # Step 1: Data preparation
    print("Step 1: Data Preparation")
    
    # Define study area
    study_area = {
        'name': 'Downtown San Francisco',
        'bounds': [(37.77, -122.43), (37.77, -122.41), (37.79, -122.41), (37.79, -122.43)]
    }
    
    # Generate H3 grid
    h3_cells = polygon_to_cells(study_area['bounds'], resolution=9)
    grid = H3Grid()
    
    # Add synthetic urban data
    for i, cell_index in enumerate(list(h3_cells)[:30]):  # Limit for example
        cell = H3Cell(index=cell_index, resolution=9)
        
        # Simulate urban indicators
        cell.properties.update({
            'population': 800 + (i * 25),
            'employment': 400 + (i * 15),
            'retail_sqft': 5000 + (i * 200),
            'green_space_pct': max(5, 30 - (i * 0.8)),
            'transit_access': min(10, 3 + (i * 0.2)),
            'housing_units': 300 + (i * 10),
            'avg_rent': 3000 + (i * 50)
        })
        
        grid.add_cell(cell)
    
    print(f"Created H3 grid with {len(grid.cells)} cells for {study_area['name']}")
    
    # Step 2: Spatial analysis
    print("\nStep 2: Spatial Analysis")
    
    spatial_analyzer = H3SpatialAnalyzer(grid)
    
    # Population clustering
    pop_hotspots = spatial_analyzer.detect_hotspots('population', method='getis_ord')
    print(f"Population hotspots: {len(pop_hotspots.get('hotspots', []))}")
    
    # Employment accessibility
    emp_autocorr = spatial_analyzer.analyze_spatial_autocorrelation('employment')
    print(f"Employment spatial autocorrelation: {emp_autocorr.get('morans_i', 0):.3f}")
    
    # Step 3: Density analysis
    print("\nStep 3: Density Analysis")
    
    density_analyzer = H3DensityAnalyzer(grid)
    
    # Population density surface
    pop_density = density_analyzer.calculate_kernel_density('population', bandwidth_rings=2)
    print(f"Population density analysis: {len(pop_density['density_surface'])} cells analyzed")
    
    # Housing density patterns
    housing_patterns = density_analyzer.analyze_density_patterns('housing_units')
    print(f"Housing patterns: {housing_patterns['pattern_summary']['n_high_density']} high-density areas")
    
    # Step 4: Clustering analysis
    print("\nStep 4: Clustering Analysis")
    
    cluster_analyzer = H3ClusterAnalyzer(grid)
    
    # Economic clustering
    econ_clusters = cluster_analyzer.density_based_clustering('employment', eps_rings=1)
    print(f"Economic clusters: {econ_clusters['n_clusters']} clusters identified")
    
    # Step 5: Integrated metrics
    print("\nStep 5: Integrated Urban Metrics")
    
    # Calculate composite indicators
    composite_scores = []
    
    for cell in grid.cells:
        props = cell.properties
        
        # Livability score (0-100)
        livability = (
            (props.get('green_space_pct', 0) / 30 * 25) +  # Green space (25 points)
            (min(props.get('transit_access', 0), 10) / 10 * 25) +  # Transit (25 points)
            (min(props.get('employment', 0), 1000) / 1000 * 25) +  # Jobs (25 points)
            (max(0, 100 - props.get('avg_rent', 3000) / 50) / 100 * 25)  # Affordability (25 points)
        )
        
        # Economic vitality score (0-100)
        vitality = (
            (min(props.get('employment', 0), 1000) / 1000 * 40) +  # Employment (40 points)
            (min(props.get('retail_sqft', 0), 10000) / 10000 * 30) +  # Retail (30 points)
            (min(props.get('population', 0), 1500) / 1500 * 30)  # Population (30 points)
        )
        
        composite_scores.append({
            'cell_index': cell.index,
            'livability_score': livability,
            'vitality_score': vitality,
            'composite_score': (livability + vitality) / 2
        })
    
    # Summary statistics
    avg_livability = sum(s['livability_score'] for s in composite_scores) / len(composite_scores)
    avg_vitality = sum(s['vitality_score'] for s in composite_scores) / len(composite_scores)
    avg_composite = sum(s['composite_score'] for s in composite_scores) / len(composite_scores)
    
    print(f"Average livability score: {avg_livability:.1f}/100")
    print(f"Average economic vitality: {avg_vitality:.1f}/100")
    print(f"Average composite score: {avg_composite:.1f}/100")
    
    # Identify top-performing areas
    top_areas = sorted(composite_scores, key=lambda x: x['composite_score'], reverse=True)[:5]
    print("\nTop 5 performing areas:")
    for i, area in enumerate(top_areas):
        print(f"  {i+1}. Cell {area['cell_index'][:8]}...: {area['composite_score']:.1f}")
    
    # Step 6: Spatial bounds integration
    if VECTOR_AVAILABLE:
        print("\nStep 6: Spatial Bounds Integration")
        
        # Calculate overall study area bounds
        all_coords = []
        for cell in grid.cells:
            try:
                from geo_infer_space.h3.operations import cell_to_coordinates
                lat, lng = cell_to_coordinates(cell.index)
                all_coords.append((lat, lng))
            except:
                pass
        
        if all_coords:
            lats = [coord[0] for coord in all_coords]
            lngs = [coord[1] for coord in all_coords]
            
            bounds = SpatialBounds(
                minx=min(lngs), miny=min(lats),
                maxx=max(lngs), maxy=max(lats)
            )
            
            print(f"Study area bounds: {bounds.area:.6f} square degrees")
            print(f"Approximate area: {bounds.area * 111.32 * 111.32:.2f} km²")
    
    print("\nH3 orchestration workflow completed successfully!")
    print("=" * 40)


def main():
    """Run all H3 integration examples."""
    print("GEO-INFER-SPACE H3 Integration Examples")
    print("=" * 50)
    print()
    
    try:
        example_h3_vector_integration()
    except Exception as e:
        print(f"H3-Vector integration example failed: {e}\n")
    
    try:
        example_h3_density_clustering()
    except Exception as e:
        print(f"H3 density-clustering example failed: {e}\n")
    
    try:
        example_h3_temporal_analysis()
    except Exception as e:
        print(f"H3 temporal analysis example failed: {e}\n")
    
    try:
        example_h3_multi_resolution_analysis()
    except Exception as e:
        print(f"H3 multi-resolution example failed: {e}\n")
    
    try:
        example_h3_orchestration_workflow()
    except Exception as e:
        print(f"H3 orchestration workflow example failed: {e}\n")
    
    print("All H3 integration examples completed!")


if __name__ == "__main__":
    main()
