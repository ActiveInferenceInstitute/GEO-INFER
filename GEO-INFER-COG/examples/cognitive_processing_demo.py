#!/usr/bin/env python3
"""
Cognitive Processing Demo for GEO-INFER-COG

This script demonstrates the core cognitive processing capabilities of the
GEO-INFER-COG module, including spatial perception, reasoning, memory,
and decision-making with human-like spatial cognition.

The demo shows how the cognitive engine processes spatial data through
multiple cognitive systems to provide human-centered spatial intelligence.

Usage:
    python cognitive_processing_demo.py

Requirements:
    - GEO-INFER-COG module installed
    - numpy, matplotlib for visualization
    - Sample spatial data (will be generated if not provided)
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# Add the module to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from geo_infer_cog import (
        CognitiveProcessingEngine,
        SpatialPerceptionModel,
        SpatialReasoningEngine,
        SpatialMemoryModel,
        SpatialLanguageProcessor,
        UserCognitiveProfile,
        ProfileManager,
        CognitiveMap,
        validate_spatial_data
    )
    print("✓ GEO-INFER-COG modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure GEO-INFER-COG is properly installed")
    sys.exit(1)


def create_sample_spatial_data():
    """Create sample spatial data for demonstration."""
    return {
        'type': 'FeatureCollection',
        'features': [
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-122.4194, 37.7749]  # San Francisco
                },
                'properties': {
                    'name': 'San Francisco',
                    'type': 'city',
                    'population': 883305,
                    'area_km2': 121.4
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-118.2437, 34.0522]  # Los Angeles
                },
                'properties': {
                    'name': 'Los Angeles',
                    'type': 'city',
                    'population': 3979576,
                    'area_km2': 1302.0
                }
            },
            {
                'type': 'Feature',
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[
                        [-122.5, 37.7],
                        [-122.3, 37.7],
                        [-122.3, 37.9],
                        [-122.5, 37.9],
                        [-122.5, 37.7]
                    ]]
                },
                'properties': {
                    'name': 'Bay Area Region',
                    'type': 'region',
                    'description': 'San Francisco Bay metropolitan area'
                }
            }
        ]
    }


def create_sample_user_profile():
    """Create a sample user profile for demonstration."""
    profile_manager = ProfileManager()

    # Create a moderately experienced user
    profile = profile_manager.create_profile(
        user_id="demo_user_001",
        initial_assessment={
            'spatial_expertise_score': 0.7,
            'cognitive_style': 'visualizer',
            'preferred_load_level': 'moderate'
        }
    )

    return profile


def demonstrate_cognitive_processing():
    """Demonstrate the full cognitive processing pipeline."""
    print("\n" + "="*60)
    print("COGNITIVE PROCESSING DEMONSTRATION")
    print("="*60)

    # Initialize components
    print("1. Initializing cognitive processing components...")

    cognitive_engine = CognitiveProcessingEngine(
        cognitive_framework='bayesian_attention',
        spatial_resolution='adaptive',
        uncertainty_handling='probabilistic'
    )

    perception_model = SpatialPerceptionModel(
        framework='bayesian_attention',
        resolution='adaptive'
    )

    reasoning_engine = SpatialReasoningEngine(
        reasoning_type='qualitative_spatial',
        uncertainty_method='probabilistic'
    )

    memory_model = SpatialMemoryModel(
        memory_types=['working', 'long_term', 'episodic'],
        consolidation_strategy='adaptive'
    )

    print("   ✓ Components initialized successfully")

    # Create sample data and user profile
    print("2. Preparing sample spatial data and user profile...")

    spatial_data = create_sample_spatial_data()
    user_profile = create_sample_user_profile()

    # Validate spatial data
    validation = validate_spatial_data(spatial_data)
    if validation['valid']:
        print("   ✓ Spatial data validation passed")
    else:
        print(f"   ✗ Spatial data validation failed: {validation['errors']}")
        return

    print("   ✓ Sample data and profile created")

    # Process spatial input through cognitive pipeline
    print("3. Processing spatial input through cognitive pipeline...")

    try:
        processing_result = cognitive_engine.process_spatial_input(
            spatial_data=spatial_data,
            context={'task_type': 'navigation'},
            user_profile=user_profile
        )

        print(f"   ✓ Cognitive processing completed in {processing_result['processing_time']:.3f}s")
        print(f"   ✓ Processing confidence: {processing_result['confidence_score']:.3f}")

        # Display cognitive state
        cognitive_state = processing_result['cognitive_state']
        print(f"   ✓ Cognitive load: {cognitive_state['cognitive_load']:.3f}")
        print(f"   ✓ Working memory items: {len(cognitive_state['working_memory'])}")

    except Exception as e:
        print(f"   ✗ Cognitive processing failed: {str(e)}")
        return

    # Demonstrate individual components
    print("4. Demonstrating individual cognitive components...")

    # Spatial perception
    perception_result = perception_model.process_spatial_input(
        spatial_data, {'task_type': 'analysis'}, user_profile
    )

    print(f"   ✓ Spatial perception: {len(perception_result['spatial_elements'])} elements processed")
    print(f"     - Attention concentration: {perception_result['perceptual_insights']['attention_patterns'].get('attention_concentration', 0):.3f}")

    # Spatial reasoning
    reasoning_result = reasoning_engine.reason_about_space(
        spatial_data, perception_result, cognitive_engine.state
    )

    print(f"   ✓ Spatial reasoning: {len(reasoning_result['conclusions'])} conclusions reached")
    print(f"     - Reasoning confidence: {reasoning_result['confidence_score']:.3f}")

    # Memory operations
    memory_result = memory_model.update_memory(
        perception_result, reasoning_result, cognitive_engine.state
    )

    print(f"   ✓ Memory operations: {memory_result['items_stored']} items stored")
    print(f"     - Consolidated: {memory_result['items_consolidated']} items")

    # Display performance metrics
    print("5. Performance metrics summary...")
    metrics = processing_result['performance_metrics']
    print(f"   ✓ Decisions made: {metrics['decisions_made']}")
    print(f"   ✓ Reasoning chains: {metrics['reasoning_chains']}")
    print(f"   ✓ Memory operations: {metrics['memory_operations']}")
    print(f"   ✓ Perception updates: {metrics['perception_updates']}")

    return processing_result


def demonstrate_spatial_language_processing():
    """Demonstrate spatial language processing capabilities."""
    print("\n" + "="*60)
    print("SPATIAL LANGUAGE PROCESSING DEMONSTRATION")
    print("="*60)

    # Initialize spatial language processor
    print("1. Initializing spatial language processor...")

    language_processor = SpatialLanguageProcessor(
        language='en',
        domain='general'
    )

    print("   ✓ Language processor initialized")

    # Sample place descriptions
    descriptions = [
        "The museum is located in downtown San Francisco, near the financial district.",
        "I need to find a coffee shop north of the park and east of Main Street.",
        "The hospital is about 2 blocks west of the university campus.",
        "Looking for restaurants in the Bay Area region, preferably near water."
    ]

    print("2. Processing place descriptions...")

    for i, description in enumerate(descriptions, 1):
        print(f"\n   Description {i}: '{description}'")

        try:
            interpretation = language_processor.process_place_description(description)

            print(f"     ✓ Interpretation confidence: {interpretation['interpretation_confidence']".3f"}")
            print(f"     ✓ Entities found: {len(interpretation['entities'])}")
            print(f"     ✓ Relations found: {len(interpretation['relations'])}")
            print(f"     ✓ Spatial concepts: {len(interpretation['spatial_concepts'])}")

            # Show extracted entities
            for entity in interpretation['entities'][:2]:  # Show first 2 entities
                print(f"       - {entity['text']} ({entity['entity_type']}, confidence: {entity['confidence']".2f"})")

            # Show geocoding results
            geocoded = [c for c in interpretation['geocoding_candidates'] if c['geocoding_success']]
            if geocoded:
                print(f"     ✓ Geocoding success: {len(geocoded)}/{len(interpretation['geocoding_candidates'])}")

        except Exception as e:
            print(f"     ✗ Processing failed: {str(e)}")

    # Display processing metrics
    metrics = language_processor.processing_metrics
    print("\n3. Language processing metrics...")
    print(f"   ✓ Entities extracted: {metrics['entities_extracted']}")
    print(f"   ✓ Relations found: {metrics['relations_found']}")
    print(f"   ✓ Descriptions processed: {metrics['descriptions_processed']}")
    print(f"   ✓ Geocoding attempts: {metrics['geocoding_attempts']}")
    print(f"   ✓ Successful geocoding: {metrics['successful_geocoding']}")


def demonstrate_cognitive_map_creation():
    """Demonstrate cognitive map creation and usage."""
    print("\n" + "="*60)
    print("COGNITIVE MAP DEMONSTRATION")
    print("="*60)

    print("1. Creating cognitive map...")

    # Create cognitive map
    cognitive_map = CognitiveMap(
        map_id="demo_san_francisco",
        spatial_bounds={'west': -122.5, 'south': 37.7, 'east': -122.3, 'north': 37.9},
        cognitive_framework='landmark_based'
    )

    print("   ✓ Cognitive map initialized")

    # Add landmarks
    landmarks = [
        ('golden_gate_park', {
            'type': 'Point',
            'coordinates': [-122.4862, 37.7710]
        }, {'name': 'Golden Gate Park', 'type': 'park', 'significance': 'high'}),
        ('downtown_sf', {
            'type': 'Point',
            'coordinates': [-122.4194, 37.7749]
        }, {'name': 'Downtown San Francisco', 'type': 'district', 'significance': 'high'}),
        ('sf_airport', {
            'type': 'Point',
            'coordinates': [-122.3750, 37.6189]
        }, {'name': 'San Francisco Airport', 'type': 'airport', 'significance': 'medium'})
    ]

    for landmark_id, geometry, properties in landmarks:
        cognitive_map.add_landmark(
            landmark_id=landmark_id,
            geometry=geometry,
            properties=properties,
            saliency=0.8 if properties['significance'] == 'high' else 0.6
        )

    print(f"   ✓ Added {len(landmarks)} landmarks")

    # Add routes between landmarks
    routes = [
        ('park_to_downtown', 'golden_gate_park', 'downtown_sf',
         [{'type': 'LineString', 'coordinates': [[-122.4862, 37.7710], [-122.4194, 37.7749]]}],
         {'length': 5.2, 'mode': 'driving', 'difficulty': 'easy'}),
        ('downtown_to_airport', 'downtown_sf', 'sf_airport',
         [{'type': 'LineString', 'coordinates': [[-122.4194, 37.7749], [-122.3750, 37.6189]]}],
         {'length': 15.8, 'mode': 'driving', 'difficulty': 'moderate'})
    ]

    for route_id, start, end, segments, properties in routes:
        cognitive_map.add_route(route_id, start, end, segments, properties)

    print(f"   ✓ Added {len(routes)} routes")

    # Add regions
    regions = [
        ('financial_district', [
            [-122.4100, 37.7850],
            [-122.3900, 37.7850],
            [-122.3900, 37.7950],
            [-122.4100, 37.7950],
            [-122.4100, 37.7850]
        ], {'name': 'Financial District', 'type': 'business_district'}, ['downtown_sf'])
    ]

    for region_id, boundary, properties, landmarks in regions:
        cognitive_map.add_region(region_id, boundary, properties, landmarks)

    print(f"   ✓ Added {len(regions)} regions")

    # Demonstrate navigation
    print("2. Demonstrating cognitive navigation...")

    navigation_path = cognitive_map.get_navigation_path(
        'downtown_sf', 'golden_gate_park', create_sample_user_profile()
    )

    if navigation_path:
        print(f"   ✓ Navigation path: {' → '.join(navigation_path)}")
    else:
        print("   ✗ No navigation path found")

    # Display map statistics
    print("3. Cognitive map statistics...")

    stats = cognitive_map.get_map_statistics()
    print(f"   ✓ Landmarks: {stats['components']['landmarks']}")
    print(f"   ✓ Routes: {stats['components']['routes']}")
    print(f"   ✓ Regions: {stats['components']['regions']}")
    print(f"   ✓ Cognitive load: {stats['performance']['cognitive_load']".3f"}")
    print(f"   ✓ Average saliency: {stats['cognitive_properties']['average_saliency']".3f"}")

    return cognitive_map


def demonstrate_user_profiling():
    """Demonstrate user cognitive profiling capabilities."""
    print("\n" + "="*60)
    print("USER COGNITIVE PROFILING DEMONSTRATION")
    print("="*60)

    print("1. Creating profile manager...")

    profile_manager = ProfileManager(
        config={
            'learning_enabled': True,
            'adaptation_enabled': True,
            'expertise_learning_rate': 0.1
        }
    )

    print("   ✓ Profile manager initialized")

    # Create user profiles
    print("2. Creating user profiles...")

    users = [
        {
            'user_id': 'novice_user',
            'assessment': {
                'spatial_expertise_score': 0.3,
                'cognitive_style': 'verbalizer',
                'preferred_load_level': 'low'
            }
        },
        {
            'user_id': 'expert_user',
            'assessment': {
                'spatial_expertise_score': 0.9,
                'cognitive_style': 'visualizer',
                'preferred_load_level': 'high'
            }
        }
    ]

    profiles = {}
    for user_data in users:
        profile = profile_manager.create_profile(
            user_id=user_data['user_id'],
            initial_assessment=user_data['assessment']
        )
        profiles[user_data['user_id']] = profile
        print(f"   ✓ Profile created for {user_data['user_id']}")

    # Simulate user interactions and profile updates
    print("3. Simulating user interactions...")

    interactions = [
        {
            'user_id': 'novice_user',
            'interaction': {'task_complexity': 0.3, 'interaction_type': 'map_viewing'},
            'outcome': {'performance_score': 0.8, 'cognitive_load': 0.4}
        },
        {
            'user_id': 'expert_user',
            'interaction': {'task_complexity': 0.8, 'interaction_type': 'spatial_analysis'},
            'outcome': {'performance_score': 0.9, 'cognitive_load': 0.7}
        }
    ]

    for interaction in interactions:
        user_id = interaction['user_id']
        profile_manager.update_profile_from_interaction(
            user_id,
            interaction['interaction'],
            interaction['outcome']
        )
        print(f"   ✓ Updated profile for {user_id}")

    # Show personalized recommendations
    print("4. Generating personalized recommendations...")

    for user_id, profile in profiles.items():
        recommendations = profile.get_personalized_recommendations({
            'task_type': 'navigation',
            'complexity': 'moderate'
        })

        print(f"\n   Recommendations for {user_id}:")
        for category, items in recommendations.items():
            if items:
                print(f"     - {category}: {len(items)} suggestions")

    # Display profile summaries
    print("5. Profile summaries...")

    for user_id, profile in profiles.items():
        summary = profile.get_profile_summary()
        print(f"\n   {user_id} profile:")
        print(f"     - Expertise: {summary['spatial_capabilities']['expertise_level']".2f"}")
        print(f"     - Cognitive style: {summary['cognitive_preferences']['cognitive_style']}")
        print(f"     - Recent performance: {summary['performance_metrics']['recent_performance']".2f"}")


def create_visualization_demo():
    """Create a simple visualization of cognitive processing results."""
    print("\n" + "="*60)
    print("COGNITIVE PROCESSING VISUALIZATION")
    print("="*60)

    try:
        # Generate sample data for visualization
        processing_result = demonstrate_cognitive_processing()

        # Create simple performance chart
        plt.figure(figsize=(10, 6))

        # Processing time distribution
        plt.subplot(1, 2, 1)
        times = [0.5, 0.8, 1.2, 0.9, 1.1]  # Sample processing times
        plt.hist(times, bins=5, alpha=0.7, edgecolor='black')
        plt.title('Processing Time Distribution')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Frequency')

        # Cognitive load over time
        plt.subplot(1, 2, 2)
        loads = [0.3, 0.4, 0.5, 0.4, 0.3]  # Sample cognitive loads
        plt.plot(loads, marker='o', linewidth=2, markersize=6)
        plt.title('Cognitive Load Trend')
        plt.xlabel('Processing Step')
        plt.ylabel('Cognitive Load')
        plt.ylim(0, 1)

        plt.tight_layout()
        plt.savefig('cognitive_processing_demo.png', dpi=300, bbox_inches='tight')
        print("   ✓ Visualization saved as 'cognitive_processing_demo.png'")

        plt.show()

    except ImportError:
        print("   ⚠ Visualization requires matplotlib (uv pip install matplotlib)")
    except Exception as e:
        print(f"   ✗ Visualization failed: {str(e)}")


def main():
    """Main demonstration function."""
    print("GEO-INFER-COG: Cognitive Geospatial Processing Demonstration")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run demonstrations
        processing_result = demonstrate_cognitive_processing()
        demonstrate_spatial_language_processing()
        cognitive_map = demonstrate_cognitive_map_creation()
        demonstrate_user_profiling()

        # Optional visualization
        create_visualization_demo()

        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("="*60)

        # Export results for further analysis
        results = {
            'timestamp': datetime.now().isoformat(),
            'cognitive_processing': processing_result,
            'cognitive_map': cognitive_map.export_to_geojson() if cognitive_map else None,
            'demo_summary': {
                'components_tested': [
                    'CognitiveProcessingEngine',
                    'SpatialPerceptionModel',
                    'SpatialReasoningEngine',
                    'SpatialMemoryModel',
                    'SpatialLanguageProcessor',
                    'UserCognitiveProfile',
                    'CognitiveMap'
                ],
                'features_demonstrated': [
                    'Spatial perception and attention',
                    'Qualitative spatial reasoning',
                    'Spatial memory management',
                    'Natural language spatial processing',
                    'User cognitive profiling',
                    'Cognitive map creation and navigation'
                ]
            }
        }

        # Save results
        with open('cognitive_demo_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print("✓ Results saved to 'cognitive_demo_results.json'")
        print("✓ Demo completed successfully!")

        return True

    except Exception as e:
        print(f"\n✗ Demonstration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
