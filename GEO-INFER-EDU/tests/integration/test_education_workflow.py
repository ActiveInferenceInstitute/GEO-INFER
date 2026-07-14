"""Integration coverage for deterministic educational exercise generation."""

from geo_infer_edu.core.exercises import ExerciseGenerator


def test_exercise_generation_produces_actionable_items() -> None:
    """Generate a mapped-learning exercise with stable structural fields."""
    exercises = ExerciseGenerator(exercise_types=["mapping"]).create(
        ["spatial indexing"], format="interactive_map", difficulty="beginner"
    )

    assert len(exercises) == 1
    assert exercises[0].concepts == ["spatial indexing"]
    assert exercises[0].instructions
