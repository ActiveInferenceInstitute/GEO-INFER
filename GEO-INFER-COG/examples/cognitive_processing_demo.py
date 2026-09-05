"""Cognitive processing demo for GEO-INFER-COG.

Runs a small feature collection through the full cognitive pipeline
(perception -> working memory -> reasoning -> memory -> decisions) using
the real public API, and prints the observable outputs.

Run with: uv run --no-sync python examples/cognitive_processing_demo.py
"""

from geo_infer_cog import (
    CognitiveProcessingEngine,
    SpatialLanguageProcessor,
    UserCognitiveProfile,
)


def main() -> None:
    # Deterministic by default: the engine uses a fixed-seed RNG internally.
    engine = CognitiveProcessingEngine()

    spatial_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.4194, 37.7749]},
                "properties": {"name": "city hall", "category": "civic"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-122.4000, 37.7900]},
                "properties": {"name": "museum", "category": "cultural"},
            },
        ],
    }

    profile = UserCognitiveProfile(user_id="demo_user", spatial_expertise=0.8)

    result = engine.process_spatial_input(
        spatial_data=spatial_data,
        context={"task": "site_assessment"},
        user_profile=profile,
    )

    print("Processing result keys:", sorted(result.keys()))
    print("Processing time (s):", result["processing_time"])
    print("Decisions:", result["decision_result"]["decisions"])
    print(
        "Decision strategy:",
        result["decision_result"]["decision_strategy"],
    )
    print(
        "Confidence distribution:",
        result["decision_result"]["confidence_distribution"],
    )

    # Spatial language processing on a natural-language description
    processor = SpatialLanguageProcessor()
    entities = processor.extract_spatial_entities(
        "The museum is north of the city hall, about two kilometers away."
    )
    print("Extracted spatial entities:", [e.text for e in entities])


if __name__ == "__main__":
    main()