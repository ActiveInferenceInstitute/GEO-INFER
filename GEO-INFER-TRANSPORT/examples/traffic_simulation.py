#!/usr/bin/env python3
"""
GEO-INFER-TRANSPORT Example: Traffic Simulation and Demand Modeling

This example demonstrates traffic simulation with demand modeling,
signal optimization, and congestion analysis.
"""

from geo_infer_transport import (
    TrafficSimulator,
    DemandModel,
    SignalOptimizer,
    EmissionsCalculator,
    ModeChoiceModel
)


def main():
    print("=" * 60)
    print("GEO-INFER-TRANSPORT: Traffic Simulation & Demand Modeling")
    print("=" * 60)
    
    # 1. Define Transportation Zones
    print("\n1. Setting Up Transportation Analysis Zones...")
    
    taz_data = [
        {'id': 'TAZ_001', 'name': 'Downtown', 'population': 50000, 'employment': 80000},
        {'id': 'TAZ_002', 'name': 'Suburban East', 'population': 75000, 'employment': 25000},
        {'id': 'TAZ_003', 'name': 'Industrial North', 'population': 20000, 'employment': 45000},
        {'id': 'TAZ_004', 'name': 'Residential South', 'population': 100000, 'employment': 15000},
        {'id': 'TAZ_005', 'name': 'Commercial West', 'population': 40000, 'employment': 35000},
    ]
    
    print(f"   TAZs defined: {len(taz_data)}")
    total_pop = sum(t['population'] for t in taz_data)
    total_emp = sum(t['employment'] for t in taz_data)
    print(f"   Total population: {total_pop:,}")
    print(f"   Total employment: {total_emp:,}")
    
    # 2. Trip Generation
    print("\n2. Running Four-Step Demand Model...")
    demand = DemandModel(
        model_type='four_step',
        trip_purposes=['home_work', 'home_other', 'non_home_based']
    )
    
    # Trip generation
    trip_generation = demand.generate_trips(
        zones=taz_data,
        generation_rates={
            'home_work': 0.8,  # trips per employee
            'home_other': 1.2,  # trips per person
            'non_home_based': 0.3  # trips per employee
        }
    )
    
    print(f"   Total trips generated: {trip_generation.get('total_trips', 0):,}")
    print(f"   Productions: {trip_generation.get('total_productions', 0):,}")
    print(f"   Attractions: {trip_generation.get('total_attractions', 0):,}")
    
    # Trip distribution
    od_matrix = demand.distribute_trips(
        trip_generation=trip_generation,
        impedance_function='gravity',
        friction_factor=2.0
    )
    
    print(f"   OD pairs: {od_matrix.get('od_pairs', 0)}")
    
    # 3. Mode Choice Modeling
    print("\n3. Running Mode Choice Model...")
    mode_choice = ModeChoiceModel(
        modes=['car', 'transit', 'bicycle', 'walk'],
        model_type='multinomial_logit'
    )
    
    mode_split = mode_choice.calculate_mode_split(
        od_matrix=od_matrix,
        utility_parameters={
            'car': {'time_coef': -0.02, 'cost_coef': -0.05, 'constant': 0},
            'transit': {'time_coef': -0.03, 'cost_coef': -0.03, 'constant': -0.5},
            'bicycle': {'time_coef': -0.04, 'cost_coef': 0, 'constant': -1.0},
            'walk': {'time_coef': -0.05, 'cost_coef': 0, 'constant': -1.5}
        }
    )
    
    print("   Mode split:")
    for mode, share in mode_split.get('shares', {}).items():
        print(f"   - {mode.title()}: {share*100:.1f}%")
    
    # 4. Traffic Assignment
    print("\n4. Running Traffic Assignment...")
    simulator = TrafficSimulator(
        assignment_method='user_equilibrium',
        time_periods=['am_peak', 'pm_peak', 'off_peak']
    )
    
    assignment = simulator.assign_traffic(
        od_matrix=od_matrix,
        mode_split=mode_split,
        network_capacity={
            'arterial_lanes': 4,
            'collector_lanes': 2,
            'local_lanes': 1
        },
        vdf_parameters={
            'alpha': 0.15,
            'beta': 4.0
        }
    )
    
    print(f"   Vehicles assigned: {assignment.get('total_vehicles', 0):,}")
    print(f"   VHT (Vehicle Hours Traveled): {assignment.get('vht', 0):,.0f}")
    print(f"   VMT (Vehicle Miles Traveled): {assignment.get('vmt', 0):,.0f}")
    
    # 5. Congestion Analysis
    print("\n5. Analyzing Congestion...")
    congestion = simulator.analyze_congestion(
        assignment=assignment,
        vc_threshold=0.8
    )
    
    print(f"   Congested links: {congestion.get('congested_links', 0)}")
    print(f"   Average V/C ratio: {congestion.get('avg_vc_ratio', 0):.2f}")
    print(f"   Total delay (hours): {congestion.get('total_delay_hours', 0):,.0f}")
    print(f"   Congestion cost: ${congestion.get('congestion_cost', 0):,.0f}")
    
    # 6. Signal Optimization
    print("\n6. Optimizing Traffic Signals...")
    signal_opt = SignalOptimizer(
        optimization_method='genetic_algorithm',
        objectives=['delay_minimization', 'throughput_maximization']
    )
    
    signal_plan = signal_opt.optimize(
        intersections=[
            {'id': 'INT_001', 'phases': 4, 'current_cycle': 90},
            {'id': 'INT_002', 'phases': 3, 'current_cycle': 80},
            {'id': 'INT_003', 'phases': 4, 'current_cycle': 100},
        ],
        traffic_data=assignment,
        coordination_enabled=True
    )
    
    print(f"   Intersections optimized: {signal_plan.get('intersections_optimized', 0)}")
    print(f"   Delay reduction: {signal_plan.get('delay_reduction_pct', 0):.1f}%")
    print(f"   Throughput improvement: {signal_plan.get('throughput_improvement_pct', 0):.1f}%")
    
    # 7. Emissions Calculation
    print("\n7. Calculating Emissions...")
    emissions = EmissionsCalculator(
        emission_model='moves',
        pollutants=['CO2', 'NOx', 'PM2.5', 'CO']
    )
    
    emission_results = emissions.calculate(
        assignment=assignment,
        fleet_composition={
            'passenger_car': 0.75,
            'light_truck': 0.15,
            'heavy_truck': 0.08,
            'bus': 0.02
        },
        average_speed_mph=25
    )
    
    print("   Daily emissions:")
    for pollutant, value in emission_results.get('daily_emissions', {}).items():
        unit = 'tons' if pollutant == 'CO2' else 'kg'
        print(f"   - {pollutant}: {value:,.1f} {unit}")
    
    print("\n" + "=" * 60)
    print("Traffic Simulation Complete!")
    print("=" * 60)
    
    # Summary
    print("\nKey Performance Indicators:")
    print(f"  - Total daily trips: {trip_generation.get('total_trips', 0):,}")
    print(f"  - Car mode share: {mode_split.get('shares', {}).get('car', 0)*100:.1f}%")
    print(f"  - Average V/C ratio: {congestion.get('avg_vc_ratio', 0):.2f}")
    print(f"  - Total daily CO2: {emission_results.get('daily_emissions', {}).get('CO2', 0):,.0f} tons")


if __name__ == "__main__":
    main()
