"""Regression tests for human-centered visualization planning."""

import pytest

from geo_infer_cog.visualization import ColorScheme, HumanCenteredVisualizer


def _points():
    return {
        "geometries": [
            {"type": "Point", "coordinates": [0.0, 0.0]},
            {"type": "Point", "coordinates": [0.05, 0.0]},
            {"type": "Point", "coordinates": [1.0, 1.0]},
        ]
    }


def test_visualization_ids_are_deterministic_per_instance():
    visualizer = HumanCenteredVisualizer(config={"proximity_threshold": 0.1})
    first = visualizer.create_optimized_map(_points())
    second = visualizer.create_optimized_map(_points())
    assert first["visualization_id"] == "viz_000001"
    assert second["visualization_id"] == "viz_000002"


def test_grouping_returns_real_clusters():
    visualizer = HumanCenteredVisualizer(config={"proximity_threshold": 0.1})
    proximity = visualizer._apply_proximity_grouping_to_data(_points())
    similarity = visualizer._apply_similarity_grouping_to_data(_points())
    assert proximity["clusters_found"] == 2
    assert proximity["clusters"][0]["size"] == 2
    assert similarity["similarity_groups"] == 1
    assert similarity["groups"][0]["size"] == 3


def test_visualization_inputs_and_color_counts_are_validated():
    with pytest.raises(ValueError, match="proximity_threshold"):
        HumanCenteredVisualizer(config={"proximity_threshold": 0})
    with pytest.raises(ValueError, match="non-negative integer"):
        ColorScheme().get_perceptually_uniform_colors(-1)
    with pytest.raises(TypeError, match="mapping"):
        HumanCenteredVisualizer().create_optimized_map([])
