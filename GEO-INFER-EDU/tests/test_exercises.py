"""
Unit tests for ExerciseGenerator.

Tests exercise creation, coding exercises, PBL scenarios,
and assessment generation.
"""

import pytest
from geo_infer_edu.core.exercises import (
    ExerciseGenerator,
    Exercise,
    Assessment,
    ExerciseType,
    DifficultyLevel
)


class TestExerciseGenerator:
    """Test suite for ExerciseGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create an ExerciseGenerator instance for testing."""
        return ExerciseGenerator(
            exercise_types=["mapping", "analysis", "coding"],
            difficulty_scaling="adaptive",
            feedback_mode="immediate"
        )
    
    def test_init_default(self):
        """Test default initialization."""
        generator = ExerciseGenerator()
        assert "mapping" in generator.exercise_types
        assert generator.difficulty_scaling == "adaptive"
        assert generator.feedback_mode == "immediate"
    
    def test_create_exercises(self, generator):
        """Test basic exercise creation."""
        exercises = generator.create(
            concepts=["spatial_analysis", "buffering"],
            format="interactive_map",
            difficulty="progressive",
            include_hints=True
        )
        
        assert len(exercises) == 2
        assert all(isinstance(e, Exercise) for e in exercises)
        assert all(len(e.hints) > 0 for e in exercises)
    
    def test_progressive_difficulty(self, generator):
        """Test progressive difficulty scaling."""
        exercises = generator.create(
            concepts=["concept_1", "concept_2", "concept_3"],
            format="practical",
            difficulty="progressive",
            include_hints=True
        )
        
        difficulties = [e.difficulty for e in exercises]
        # Should progress through difficulty levels
        assert difficulties[0] == DifficultyLevel.BEGINNER
        assert difficulties[1] == DifficultyLevel.INTERMEDIATE
        assert difficulties[2] == DifficultyLevel.ADVANCED
    
    def test_fixed_difficulty(self, generator):
        """Test fixed difficulty setting."""
        exercises = generator.create(
            concepts=["topic_1", "topic_2"],
            format="code",
            difficulty="advanced",
            include_hints=False
        )
        
        assert all(e.difficulty == DifficultyLevel.ADVANCED for e in exercises)
        assert all(len(e.hints) == 0 for e in exercises)
    
    def test_exercise_has_required_fields(self, generator):
        """Test that exercises have all required fields."""
        exercises = generator.create(
            concepts=["test_concept"],
            format="interactive_map"
        )
        
        exercise = exercises[0]
        assert exercise.id
        assert exercise.title
        assert exercise.description
        assert exercise.exercise_type
        assert exercise.difficulty
        assert exercise.instructions
        assert exercise.expected_duration_minutes > 0
    
    def test_create_coding_exercises(self, generator):
        """Test coding exercise generation."""
        exercises = generator.create_coding_exercises(
            topic="h3_spatial_indexing",
            language="python",
            framework="geo_infer",
            test_cases=True,
            starter_code=True
        )
        
        assert len(exercises) == 3  # beginner, intermediate, advanced
        assert all(e.exercise_type == ExerciseType.CODING for e in exercises)
        assert all(e.starter_code is not None for e in exercises)
        assert all(len(e.test_cases) > 0 for e in exercises)
    
    def test_coding_exercise_starter_code(self, generator):
        """Test starter code content."""
        exercises = generator.create_coding_exercises(
            topic="buffer_analysis",
            language="python",
            framework="geo_infer",
            test_cases=True,
            starter_code=True
        )
        
        starter_code = exercises[0].starter_code
        assert "def analyze_" in starter_code
        assert "TODO" in starter_code
        assert "SpatialAnalyzer" in starter_code
    
    def test_coding_exercise_test_cases(self, generator):
        """Test that test cases are properly generated."""
        exercises = generator.create_coding_exercises(
            topic="clustering",
            language="python",
            framework="geo_infer"
        )
        
        test_cases = exercises[0].test_cases
        assert len(test_cases) >= 3
        assert all("name" in tc for tc in test_cases)
        assert all("input" in tc for tc in test_cases)
        assert all("expected" in tc for tc in test_cases)
    
    def test_create_pbl_scenario(self, generator):
        """Test problem-based learning scenario creation."""
        pbl = generator.create_pbl_scenario(
            context="urban_planning",
            problem="optimize_fire_station_locations",
            data_provided=["population_density", "road_network", "existing_stations"],
            expected_deliverables=["analysis_report", "optimal_locations", "justification"]
        )
        
        assert isinstance(pbl, Exercise)
        assert pbl.exercise_type == ExerciseType.PROJECT
        assert pbl.difficulty == DifficultyLevel.ADVANCED
        assert len(pbl.resources) == 3
        assert "rubric" in dir(pbl)
        assert len(pbl.rubric) > 0
    
    def test_pbl_scenario_instructions(self, generator):
        """Test PBL scenario has comprehensive instructions."""
        pbl = generator.create_pbl_scenario(
            context="environmental_monitoring",
            problem="detect_deforestation",
            data_provided=["satellite_imagery", "forest_boundaries"],
            expected_deliverables=["change_map", "analysis_report"]
        )
        
        instructions = pbl.instructions
        assert "Problem-Based Learning" in instructions
        assert "Context" in instructions
        assert "Deliverables" in instructions
        assert "satellite_imagery" in instructions
    
    def test_create_assessment(self, generator):
        """Test assessment creation."""
        objectives = [
            {"description": "Understand spatial relationships", "concept": "spatial_concepts"},
            {"description": "Apply buffer analysis", "concept": "buffer_analysis"},
            {"description": "Create thematic maps", "concept": "cartography"}
        ]
        
        assessment = generator.create_assessment(
            learning_objectives=objectives,
            item_types=["multiple_choice", "practical"],
            difficulty_distribution={"easy": 0.3, "medium": 0.5, "hard": 0.2},
            rubrics=True
        )
        
        assert isinstance(assessment, Assessment)
        assert len(assessment.items) == 3
        assert assessment.passing_score == 0.7
        assert len(assessment.rubrics) == 3
    
    def test_assessment_time_limit(self, generator):
        """Test assessment time limit calculation."""
        objectives = [
            {"description": "Obj 1", "concept": "concept_1"},
            {"description": "Obj 2", "concept": "concept_2"}
        ]
        
        assessment = generator.create_assessment(
            learning_objectives=objectives,
            item_types=["multiple_choice", "practical"],
            difficulty_distribution={"easy": 0.5, "medium": 0.5, "hard": 0.0}
        )
        
        assert assessment.time_limit_minutes > 0
        # Time limit should be sum of item durations
        total_expected = sum(item.expected_duration_minutes for item in assessment.items)
        assert assessment.time_limit_minutes == total_expected
    
    def test_exercise_format_mapping(self, generator):
        """Test that formats map to correct exercise types."""
        format_expectations = {
            "interactive_map": ExerciseType.MAPPING,
            "code": ExerciseType.CODING,
            "quiz": ExerciseType.MULTIPLE_CHOICE,
            "practical": ExerciseType.PRACTICAL
        }
        
        for format_name, expected_type in format_expectations.items():
            exercises = generator.create(
                concepts=["test"],
                format=format_name
            )
            assert exercises[0].exercise_type == expected_type
    
    def test_duration_estimation(self, generator):
        """Test duration estimation varies by difficulty."""
        beginner_exercises = generator.create(
            concepts=["topic"],
            format="practical",
            difficulty="beginner"
        )
        
        advanced_exercises = generator.create(
            concepts=["topic"],
            format="practical",
            difficulty="advanced"
        )
        
        # Advanced should take longer
        assert advanced_exercises[0].expected_duration_minutes > beginner_exercises[0].expected_duration_minutes
    
    def test_unique_exercise_ids(self, generator):
        """Test that generated exercise IDs are unique."""
        exercises = generator.create(
            concepts=["a", "b", "c", "d", "e"],
            format="analysis"
        )
        
        ids = [e.id for e in exercises]
        assert len(ids) == len(set(ids))  # All unique


