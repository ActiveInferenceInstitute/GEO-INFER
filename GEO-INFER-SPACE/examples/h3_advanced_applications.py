"""
H3 Advanced Applications Examples.

Real-world examples demonstrating H3 machine learning integration,
disaster response, and performance optimization based on Analytics Vidhya guide:
https://www.analyticsvidhya.com/blog/2025/03/ubers-h3-for-spatial-indexing/
"""

import logging
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Core H3 functionality
from geo_infer_space.h3 import (
    H3Grid, H3Cell, coordinate_to_cell, grid_disk, polygon_to_cells
)

# Advanced H3 methods
from geo_infer_space.h3.ml_integration import (
    H3MLFeatureEngine, H3DisasterResponse, H3PerformanceOptimizer
)

# Analytics
from geo_infer_space.h3.analytics import (
    H3SpatialAnalyzer, H3DensityAnalyzer, H3TemporalAnalyzer
)

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    logging.warning("NumPy not available")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available")

logger = logging.getLogger(__name__)


def example_demand_forecasting_ml():
    """
    Example: H3-based demand forecasting for ride-sharing.
    
    Demonstrates ML feature engineering using H3 hexagonal grids
    for demand prediction as described in Analytics Vidhya guide.
    """
    print("H3 Demand Forecasting ML Example")
    print("=" * 40)
    
    # Create H3 grid for San Francisco with ride demand data
    grid = H3Grid()
    
    # Simulate ride demand data across SF
    sf_area = [
        (37.7749, -122.4194),  # Downtown SF
        (37.7849, -122.4094),  # North Beach
        (37.7649, -122.4294),  # Mission
        (37.7949, -122.3994),  # Financial District
        (37.7549, -122.4394),  # Castro
        (37.7449, -122.4494),  # Sunset
        (37.7349, -122.4594),  # Richmond
        (37.8049, -122.4194),  # Russian Hill
    ]
    
    # Create cells with realistic demand patterns
    for i, (lat, lng) in enumerate(sf_area):
        cell = H3Cell.from_coordinates(lat, lng, 9)
        
        # Simulate demand based on area characteristics
        base_demand = 50
        if i in [0, 3]:  # Downtown and Financial District
            demand_multiplier = 3.0
        elif i in [1, 7]:  # North Beach and Russian Hill
            demand_multiplier = 2.0
        else:
            demand_multiplier = 1.0
        
        # Add time-based variation
        hour = (datetime.now().hour + i) % 24
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            time_multiplier = 1.5
        elif 22 <= hour or hour <= 5:  # Night hours
            time_multiplier = 0.3
        else:
            time_multiplier = 1.0
        
        demand = int(base_demand * demand_multiplier * time_multiplier)
        supply = int(demand * 0.8 + random.randint(-10, 10))  # Supply slightly less than demand
        
        cell.properties.update({
            'ride_demand': demand,
            'driver_supply': max(0, supply),
            'population_density': 1000 + (i * 200),
            'poi_count': 10 + (i * 5),
            'avg_trip_distance': 2.5 + (i * 0.3),
            'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
            'weather_score': 0.8 + (i * 0.02),  # Weather favorability
            'event_impact': random.choice([0, 0, 0, 1, 2])  # Special events
        })
        
        grid.add_cell(cell)
    
    print(f"Created demand forecasting grid with {len(grid.cells)} cells")
    
    # ML Feature Engineering
    ml_engine = H3MLFeatureEngine(grid)
    
    # Create demand forecasting features
    demand_features = ml_engine.create_demand_forecasting_features('ride_demand')
    
    print(f"Generated {len(demand_features['features'])} feature sets")
    print(f"Total features per cell: {len(demand_features['feature_names'])}")
    
    # Display sample features
    if demand_features['features']:
        sample_features = demand_features['features'][0]
        print(f"\\nSample features for cell {sample_features['cell_index'][:8]}...:")
        
        key_features = [
            'demand_value', 'demand_density', 'supply_demand_ratio',
            'neighbor_avg', 'demand_gradient', 'utilization_rate',
            'hour', 'is_rush_hour', 'is_weekend'
        ]
        
        for feature in key_features:
            if feature in sample_features:
                value = sample_features[feature]
                if isinstance(value, float):
                    print(f"  {feature}: {value:.3f}")
                else:
                    print(f"  {feature}: {value}")
    
    # Analyze spatial patterns in demand
    spatial_analyzer = H3SpatialAnalyzer(grid)
    demand_autocorr = spatial_analyzer.analyze_spatial_autocorrelation('ride_demand')
    
    print(f"\\nSpatial Analysis:")
    print(f"  Demand spatial autocorrelation: {demand_autocorr.get('morans_i', 0):.3f}")
    print(f"  Pattern: {demand_autocorr.get('interpretation', 'Unknown')}")
    
    # Detect demand hotspots
    hotspots = spatial_analyzer.detect_hotspots('ride_demand', method='getis_ord')
    print(f"  Demand hotspots detected: {len(hotspots.get('hotspots', []))}")
    print(f"  Low-demand areas: {len(hotspots.get('coldspots', []))}")
    
    # Performance optimization recommendations
    optimizer = H3PerformanceOptimizer()
    
    # Estimate area covered by grid
    estimated_area = len(grid.cells) * 0.1  # Rough estimate
    ml_optimization = optimizer.optimize_grid_resolution(
        estimated_area, 
        analysis_type='ml',
        target_cells=len(grid.cells)
    )
    
    print(f"\\nML Optimization Recommendations:")
    print(f"  Current resolution: 9")
    print(f"  Recommended resolution: {ml_optimization['recommended_resolution']}")
    print(f"  Estimated cells: {ml_optimization['estimated_cells']}")
    
    # Simulate ML model training preparation
    print(f"\\nML Training Data Preparation:")
    
    # Convert features to training format
    training_data = []
    for feature_set in demand_features['features']:
        # Extract numerical features only
        numerical_features = {}
        for key, value in feature_set.items():
            if isinstance(value, (int, float)) and key != 'target_value':
                numerical_features[key] = value
        
        training_data.append({
            'features': numerical_features,
            'target': feature_set.get('target_value', 0)
        })
    
    print(f"  Training samples: {len(training_data)}")
    print(f"  Features per sample: {len(training_data[0]['features']) if training_data else 0}")
    
    # Calculate feature importance (simplified)
    if training_data and NUMPY_AVAILABLE:
        feature_names = list(training_data[0]['features'].keys())
        targets = np.array([sample['target'] for sample in training_data])
        
        correlations = []
        for feature_name in feature_names:
            feature_values = np.array([sample['features'][feature_name] for sample in training_data])
            if np.std(feature_values) > 0:  # Avoid division by zero
                correlation = np.corrcoef(feature_values, targets)[0, 1]
                correlations.append((feature_name, abs(correlation)))
        
        # Sort by correlation strength
        correlations.sort(key=lambda x: x[1], reverse=True)
        
        print(f"  Top 5 most correlated features:")
        for i, (feature, corr) in enumerate(correlations[:5]):
            if not math.isnan(corr):
                print(f"    {i+1}. {feature}: {corr:.3f}")
    
    print("\\nDemand forecasting ML example completed successfully\\n")


