"""Cognitive wayfinding demo for GEO-INFER-COG.

Builds a cognitive map from landmarks and routes, generates a navigation
path with cognitive distortions, and demonstrates spatial memory storage
and profile-aware processing using the real public API.

Run with: uv run --no-sync python examples/cognitive_wayfinding.py
"""

from geo_infer_cog import CognitiveMap, SpatialMemoryModel, UserCognitiveProfile


def main() -> None:
    user = UserCognitiveProfile(
        user_id="visitor",
        spatial_expertise=0.4,
        spatial_reasoning_style="qualitative",
    )

    # --- Cognitive map: landmarks and routes -----------------------------
    cmap = CognitiveMap(
        "campus_map",
        spatial_bounds={"bbox": [-122.45, 37.43, -122.42, 37.44]},
        cognitive_framework="route_based",
    )

    landmarks = {
        "gate": {"type": "Point", "coordinates": [-122.4450, 37.4320]},
        "library": {"type": "Point", "coordinates": [-122.4400, 37.4330]},
        "quad": {"type": "Point", "coordinates": [-122.4350, 37.4340]},
        "lab": {"type": "Point", "coordinates": [-122.4300, 37.4350]},
    }
    for landmark_id, geometry in landmarks.items():
        cmap.add_landmark(landmark_id, geometry, {"name": landmark_id}, saliency=0.7)

    cmap.add_route("gate_to_library", "gate", "library", segments=[], properties={"mode": "walk"})
    cmap.add_route("library_to_quad", "library", "quad", segments=[], properties={"mode": "walk"})
    cmap.add_route("quad_to_lab", "quad", "lab", segments=[], properties={"mode": "walk"})

    print("Map statistics:", cmap.get_map_statistics())
    print("Cognitive load:", cmap.calculate_cognitive_load(user))

    # --- Navigation with cognitive distortions ----------------------------
    path = cmap.get_navigation_path("gate", "lab", user_profile=user)
    print("Navigation path (gate -> lab):", path)

    # --- Spatial memory: store and retrieve a navigation event ------------
    memory = SpatialMemoryModel(
        memory_types=["working", "long_term", "episodic"],
        consolidation_strategy="adaptive",
    )
    item_id = memory.store_spatial_memory(
        content={"path": path, "destination": "lab"},
        memory_type="episodic",
        importance=0.8,
        spatial_context={"bbox": cmap.spatial_bounds["bbox"]},
    )
    retrieved = memory.retrieve_spatial_memory(item_id)
    print("Retrieved memory item:", retrieved is not None)


if __name__ == "__main__":
    main()