class TestExercise:
    """Test suite for Exercise dataclass."""
    
    def test_create_exercise(self):
        """Test creating an exercise."""
        exercise = Exercise(
            id="ex_test",
            title="Test Exercise",
            description="A test exercise",
            exercise_type=ExerciseType.ANALYSIS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            concepts=["spatial_analysis"],
            instructions="Complete the analysis",
            expected_duration_minutes=30
        )
        
        assert exercise.id == "ex_test"
        assert exercise.hints == []
        assert exercise.starter_code is None
        assert exercise.test_cases == []
    
    def test_exercise_with_all_fields(self):
        """Test exercise with all optional fields."""
        exercise = Exercise(
            id="ex_full",
            title="Full Exercise",
            description="Complete exercise",
            exercise_type=ExerciseType.CODING,
            difficulty=DifficultyLevel.ADVANCED,
            concepts=["programming"],
            instructions="Write the code",
            expected_duration_minutes=60,
            hints=["Hint 1", "Hint 2"],
            starter_code="# Your code here",
            test_cases=[{"name": "test_1"}],
            rubric={"criteria": "value"},
            resources=["Resource 1"]
        )
        
        assert len(exercise.hints) == 2
        assert exercise.starter_code is not None
        assert len(exercise.test_cases) == 1


class TestAssessment:
    """Test suite for Assessment dataclass."""
    
    def test_create_assessment(self):
        """Test creating an assessment."""
        exercise = Exercise(
            id="item_1",
            title="Item 1",
            description="Test item",
            exercise_type=ExerciseType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            concepts=["basic"],
            instructions="Answer the question",
            expected_duration_minutes=5
        )
        
        assessment = Assessment(
            id="test_assessment",
            title="Test Assessment",
            description="A test assessment",
            items=[exercise]
        )
        
        assert assessment.id == "test_assessment"
        assert len(assessment.items) == 1
        assert assessment.passing_score == 0.7
        assert assessment.time_limit_minutes is None