def example_disaster_response_system():
    """
    Example: H3-based disaster response and evacuation planning.
    
    Demonstrates disaster response capabilities using H3 spatial analysis
    for emergency management and environmental monitoring.
    """
    print("H3 Disaster Response System Example")
    print("=" * 40)
    
    # Create H3 grid for disaster-prone coastal area
    grid = H3Grid()
    
    # Simulate coastal area with varying flood risk
    coastal_area = [
        (37.7749, -122.4194),  # High risk - waterfront
        (37.7759, -122.4184),  # High risk - low elevation
        (37.7739, -122.4204),  # Medium risk - moderate elevation
        (37.7769, -122.4174),  # Medium risk - residential
        (37.7729, -122.4214),  # Low risk - higher elevation
        (37.7779, -122.4164),  # Low risk - inland
        (37.7719, -122.4224),  # Safe zone - hills
        (37.7789, -122.4154),  # Safe zone - elevated
    ]
    
    # Risk factors and population data
    risk_levels = [0.9, 0.85, 0.6, 0.55, 0.3, 0.25, 0.1, 0.05]
    populations = [2000, 1800, 1500, 1200, 1000, 800, 600, 400]
    elevations = [2, 5, 15, 20, 35, 40, 60, 80]  # meters above sea level
    
    for i, ((lat, lng), risk, pop, elev) in enumerate(zip(coastal_area, risk_levels, populations, elevations)):
        cell = H3Cell.from_coordinates(lat, lng, 9)
        
        cell.properties.update({
            'flood_risk': risk,
            'population': pop,
            'elevation': elev,
            'infrastructure_density': 0.9 - (i * 0.1),
            'elderly_population': int(pop * 0.15),  # 15% elderly
            'disabled_population': int(pop * 0.08),  # 8% disabled
            'vehicle_ownership': 0.7 - (i * 0.05),  # Decreasing vehicle ownership
            'building_vulnerability': risk * 0.8,  # Correlated with flood risk
            'emergency_services_distance': i * 0.5,  # km to emergency services
            'baseline_temperature': 20.0,
            'current_temperature': 20.0 + (risk * 3),  # Higher temp in risk areas
            'baseline_water_level': 0.0,
            'current_water_level': risk * 2.5  # Rising water levels
        })
        
        grid.add_cell(cell)
    
    print(f"Created disaster response grid with {len(grid.cells)} cells")
    
    # Disaster Response Analysis
    disaster_analyzer = H3DisasterResponse(grid)
    
    # Analyze evacuation zones
    evacuation_analysis = disaster_analyzer.analyze_evacuation_zones(
        hazard_column='flood_risk',
        population_column='population',
        evacuation_radius_km=3.0
    )
    
    print(f"\\nEvacuation Zone Analysis:")
    print(f"  High-risk zones identified: {len(evacuation_analysis['high_risk_zones'])}")
    print(f"  Total affected population: {evacuation_analysis['total_affected_population']:,}")
    
    # Display high-risk zones
    for i, zone in enumerate(evacuation_analysis['high_risk_zones'][:3]):
        print(f"  Zone {i+1}: Risk {zone['hazard_level']:.2f}, Population {zone['population']:,}")
    
    # Evacuation logistics
    evac_analysis = evacuation_analysis['evacuation_analysis']
    print(f"\\nEvacuation Logistics:")
    print(f"  Estimated vehicles needed: {evac_analysis['estimated_vehicles_needed']:,}")
    print(f"  Estimated evacuation time: {evac_analysis['estimated_evacuation_time_hours']} hours")
    print(f"  Priority zones: {len(evac_analysis['priority_zones'])}")
    
    # Environmental monitoring
    env_changes = disaster_analyzer.monitor_environmental_changes(
        baseline_column='baseline_water_level',
        current_column='current_water_level',
        change_threshold=0.5
    )
    
    print(f"\\nEnvironmental Monitoring:")
    print(f"  Significant changes detected: {len(env_changes['significant_changes'])}")
    print(f"  Change clusters identified: {len(env_changes['change_clusters'])}")
    
    if env_changes['summary_statistics']:
        stats = env_changes['summary_statistics']
        print(f"  Average water level change: {stats['mean_change']:.2f}m")
        print(f"  Maximum change: {stats['max_change']:.2f}m")
    
    # Vulnerability assessment using spatial analysis
    spatial_analyzer = H3SpatialAnalyzer(grid)
    
    # Analyze spatial clustering of vulnerability
    vulnerability_hotspots = spatial_analyzer.detect_hotspots('flood_risk', method='getis_ord')
    
    print(f"\\nVulnerability Assessment:")
    print(f"  Risk hotspots: {len(vulnerability_hotspots.get('hotspots', []))}")
    print(f"  Safe zones: {len(vulnerability_hotspots.get('coldspots', []))}")
    
    # Population density analysis
    density_analyzer = H3DensityAnalyzer(grid)
    pop_density = density_analyzer.calculate_kernel_density('population', bandwidth_rings=2)
    
    print(f"\\nPopulation Density Analysis:")
    density_stats = pop_density['statistics']
    print(f"  Mean population density: {density_stats['mean_density']:.1f}")
    print(f"  Peak density area: {density_stats['max_density']:.1f}")
    
    # Risk-population correlation analysis
    risk_values = [cell.properties['flood_risk'] for cell in grid.cells]
    pop_values = [cell.properties['population'] for cell in grid.cells]
    
    if NUMPY_AVAILABLE and len(risk_values) > 1:
        correlation = np.corrcoef(risk_values, pop_values)[0, 1]
        print(f"  Risk-population correlation: {correlation:.3f}")
        
        if correlation > 0.3:
            print("  ⚠️  High-risk areas have high population - priority for evacuation")
        elif correlation < -0.3:
            print("  ✅ High-risk areas have low population - manageable evacuation")
        else:
            print("  ℹ️  Mixed risk-population distribution")
    
    # Emergency resource allocation
    print(f"\\nEmergency Resource Allocation:")
    
    # Calculate resource needs per zone
    total_vulnerable = sum(
        cell.properties.get('elderly_population', 0) + 
        cell.properties.get('disabled_population', 0)
        for cell in grid.cells
    )
    
    total_vehicles_available = sum(
        int(cell.properties.get('population', 0) * cell.properties.get('vehicle_ownership', 0))
        for cell in grid.cells
    )
    
    print(f"  Vulnerable population: {total_vulnerable:,}")
    print(f"  Available vehicles: {total_vehicles_available:,}")
    print(f"  Vehicle deficit: {max(0, evac_analysis['estimated_vehicles_needed'] - total_vehicles_available):,}")
    
    # Shelter capacity planning
    safe_zones = [cell for cell in grid.cells if cell.properties['flood_risk'] < 0.3]
    shelter_capacity = sum(cell.properties['population'] for cell in safe_zones) * 1.5  # 150% capacity
    
    print(f"  Safe zones available: {len(safe_zones)}")
    print(f"  Estimated shelter capacity: {int(shelter_capacity):,}")
    print(f"  Shelter adequacy: {'✅ Adequate' if shelter_capacity >= evacuation_analysis['total_affected_population'] else '⚠️ Insufficient'}")
    
    print("\\nDisaster response system example completed successfully\\n")


