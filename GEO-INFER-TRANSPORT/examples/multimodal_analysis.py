#!/usr/bin/env python3
"""
GEO-INFER-TRANSPORT Example: Multi-Modal Transportation Analysis

This example demonstrates comprehensive transportation network analysis
including routing, traffic analysis, accessibility, and transit optimization.
"""

from geo_infer_transport import (
    TransportNetwork,
    RoutingEngine,
    TrafficAnalyzer,
    AccessibilityAnalyzer,
    TransitOptimizer
)


def main():
    print("=" * 60)
    print("GEO-INFER-TRANSPORT: Multi-Modal Transport Analysis")
    print("=" * 60)
    
    # 1. Build Transport Network
    print("\n1. Building Transport Network...")
    network = TransportNetwork(
        modes=['road', 'transit', 'bicycle', 'pedestrian'],
        data_format='osm'
    )
    
    # Add nodes and edges
    nodes = [
        {'id': 'A', 'lat': 34.05, 'lon': -118.25, 'type': 'intersection'},
        {'id': 'B', 'lat': 34.06, 'lon': -118.24, 'type': 'intersection'},
        {'id': 'C', 'lat': 34.07, 'lon': -118.23, 'type': 'transit_stop'},
        {'id': 'D', 'lat': 34.05, 'lon': -118.22, 'type': 'intersection'},
        {'id': 'E', 'lat': 34.04, 'lon': -118.23, 'type': 'transit_stop'},
    ]
    
    edges = [
        {'from': 'A', 'to': 'B', 'mode': 'road', 'distance_km': 1.5, 'speed_limit': 50},
        {'from': 'B', 'to': 'C', 'mode': 'road', 'distance_km': 1.2, 'speed_limit': 40},
        {'from': 'C', 'to': 'D', 'mode': 'road', 'distance_km': 1.0, 'speed_limit': 40},
        {'from': 'A', 'to': 'E', 'mode': 'road', 'distance_km': 1.3, 'speed_limit': 50},
        {'from': 'E', 'to': 'D', 'mode': 'road', 'distance_km': 1.1, 'speed_limit': 40},
        {'from': 'C', 'to': 'E', 'mode': 'transit', 'distance_km': 2.0, 'speed_limit': 30},
    ]
    
    for node in nodes:
        network.add_node(**node)
    for edge in edges:
        network.add_edge(**edge)
    
    stats = network.get_network_statistics()
    print(f"   Network: {stats['node_count']} nodes, {stats['edge_count']} edges")
    print(f"   Modes: {', '.join(stats.get('modes', ['road']))}")
    
    # 2. Route Optimization
    print("\n2. Computing Optimal Routes...")
    router = RoutingEngine(
        algorithms=['dijkstra', 'astar', 'contraction_hierarchies'],
        default_algorithm='astar'
    )
    
    route = router.find_route(
        network=network,
        origin='A',
        destination='D',
        mode='road',
        optimization='time'
    )
    
    print(f"   Route: {' -> '.join(route['path'])}")
    print(f"   Distance: {route['total_distance_km']:.2f} km")
    print(f"   Time: {route['total_time_minutes']:.1f} minutes")
    
    # Multi-modal routing
    multimodal_route = router.find_multimodal_route(
        network=network,
        origin='A',
        destination='D',
        allowed_modes=['road', 'transit'],
        max_transfers=2
    )
    
    print(f"   Multi-modal route: {len(multimodal_route['segments'])} segments")
    
    # 3. Traffic Analysis
    print("\n3. Analyzing Traffic Patterns...")
    traffic = TrafficAnalyzer(
        models=['bpr', 'gravity', 'four_step'],
        time_periods=['am_peak', 'pm_peak', 'off_peak']
    )
    
    # Generate OD matrix
    od_matrix = traffic.generate_od_matrix(
        zones=['zone_1', 'zone_2', 'zone_3'],
        trip_generation={'zone_1': 1000, 'zone_2': 1500, 'zone_3': 800},
        attraction={'zone_1': 500, 'zone_2': 1200, 'zone_3': 1600}
    )
    
    print(f"   OD Matrix: {od_matrix.get('zones', 0)}x{od_matrix.get('zones', 0)}")
    print(f"   Total trips: {od_matrix.get('total_trips', 0):,}")
    
    # Congestion analysis
    congestion = traffic.analyze_congestion(
        network=network,
        demand=od_matrix,
        time_period='am_peak'
    )
    
    print(f"   Congested links: {congestion.get('congested_links', 0)}")
    print(f"   V/C ratio > 0.8: {congestion.get('vc_above_threshold', 0)} links")
    
    # 4. Accessibility Analysis
    print("\n4. Computing Accessibility Metrics...")
    accessibility = AccessibilityAnalyzer(
        metrics=['cumulative', 'gravity', 'time_threshold'],
        modes=['car', 'transit', 'walk']
    )
    
    # Generate isochrones
    isochrones = accessibility.calculate_isochrones(
        network=network,
        origin='A',
        time_thresholds=[10, 20, 30],  # minutes
        mode='road'
    )
    
    print(f"   Isochrones computed for {len(isochrones)} time thresholds")
    for iso in isochrones:
        print(f"   - {iso['time_minutes']}min: {iso['reachable_nodes']} nodes")
    
    # Equity analysis
    equity = accessibility.analyze_equity(
        network=network,
        population_data=[
            {'zone': 'zone_1', 'population': 10000, 'income_median': 50000},
            {'zone': 'zone_2', 'population': 15000, 'income_median': 35000},
            {'zone': 'zone_3', 'population': 8000, 'income_median': 75000},
        ],
        opportunity_locations=[
            {'type': 'employment', 'location': 'B', 'jobs': 5000},
            {'type': 'healthcare', 'location': 'C', 'capacity': 200},
        ]
    )
    
    print(f"   Gini coefficient: {equity.get('gini', 0):.3f}")
    print(f"   Equity score: {equity.get('equity_score', 0):.2f}")
    
    # 5. Transit Optimization
    print("\n5. Optimizing Transit Network...")
    transit = TransitOptimizer(
        optimization_objectives=['coverage', 'ridership', 'efficiency'],
        constraints={'budget': 10000000, 'fleet_size': 50}
    )
    
    # Optimize frequency
    frequency_opt = transit.optimize_frequency(
        routes=[
            {'id': 'route_1', 'stops': ['A', 'C', 'E'], 'demand': 500},
            {'id': 'route_2', 'stops': ['B', 'C', 'D'], 'demand': 800},
        ],
        available_vehicles=20,
        service_hours=16
    )
    
    print(f"   Routes optimized: {len(frequency_opt.get('routes', []))}")
    for route_opt in frequency_opt.get('routes', []):
        print(f"   - {route_opt['id']}: {route_opt['frequency_min']} min headway")
    
    # Coverage analysis
    coverage = transit.calculate_coverage(
        network=network,
        transit_stops=['C', 'E'],
        walk_distance_meters=400
    )
    
    print(f"   Population covered: {coverage.get('population_covered_pct', 0):.1f}%")
    print(f"   Area covered: {coverage.get('area_covered_km2', 0):.2f} km²")
    
    print("\n" + "=" * 60)
    print("Transport Analysis Complete!")
    print("=" * 60)
    
    # Summary
    print("\nKey Findings:")
    print(f"  - Network: {stats['node_count']} nodes, {stats['edge_count']} edges")
    print(f"  - Best route A→D: {route['total_time_minutes']:.1f} min")
    print(f"  - Transit coverage: {coverage.get('population_covered_pct', 0):.1f}%")
    print(f"  - Accessibility equity: {equity.get('equity_score', 0):.2f}")


if __name__ == "__main__":
    main()
