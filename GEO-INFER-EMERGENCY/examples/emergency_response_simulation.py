#!/usr/bin/env python3
"""
GEO-INFER-EMERGENCY Example: Emergency Response Simulation

This example demonstrates a complete emergency response workflow
including incident coordination, resource deployment, and evacuation planning.
"""

from geo_infer_emergency import (
    EmergencyCoordinator,
    ResourceDeployer,
    EvacuationPlanner,
    SituationalAwareness,
    SearchAndRescue
)


def main():
    print("=" * 60)
    print("GEO-INFER-EMERGENCY: Emergency Response Simulation")
    print("=" * 60)
    
    # 1. Initialize Emergency Coordinator
    print("\n1. Initializing Emergency Command Structure...")
    coordinator = EmergencyCoordinator(
        command_structure='ics',  # Incident Command System
        agencies=['fire', 'ems', 'police', 'public_works']
    )
    
    # Create an incident
    incident = coordinator.create_incident(
        incident_type='wildfire',
        severity='major',
        location={'latitude': 34.05, 'longitude': -118.25},
        affected_area_km2=50.0
    )
    
    print(f"   Incident created: {incident['id']}")
    print(f"   Type: {incident['type']}, Severity: {incident['severity']}")
    
    # 2. Build Situational Awareness
    print("\n2. Building Situational Awareness (Common Operating Picture)...")
    sa = SituationalAwareness(
        data_sources=['sensors', 'reports', 'satellite'],
        fusion_method='kalman_filter'
    )
    
    cop = sa.build_cop(
        incident_id=incident['id'],
        data_layers=['fire_perimeter', 'population', 'infrastructure', 'weather'],
        update_interval_seconds=30
    )
    
    print(f"   COP established with {len(cop.get('layers', []))} layers")
    print(f"   Threat level: {cop.get('threat_assessment', {}).get('level', 'unknown')}")
    
    # 3. Deploy Resources
    print("\n3. Deploying Emergency Resources...")
    deployer = ResourceDeployer(
        optimization_method='multi_objective',
        resource_types=['fire_engines', 'ambulances', 'helicopters', 'personnel']
    )
    
    deployment = deployer.deploy(
        incident=incident,
        available_resources={
            'fire_engines': 15,
            'ambulances': 10,
            'helicopters': 3,
            'personnel': 200
        },
        constraints={
            'max_response_time_minutes': 15,
            'resource_reserve_ratio': 0.2
        }
    )
    
    print(f"   Deployed {deployment.get('total_deployed', 0)} resource units")
    for resource, count in deployment.get('deployment', {}).items():
        print(f"   - {resource}: {count} units")
    
    # 4. Plan Evacuation
    print("\n4. Planning Evacuation...")
    evac_planner = EvacuationPlanner(
        routing_algorithm='multi_objective',
        shelter_database='regional_shelters'
    )
    
    evac_plan = evac_planner.plan(
        affected_area=incident['affected_area'],
        population_estimate=25000,
        evacuation_zones=['zone_a', 'zone_b', 'zone_c'],
        available_shelters=[
            {'id': 'shelter_1', 'capacity': 5000, 'location': {'lat': 34.1, 'lon': -118.0}},
            {'id': 'shelter_2', 'capacity': 8000, 'location': {'lat': 34.0, 'lon': -118.3}},
            {'id': 'shelter_3', 'capacity': 10000, 'location': {'lat': 33.95, 'lon': -118.1}}
        ]
    )
    
    print(f"   Evacuation zones: {len(evac_plan.get('zones', []))}")
    print(f"   Routes planned: {len(evac_plan.get('routes', {}).get('routes', []))}")
    print(f"   Estimated clearance time: {evac_plan.get('estimated_clearance_hours', 0):.1f} hours")
    
    # 5. Search and Rescue Operations
    print("\n5. Planning Search and Rescue Operations...")
    sar = SearchAndRescue(
        search_patterns=['parallel', 'expanding_square', 'sector'],
        team_types=['ground', 'canine', 'aerial']
    )
    
    sar_plan = sar.plan_mission(
        search_area={
            'center': {'latitude': 34.05, 'longitude': -118.25},
            'radius_km': 5.0
        },
        priority_zones=['residential', 'schools', 'hospitals'],
        available_teams={
            'ground': 10,
            'canine': 4,
            'aerial': 2
        },
        time_constraint_hours=24
    )
    
    print(f"   Search sectors: {len(sar_plan.get('sectors', []))}")
    print(f"   Teams assigned: {sar_plan.get('teams_assigned', 0)}")
    print(f"   Coverage probability: {sar_plan.get('pod', 0):.1%}")
    
    # 6. Monitor and coordinate
    print("\n6. Coordinating Multi-Agency Response...")
    coordination = coordinator.coordinate_response(
        incident_id=incident['id'],
        agencies=['fire', 'ems', 'police'],
        tasks={
            'fire': ['perimeter_control', 'suppression'],
            'ems': ['medical_staging', 'evacuation_support'],
            'police': ['traffic_control', 'security']
        }
    )
    
    print(f"   Agencies coordinated: {len(coordination.get('agencies', []))}")
    print(f"   Active tasks: {coordination.get('active_tasks', 0)}")
    
    print("\n" + "=" * 60)
    print("Emergency Response Simulation Complete!")
    print("=" * 60)
    
    # Summary
    print("\nSummary:")
    print(f"  - Incident: {incident['type']} ({incident['severity']})")
    print(f"  - Resources deployed: {deployment.get('total_deployed', 0)} units")
    print(f"  - Population to evacuate: 25,000")
    print(f"  - SAR coverage: {sar_plan.get('pod', 0):.1%}")


if __name__ == "__main__":
    main()