def example_performance_optimization():
    """
    Example: H3 performance optimization and benchmarking.
    
    Demonstrates performance optimization techniques for large-scale
    H3 spatial analysis applications.
    """
    print("H3 Performance Optimization Example")
    print("=" * 40)
    
    # Performance benchmarking
    optimizer = H3PerformanceOptimizer()
    
    # Create test coordinates for benchmarking
    test_coordinates = [
        (37.7749, -122.4194),  # San Francisco
        (40.7128, -74.0060),   # New York
        (34.0522, -118.2437),  # Los Angeles
        (41.8781, -87.6298),   # Chicago
        (29.7604, -95.3698),   # Houston
        (33.4484, -112.0740),  # Phoenix
        (39.9526, -75.1652),   # Philadelphia
        (32.7767, -96.7970),   # Dallas
    ]
    
    print(f"Benchmarking H3 operations with {len(test_coordinates)} test coordinates...")
    
    # Benchmark H3 operations
    benchmark_results = optimizer.benchmark_h3_operations(
        test_coordinates, 
        resolutions=[6, 7, 8, 9, 10]
    )
    
    if 'error' not in benchmark_results:
        print(f"\\nBenchmark Results:")
        
        bench_data = benchmark_results['benchmark_results']
        
        if 'coordinate_conversion' in bench_data:
            coord_bench = bench_data['coordinate_conversion']
            print(f"  Coordinate Conversion:")
            print(f"    Average time: {coord_bench['avg_time_ms']:.3f} ms")
            print(f"    Operations/second: {coord_bench['operations_per_second']:.0f}")
        
        if 'neighbor_operations' in bench_data:
            neighbor_bench = bench_data['neighbor_operations']
            print(f"  Neighbor Operations:")
            print(f"    Average time: {neighbor_bench['avg_time_ms']:.3f} ms")
            print(f"    Operations/second: {neighbor_bench['operations_per_second']:.0f}")
        
        if 'distance_calculations' in bench_data:
            distance_bench = bench_data['distance_calculations']
            print(f"  Distance Calculations:")
            print(f"    Average time: {distance_bench['avg_time_ms']:.3f} ms")
            print(f"    Operations/second: {distance_bench['operations_per_second']:.0f}")
        
        # Memory usage analysis
        if 'memory_usage' in bench_data:
            memory = bench_data['memory_usage']
            print(f"  Memory Usage:")
            print(f"    Single cell: {memory['single_cell_bytes']} bytes")
            print(f"    Neighbor storage: {memory['neighbor_storage_bytes']} bytes")
            print(f"    Cells per MB: ~{memory['estimated_cells_per_mb']:,}")
    
    # Resolution optimization for different scenarios
    print(f"\\nResolution Optimization Recommendations:")
    
    scenarios = [
        {'name': 'City-wide Analysis', 'area_km2': 600, 'analysis_type': 'general'},
        {'name': 'ML Demand Forecasting', 'area_km2': 200, 'analysis_type': 'ml', 'target_cells': 5000},
        {'name': 'Real-time Visualization', 'area_km2': 100, 'analysis_type': 'visualization'},
        {'name': 'Routing Optimization', 'area_km2': 50, 'analysis_type': 'routing'},
        {'name': 'Neighborhood Analysis', 'area_km2': 10, 'analysis_type': 'general'}
    ]
    
    for scenario in scenarios:
        recommendation = optimizer.optimize_grid_resolution(**{k: v for k, v in scenario.items() if k != 'name'})
        
        print(f"  {scenario['name']}:")
        print(f"    Area: {scenario['area_km2']} km²")
        print(f"    Recommended resolution: {recommendation['recommended_resolution']}")
        print(f"    Estimated cells: {recommendation['estimated_cells']:,}")
        
        # Show top alternatives
        alternatives = recommendation['all_recommendations'][:3]
        print(f"    Alternatives: {[alt['resolution'] for alt in alternatives]}")
    
    # Large-scale performance analysis
    print(f"\\nLarge-scale Performance Analysis:")
    
    # Simulate large-scale grid
    large_area_km2 = 10000  # Large metropolitan area
    large_scale_rec = optimizer.optimize_grid_resolution(large_area_km2, analysis_type='ml')
    
    estimated_cells = large_scale_rec['estimated_cells']
    print(f"  Large area: {large_area_km2:,} km²")
    print(f"  Recommended resolution: {large_scale_rec['recommended_resolution']}")
    print(f"  Estimated cells: {estimated_cells:,}")
    
    # Performance projections
    if 'benchmark_results' in benchmark_results and 'coordinate_conversion' in benchmark_results['benchmark_results']:
        coord_ops_per_sec = benchmark_results['benchmark_results']['coordinate_conversion']['operations_per_second']
        
        if coord_ops_per_sec > 0:
            time_to_process = estimated_cells / coord_ops_per_sec
            print(f"  Estimated processing time: {time_to_process:.1f} seconds")
            
            if time_to_process > 60:
                print(f"  ⚠️  Consider parallel processing or coarser resolution")
            else:
                print(f"  ✅ Processing time acceptable for real-time applications")
    
    # Memory requirements
    if 'benchmark_results' in benchmark_results and 'memory_usage' in benchmark_results['benchmark_results']:
        memory_usage = benchmark_results['benchmark_results']['memory_usage']
        cells_per_mb = memory_usage['estimated_cells_per_mb']
        
        if cells_per_mb > 0:
            estimated_memory_mb = estimated_cells / cells_per_mb
            print(f"  Estimated memory: {estimated_memory_mb:.1f} MB")
            
            if estimated_memory_mb > 1000:  # > 1GB
                print(f"  ⚠️  High memory usage - consider data streaming or chunking")
            else:
                print(f"  ✅ Memory usage manageable")
    
    # Optimization recommendations
    print(f"\\nOptimization Recommendations:")
    print(f"  • Use resolution 8-10 for ML applications")
    print(f"  • Use resolution 6-8 for visualization")
    print(f"  • Use resolution 9-12 for routing")
    print(f"  • Consider parallel processing for >100k cells")
    print(f"  • Use data streaming for >1M cells")
    print(f"  • Cache frequently accessed neighbor relationships")
    
    print("\\nPerformance optimization example completed successfully\\n")


