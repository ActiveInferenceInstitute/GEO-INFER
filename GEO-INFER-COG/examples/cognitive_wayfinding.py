#!/usr/bin/env python3
"""
GEO-INFER-COG Example: Cognitive Mapping and Wayfinding

This example demonstrates cognitive mapping, spatial memory,
wayfinding simulation, and human spatial cognition modeling.
"""

from geo_infer_cog import (
    CognitiveProcessingEngine,
    SpatialMemoryModel,
    WayfindingSimulator,
    CognitiveMapBuilder,
    UserCognitiveProfile
)


def main():
    print("=" * 60)
    print("GEO-INFER-COG: Cognitive Mapping & Wayfinding")
    print("=" * 60)
    
    # 1. Create User Cognitive Profile
    print("\n1. Setting Up User Cognitive Profile...")
    
    user_profile = UserCognitiveProfile(
        user_id='user_001',
        spatial_ability='medium',
        navigation_strategy='route',  # vs 'survey'
        working_memory_capacity=7,
        familiarity_level='novice'
    )
    
    print(f"   User ID: {user_profile.user_id}")
    print(f"   Spatial ability: {user_profile.spatial_ability}")
    print(f"   Navigation strategy: {user_profile.navigation_strategy}")
    
    # 2. Initialize Cognitive Engine
    print("\n2. Initializing Cognitive Processing Engine...")
    
    engine = CognitiveProcessingEngine(
        cognitive_framework='bayesian_attention',
        spatial_resolution='adaptive',
        temporal_modeling='working_memory',
        uncertainty_handling='probabilistic'
    )
    
    print(f"   Framework: {engine.cognitive_framework}")
    print(f"   Resolution: {engine.spatial_resolution}")
    
    # 3. Build Cognitive Map
    print("\n3. Building Cognitive Map from Environment...")
    
    # Define environment
    environment = {
        'landmarks': [
            {'id': 'L1', 'name': 'Clock Tower', 'x': 0, 'y': 0, 'salience': 0.9},
            {'id': 'L2', 'name': 'Park', 'x': 200, 'y': 100, 'salience': 0.7},
            {'id': 'L3', 'name': 'Library', 'x': 400, 'y': 50, 'salience': 0.8},
            {'id': 'L4', 'name': 'Mall', 'x': 300, 'y': 300, 'salience': 0.85},
            {'id': 'L5', 'name': 'Station', 'x': 500, 'y': 200, 'salience': 0.95},
        ],
        'paths': [
            {'from': 'L1', 'to': 'L2', 'distance': 224, 'turns': 1},
            {'from': 'L2', 'to': 'L3', 'distance': 206, 'turns': 0},
            {'from': 'L3', 'to': 'L5', 'distance': 180, 'turns': 1},
            {'from': 'L1', 'to': 'L4', 'distance': 424, 'turns': 2},
            {'from': 'L4', 'to': 'L5', 'distance': 224, 'turns': 1},
        ]
    }
    
    map_builder = CognitiveMapBuilder(
        encoding_method='hierarchical',
        distortion_model='regression_to_mean'
    )
    
    cognitive_map = map_builder.build(
        environment=environment,
        user_profile=user_profile,
        exposure_duration_minutes=30
    )
    
    print(f"   Landmarks encoded: {len(cognitive_map.landmarks)}")
    print(f"   Connections learned: {len(cognitive_map.connections)}")
    print(f"   Map completeness: {cognitive_map.completeness:.1%}")
    
    # 4. Simulate Spatial Memory
    print("\n4. Simulating Spatial Memory...")
    
    memory = SpatialMemoryModel(
        memory_types=['working', 'long_term', 'episodic'],
        consolidation_strategy='adaptive'
    )
    
    # Encode locations into memory
    for landmark in environment['landmarks']:
        memory.encode(
            item=landmark,
            encoding_strength=landmark['salience'],
            context={'time': 'morning', 'weather': 'sunny'}
        )
    
    # Test recall after delay
    recall_test = memory.recall_locations(
        cue={'near': 'Clock Tower'},
        delay_hours=24
    )
    
    print(f"   Locations encoded: {len(environment['landmarks'])}")
    print(f"   Recall accuracy: {recall_test.get('accuracy', 0):.1%}")
    print(f"   Mean localization error: {recall_test.get('mean_error', 0):.1f} units")
    
    # 5. Wayfinding Simulation
    print("\n5. Simulating Wayfinding Task...")
    
    wayfinder = WayfindingSimulator(
        decision_model='bounded_rationality',
        error_model='landmark_based'
    )
    
    wayfinding_result = wayfinder.simulate(
        cognitive_map=cognitive_map,
        start='L1',
        destination='L5',
        user_profile=user_profile,
        include_decision_trace=True
    )
    
    print(f"   Route taken: {' -> '.join(wayfinding_result['route'])}")
    print(f"   Distance traveled: {wayfinding_result['distance']:.0f} units")
    print(f"   Optimal distance: {wayfinding_result['optimal_distance']:.0f} units")
    print(f"   Efficiency: {wayfinding_result['efficiency']:.1%}")
    print(f"   Decision points: {len(wayfinding_result['decisions'])}")
    
    # 6. Analyze Cognitive Load
    print("\n6. Analyzing Cognitive Load...")
    
    load_analysis = engine.analyze_cognitive_load(
        task='wayfinding',
        complexity_factors={
            'route_length': wayfinding_result['distance'],
            'decision_points': len(wayfinding_result['decisions']),
            'turns': sum(1 for d in wayfinding_result['decisions'] if d.get('turn')),
            'unfamiliar_areas': 2
        },
        user_profile=user_profile
    )
    
    print(f"   Overall cognitive load: {load_analysis['overall_load']:.2f}/1.0")
    print(f"   Perceptual load: {load_analysis['perceptual_load']:.2f}")
    print(f"   Memory load: {load_analysis['memory_load']:.2f}")
    print(f"   Decision load: {load_analysis['decision_load']:.2f}")
    
    # 7. Generate Navigation Instructions
    print("\n7. Generating Cognitively-Optimized Instructions...")
    
    instructions = engine.generate_instructions(
        route=wayfinding_result['route'],
        cognitive_map=cognitive_map,
        user_profile=user_profile,
        instruction_style='landmark_based'
    )
    
    print("   Navigation instructions:")
    for i, instruction in enumerate(instructions[:3], 1):
        print(f"   {i}. {instruction}")
    
    # 8. Assess Spatial Knowledge Acquisition
    print("\n8. Assessing Spatial Knowledge...")
    
    assessment = engine.assess_spatial_knowledge(
        cognitive_map=cognitive_map,
        knowledge_types=['landmark', 'route', 'survey'],
        test_items=5
    )
    
    print("   Knowledge levels:")
    print(f"   - Landmark knowledge: {assessment['landmark_score']:.1%}")
    print(f"   - Route knowledge: {assessment['route_score']:.1%}")
    print(f"   - Survey knowledge: {assessment['survey_score']:.1%}")
    print(f"   - Overall: {assessment['overall_score']:.1%}")
    
    print("\n" + "=" * 60)
    print("Cognitive Analysis Complete!")
    print("=" * 60)
    
    # Summary
    print("\nSummary:")
    print(f"  - User profile: {user_profile.navigation_strategy} navigator")
    print(f"  - Cognitive map completeness: {cognitive_map.completeness:.1%}")
    print(f"  - Wayfinding efficiency: {wayfinding_result['efficiency']:.1%}")
    print(f"  - Cognitive load: {load_analysis['overall_load']:.2f}")


if __name__ == "__main__":
    main()
