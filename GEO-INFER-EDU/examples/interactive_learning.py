#!/usr/bin/env python3
"""
GEO-INFER-EDU Example: Personalized Interactive Learning Session

Demonstrates the real personalization API: registering a learner and a small
resource library, building an adaptive pathway, recommending resources,
delivering adaptive content, and scheduling spaced reviews.
"""

from geo_infer_edu import (
    ExerciseGenerator,
    PersonalizedLearning,
)
from geo_infer_edu.core.personalization import LearningResource


def main() -> None:
    print("=" * 60)
    print("1. Set up the personalization engine and resource library")
    print("=" * 60)
    personalizer = PersonalizedLearning(
        adaptation_method="knowledge_tracing",
        recommendation_algorithm="collaborative_filtering",
    )

    resources = [
        LearningResource(
            resource_id="res_001",
            title="Interactive Choropleth Mapping",
            resource_type="tutorial",
            topic="geovisualization",
            difficulty="beginner",
            duration_minutes=40,
            format="interactive",
        ),
        LearningResource(
            resource_id="res_002",
            title="Designing Effective Map Symbology",
            resource_type="reading",
            topic="geovisualization",
            difficulty="intermediate",
            duration_minutes=25,
            format="text",
        ),
        LearningResource(
            resource_id="res_003",
            title="Automate GIS Workflows with Python",
            resource_type="exercise",
            topic="geospatial_programming",
            difficulty="intermediate",
            duration_minutes=60,
            format="notebook",
        ),
    ]
    for resource in resources:
        personalizer.register_resource(resource)
    print(f"Registered {len(resources)} learning resources")

    print()
    print("=" * 60)
    print("2. Create an adaptive learning pathway")
    print("=" * 60)
    profile = personalizer.register_learner(
        {
            "id": "student_042",
            "learning_style": "visual",
            "prior_knowledge": ["spatial_analysis"],
            "interests": ["cartography"],
            "hours_per_week": 8,
        }
    )
    pathway = personalizer.create_pathway(
        learner_profile={"id": profile.learner_id, "prior_knowledge": ["spatial_analysis"]},
        learning_goals=["geovisualization", "geospatial_programming"],
        constraints={"time": "20_hours"},
    )
    print(f"Pathway {pathway.pathway_id} ({pathway.optimization_strategy}):")
    for step in pathway.sequence:
        print(f"  {step['order']}. {step['skill']} "
              f"(~{step['estimated_hours']:.1f} hours, "
              f"{len(step['resources'])} matching resources)")
    print(f"Estimated duration: {pathway.estimated_duration_weeks} weeks")

    print()
    print("=" * 60)
    print("3. Recommend resources for the next topic")
    print("=" * 60)
    recommendations = personalizer.recommend_resources(
        learner_id="student_042",
        current_topic="geovisualization",
    )
    for rec in recommendations:
        print(f"- {rec['title']} [{rec['type']}] "
              f"relevance={rec['relevance_score']:.2f} "
              f"matches_style={rec['matches_style']}")

    print()
    print("=" * 60)
    print("4. Adaptive delivery and spaced review")
    print("=" * 60)
    content = personalizer.deliver_adaptive_content(
        learner_id="student_042",
        topic="geovisualization",
    )
    print(f"Adaptive content keys: {sorted(content)}")

    exercises = ExerciseGenerator().create(
        concepts=["map_symbology"],
        format="quiz",
        difficulty="beginner",
    )
    for exercise in exercises:
        print(f"Exercise: {exercise.title} - {exercise.concepts}")

    schedule = personalizer.schedule_review(
        learner_id="student_042",
        mastered_topics=["spatial_analysis"],
    )
    print("Review schedule:")
    for entry in schedule:
        print(f"- {entry['topic']} in {entry['interval_days']} days")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()