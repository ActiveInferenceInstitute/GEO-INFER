"""Tests for exercise generator module."""

import pytest
from geo_infer_edu.core.exercises import (
    ExerciseGenerator,
    ExerciseType,
    DifficultyLevel,
    Exercise,
    Assessment,
)


class TestExerciseDataclasses:
    """Tests for exercise dataclass and enum creation."""

    def test_exercise_type_values(self) -> None:
        assert ExerciseType.MAPPING.value == "mapping"
        assert ExerciseType.CODING.value == "coding"
        assert ExerciseType.PROJECT.value == "project"

    def test_difficulty_level_values(self) -> None:
        assert DifficultyLevel.BEGINNER.value == "beginner"
        assert DifficultyLevel.EXPERT.value == "expert"

    def test_exercise_creation(self) -> None:
        exercise = Exercise(
            id="ex1",
            title="Buffer Analysis",
            description="Practice buffer analysis",
            exercise_type=ExerciseType.MAPPING,
            difficulty=DifficultyLevel.BEGINNER,
            concepts=["buffer_analysis"],
            instructions="Create buffer zones",
            expected_duration_minutes=20,
        )
        assert exercise.id == "ex1"
        assert exercise.expected_duration_minutes == 20


class TestExerciseGeneratorInit:
    """Tests for ExerciseGenerator initialization."""

    def test_default_initialization(self) -> None:
        gen = ExerciseGenerator()
        assert gen is not None
        assert "mapping" in gen.exercise_types
        assert gen.difficulty_scaling == "adaptive"
        assert gen.feedback_mode == "immediate"

    def test_custom_initialization(self) -> None:
        gen = ExerciseGenerator(
            exercise_types=["coding"],
            difficulty_scaling="fixed",
            feedback_mode="delayed",
        )
        assert gen.exercise_types == ["coding"]
        assert gen.difficulty_scaling == "fixed"


class TestExerciseCreation:
    """Tests for exercise creation."""

    def test_create_exercises_progressive(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["buffer_analysis", "overlay_analysis", "spatial_join"],
            format="interactive_map",
            difficulty="progressive",
        )
        assert len(exercises) == 3
        assert exercises[0].difficulty == DifficultyLevel.BEGINNER
        assert exercises[1].difficulty == DifficultyLevel.INTERMEDIATE
        assert exercises[2].difficulty == DifficultyLevel.ADVANCED

    def test_create_exercises_fixed_difficulty(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["interpolation"],
            format="code",
            difficulty="intermediate",
        )
        assert len(exercises) == 1
        assert exercises[0].difficulty == DifficultyLevel.INTERMEDIATE
        assert exercises[0].exercise_type == ExerciseType.CODING

    def test_create_with_hints(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["gis_basics"],
            include_hints=True,
        )
        assert len(exercises[0].hints) > 0

    def test_create_without_hints(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["gis_basics"],
            include_hints=False,
        )
        assert len(exercises[0].hints) == 0

    def test_coding_exercises_have_starter_code(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["spatial_analysis"],
            format="code",
        )
        assert exercises[0].starter_code is not None
        assert "def analyze_" in exercises[0].starter_code

    def test_coding_exercises_have_test_cases(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["spatial_analysis"],
            format="code",
        )
        assert len(exercises[0].test_cases) > 0


class TestCodingExercises:
    """Tests for coding exercise generation."""

    def test_create_coding_exercises(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create_coding_exercises(
            topic="spatial_analysis",
            language="python",
            framework="geo_infer",
        )
        assert len(exercises) == 3  # beginner, intermediate, advanced
        for ex in exercises:
            assert ex.exercise_type == ExerciseType.CODING
            assert ex.starter_code is not None
            assert len(ex.test_cases) > 0

    def test_coding_exercises_without_starter_code(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create_coding_exercises(
            topic="raster_analysis",
            starter_code=False,
        )
        assert exercises[0].starter_code is None

    def test_coding_exercises_without_test_cases(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create_coding_exercises(
            topic="vector_analysis",
            test_cases=False,
        )
        assert len(exercises[0].test_cases) == 0


class TestPBLScenario:
    """Tests for problem-based learning scenarios."""

    def test_create_pbl_scenario(self) -> None:
        gen = ExerciseGenerator()
        exercise = gen.create_pbl_scenario(
            context="urban_planning",
            problem="optimize_fire_station_locations",
            data_provided=["road_network.shp", "population_grid.tif", "fire_incidents.csv"],
            expected_deliverables=["Location analysis map", "Optimization report"],
        )
        assert exercise.exercise_type == ExerciseType.PROJECT
        assert exercise.difficulty == DifficultyLevel.ADVANCED
        assert exercise.expected_duration_minutes == 180
        assert "urban_planning" in exercise.concepts
        assert len(exercise.rubric) > 0
        # Check rubric weights sum to approximately 1
        total_weight = sum(v["weight"] for v in exercise.rubric.values())
        assert abs(total_weight - 1.0) < 0.01


class TestAssessmentCreation:
    """Tests for assessment creation."""

    def test_create_assessment(self) -> None:
        gen = ExerciseGenerator()
        assessment = gen.create_assessment(
            learning_objectives=[
                {"concept": "gis_basics", "description": "Demonstrate GIS fundamentals"},
                {"concept": "spatial_analysis", "description": "Apply spatial analysis"},
                {"concept": "cartography", "description": "Create professional maps"},
            ],
            item_types=["multiple_choice", "practical"],
            difficulty_distribution={"easy": 0.3, "medium": 0.5, "hard": 0.2},
        )
        assert isinstance(assessment, Assessment)
        assert len(assessment.items) == 3
        assert assessment.passing_score == 0.7
        assert assessment.time_limit_minutes > 0
        assert len(assessment.rubrics) == 3

    def test_assessment_without_rubrics(self) -> None:
        gen = ExerciseGenerator()
        assessment = gen.create_assessment(
            learning_objectives=[
                {"concept": "gis", "description": "GIS skills"},
            ],
            item_types=["practical"],
            difficulty_distribution={"medium": 1.0},
            rubrics=False,
        )
        assert len(assessment.rubrics) == 0

    def test_unique_exercise_ids(self) -> None:
        gen = ExerciseGenerator()
        exercises = gen.create(
            concepts=["a", "b", "c", "d", "e"],
            format="interactive_map",
        )
        ids = [ex.id for ex in exercises]
        assert len(ids) == len(set(ids))  # All unique