def example_integrated_smart_city():
    """
    Example: Integrated smart city application using all H3 capabilities.
    
    Demonstrates comprehensive H3 usage combining ML, disaster response,
    and performance optimization for smart city management.
    """
    print("H3 Integrated Smart City Example")
    print("=" * 40)
    
    # Create comprehensive smart city grid
    grid = H3Grid()
    
    # Define city districts with different characteristics
    city_districts = [
        {'name': 'Downtown', 'coords': (37.7749, -122.4194), 'type': 'business'},
        {'name': 'Residential North', 'coords': (37.7849, -122.4094), 'type': 'residential'},
        {'name': 'Industrial', 'coords': (37.7649, -122.4294), 'type': 'industrial'},
        {'name': 'Waterfront', 'coords': (37.7949, -122.3994), 'type': 'mixed'},
        {'name': 'Suburbs', 'coords': (37.7549, -122.4394), 'type': 'suburban'},
        {'name': 'Tech Hub', 'coords': (37.7449, -122.4494), 'type': 'business'},
        {'name': 'University', 'coords': (37.7349, -122.4594), 'type': 'institutional'},
        {'name': 'Airport', 'coords': (37.8049, -122.4194), 'type': 'transport'},
    ]
    
    # Create cells with comprehensive smart city data
    for i, district in enumerate(city_districts):
        cell = H3Cell.from_coordinates(district['coords'][0], district['coords'][1], 9)
        
        # Base characteristics by district type
        if district['type'] == 'business':
            base_demand = 200
            population = 800
            flood_risk = 0.4
            air_quality = 0.6
        elif district['type'] == 'residential':
            base_demand = 80
            population = 2000
            flood_risk = 0.3
            air_quality = 0.8
        elif district['type'] == 'industrial':
            base_demand = 150
            population = 500
            flood_risk = 0.6
            air_quality = 0.4
        elif district['type'] == 'mixed':
            base_demand = 120
            population = 1200
            flood_risk = 0.7  # Waterfront
            air_quality = 0.7
        elif district['type'] == 'suburban':
            base_demand = 60
            population = 1500
            flood_risk = 0.2
            air_quality = 0.9
        elif district['type'] == 'institutional':
            base_demand = 100
            population = 800
            flood_risk = 0.25
            air_quality = 0.85
        else:  # transport
            base_demand = 300
            population = 200
            flood_risk = 0.5
            air_quality = 0.5
        
        # Add temporal variation
        current_hour = datetime.now().hour
        if district['type'] in ['business', 'institutional'] and 9 <= current_hour <= 17:
            demand_multiplier = 1.5
        elif district['type'] == 'residential' and (7 <= current_hour <= 9 or 17 <= current_hour <= 19):
            demand_multiplier = 1.3
        else:
            demand_multiplier = 1.0
        
        cell.properties.update({
            # Transportation & Mobility
            'ride_demand': int(base_demand * demand_multiplier),
            'driver_supply': int(base_demand * demand_multiplier * 0.8),
            'public_transport_usage': random.randint(50, 200),
            'traffic_congestion': random.uniform(0.2, 0.8),
            'parking_availability': random.uniform(0.1, 0.9),
            
            # Demographics & Social
            'population': population,
            'population_density': population / 0.1,  # per km²
            'elderly_population': int(population * random.uniform(0.1, 0.2)),
            'income_level': random.uniform(30000, 120000),
            'education_level': random.uniform(0.6, 0.95),
            
            # Infrastructure & Services
            'infrastructure_quality': random.uniform(0.6, 0.95),
            'internet_coverage': random.uniform(0.8, 0.99),
            'healthcare_access': random.uniform(0.5, 0.9),
            'emergency_response_time': random.uniform(3, 15),  # minutes
            
            # Environment & Safety
            'flood_risk': flood_risk,
            'air_quality_index': air_quality,
            'noise_level': random.uniform(0.3, 0.8),
            'crime_rate': random.uniform(0.1, 0.6),
            'green_space_ratio': random.uniform(0.1, 0.4),
            
            # Energy & Utilities
            'energy_consumption': random.uniform(50, 200),  # kWh per capita
            'renewable_energy_ratio': random.uniform(0.2, 0.8),
            'water_usage': random.uniform(100, 300),  # liters per capita
            'waste_generation': random.uniform(1, 5),  # kg per capita
            
            # Economic
            'business_density': random.uniform(0.1, 0.8),
            'employment_rate': random.uniform(0.7, 0.95),
            'property_value': random.uniform(300000, 1500000),
            'retail_activity': random.uniform(0.2, 0.9),
            
            # Temporal
            'timestamp': datetime.now().isoformat(),
            'district_name': district['name'],
            'district_type': district['type'],
            
            # Baseline values for change detection
            'baseline_air_quality': air_quality,
            'baseline_traffic': 0.5,
            'baseline_energy': 100
        })
        
        grid.add_cell(cell)
    
    print(f"Created smart city grid with {len(grid.cells)} districts")
    
    # 1. ML-based Demand Forecasting
    print(f"\\n1. ML-based Transportation Demand Forecasting")
    print("-" * 50)
    
    ml_engine = H3MLFeatureEngine(grid)
    demand_features = ml_engine.create_demand_forecasting_features('ride_demand')
    
    print(f"Generated ML features for {len(demand_features['features'])} districts")
    
    # Analyze feature correlations
    if demand_features['features'] and NUMPY_AVAILABLE:
        features_data = demand_features['features']
        
        # Calculate correlation between demand and key urban factors
        demands = [f['demand_value'] for f in features_data]
        populations = [f.get('neighbor_avg', 0) for f in features_data]  # Using neighbor avg as proxy
        
        if len(demands) > 1 and len(populations) > 1:
            demand_pop_corr = np.corrcoef(demands, populations)[0, 1]
            print(f"Demand-Population correlation: {demand_pop_corr:.3f}")
    
    # 2. Disaster Response & Resilience
    print(f"\\n2. Disaster Response & Urban Resilience")
    print("-" * 50)
    
    disaster_analyzer = H3DisasterResponse(grid)
    
    # Flood risk analysis
    evacuation_zones = disaster_analyzer.analyze_evacuation_zones(
        'flood_risk', 'population', evacuation_radius_km=2.0
    )
    
    print(f"Flood risk analysis:")
    print(f"  High-risk districts: {len(evacuation_zones['high_risk_zones'])}")
    print(f"  Population at risk: {evacuation_zones['total_affected_population']:,}")
    
    # Environmental monitoring
    env_changes = disaster_analyzer.monitor_environmental_changes(
        'baseline_air_quality', 'air_quality_index', change_threshold=0.1
    )
    
    print(f"Environmental monitoring:")
    print(f"  Air quality changes: {len(env_changes['significant_changes'])}")
    
    # 3. Spatial Analytics
    print(f"\\n3. Spatial Analytics & Pattern Detection")
    print("-" * 50)
    
    spatial_analyzer = H3SpatialAnalyzer(grid)
    
    # Analyze spatial patterns
    crime_hotspots = spatial_analyzer.detect_hotspots('crime_rate', method='getis_ord')
    traffic_autocorr = spatial_analyzer.analyze_spatial_autocorrelation('traffic_congestion')
    
    print(f"Crime hotspots detected: {len(crime_hotspots.get('hotspots', []))}")
    print(f"Traffic congestion autocorrelation: {traffic_autocorr.get('morans_i', 0):.3f}")
    
    # Density analysis
    density_analyzer = H3DensityAnalyzer(grid)
    pop_density = density_analyzer.calculate_kernel_density('population', bandwidth_rings=2)
    
    print(f"Population density analysis:")
    density_stats = pop_density['statistics']
    print(f"  Peak density: {density_stats['max_density']:.0f}")
    print(f"  Average density: {density_stats['mean_density']:.0f}")
    
    # 4. Performance Optimization
    print(f"\\n4. Performance Optimization")
    print("-" * 50)
    
    optimizer = H3PerformanceOptimizer()
    
    # Get coordinates for benchmarking
    coords = []
    for cell in grid.cells:
        try:
            import h3
            if h3:
                lat, lng = h3.cell_to_latlng(cell.index)
                coords.append((lat, lng))
        except:
            pass
    
    if coords:
        benchmark = optimizer.benchmark_h3_operations(coords[:5])  # Limit for demo
        
        if 'error' not in benchmark:
            bench_data = benchmark['benchmark_results']
            if 'coordinate_conversion' in bench_data:
                ops_per_sec = bench_data['coordinate_conversion']['operations_per_second']
                print(f"H3 operations performance: {ops_per_sec:.0f} ops/sec")
    
    # Resolution optimization for different city applications
    city_area = len(grid.cells) * 0.1  # Rough area estimate
    
    applications = [
        ('Real-time Traffic', 'visualization'),
        ('Demand Forecasting', 'ml'),
        ('Emergency Routing', 'routing')
    ]
    
    for app_name, app_type in applications:
        rec = optimizer.optimize_grid_resolution(city_area, analysis_type=app_type)
        print(f"{app_name}: Resolution {rec['recommended_resolution']} ({rec['estimated_cells']} cells)")
    
    # 5. Integrated City Dashboard Metrics
    print(f"\\n5. Smart City Dashboard Metrics")
    print("-" * 50)
    
    # Calculate city-wide KPIs
    total_population = sum(cell.properties['population'] for cell in grid.cells)
    avg_air_quality = sum(cell.properties['air_quality_index'] for cell in grid.cells) / len(grid.cells)
    avg_traffic = sum(cell.properties['traffic_congestion'] for cell in grid.cells) / len(grid.cells)
    total_energy = sum(cell.properties['energy_consumption'] for cell in grid.cells)
    avg_response_time = sum(cell.properties['emergency_response_time'] for cell in grid.cells) / len(grid.cells)
    
    print(f"City Overview:")
    print(f"  Total Population: {total_population:,}")
    print(f"  Average Air Quality: {avg_air_quality:.2f} (0-1 scale)")
    print(f"  Average Traffic Congestion: {avg_traffic:.2f} (0-1 scale)")
    print(f"  Total Energy Consumption: {total_energy:.0f} kWh")
    print(f"  Average Emergency Response: {avg_response_time:.1f} minutes")
    
    # District rankings
    districts_by_livability = []
    for cell in grid.cells:
        props = cell.properties
        
        # Calculate livability score
        livability = (
            props['air_quality_index'] * 0.25 +
            (1 - props['crime_rate']) * 0.25 +
            props['green_space_ratio'] * 0.2 +
            (1 - props['traffic_congestion']) * 0.15 +
            props['healthcare_access'] * 0.15
        )
        
        districts_by_livability.append({
            'name': props['district_name'],
            'livability': livability,
            'population': props['population']
        })
    
    districts_by_livability.sort(key=lambda x: x['livability'], reverse=True)
    
    print(f"\\nTop 3 Most Livable Districts:")
    for i, district in enumerate(districts_by_livability[:3]):
        print(f"  {i+1}. {district['name']}: {district['livability']:.3f}")
    
    # Sustainability metrics
    avg_renewable = sum(cell.properties['renewable_energy_ratio'] for cell in grid.cells) / len(grid.cells)
    total_waste = sum(cell.properties['waste_generation'] for cell in grid.cells)
    
    print(f"\\nSustainability Metrics:")
    print(f"  Renewable Energy Ratio: {avg_renewable:.2f}")
    print(f"  Total Waste Generation: {total_waste:.1f} kg/capita")
    
    # Recommendations
    print(f"\\nSmart City Recommendations:")
    
    # Traffic optimization
    high_traffic_districts = [cell.properties['district_name'] for cell in grid.cells 
                            if cell.properties['traffic_congestion'] > 0.6]
    if high_traffic_districts:
        print(f"  🚦 Optimize traffic in: {', '.join(high_traffic_districts)}")
    
    # Air quality improvement
    low_air_quality = [cell.properties['district_name'] for cell in grid.cells 
                      if cell.properties['air_quality_index'] < 0.6]
    if low_air_quality:
        print(f"  🌱 Improve air quality in: {', '.join(low_air_quality)}")
    
    # Emergency response
    slow_response = [cell.properties['district_name'] for cell in grid.cells 
                    if cell.properties['emergency_response_time'] > 10]
    if slow_response:
        print(f"  🚑 Improve emergency response in: {', '.join(slow_response)}")
    
    print("\\nIntegrated smart city example completed successfully!")
    print("=" * 40)


def main():
    """Run all advanced H3 application examples."""
    print("GEO-INFER-SPACE H3 Advanced Applications")
    print("=" * 60)
    print()
    
    try:
        example_demand_forecasting_ml()
    except Exception as e:
        print(f"Demand forecasting ML example failed: {e}\\n")
    
    try:
        example_disaster_response_system()
    except Exception as e:
        print(f"Disaster response example failed: {e}\\n")
    
    try:
        example_performance_optimization()
    except Exception as e:
        print(f"Performance optimization example failed: {e}\\n")
    
    try:
        example_integrated_smart_city()
    except Exception as e:
        print(f"Integrated smart city example failed: {e}\\n")
    
    print("All H3 advanced application examples completed!")


if __name__ == "__main__":
    main()
