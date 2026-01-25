"""
Unit tests for CurriculumDesigner.

Tests curriculum design, module generation, standards alignment,
and learning pathway creation.
"""

import pytest
from geo_infer_edu.core.curriculum import (
    CurriculumDesigner,
    Curriculum,
    CurriculumModule,
    LearningObjective,
    EducationLevel,
    PedagogicalApproach
)


class TestCurriculumDesigner:
    """Test suite for CurriculumDesigner class."""
    
    @pytest.fixture
    def designer(self):
        """Create a CurriculumDesigner instance for testing."""
        return CurriculumDesigner(
            standards=["bok", "ngss"],
            pedagogical_approach="constructivist",
            assessment_framework="competency_based"
        )
    
    def test_init_default(self):
        """Test default initialization."""
        designer = CurriculumDesigner()
        assert designer.standards == ["bok"]
        assert designer.pedagogical_approach == PedagogicalApproach.CONSTRUCTIVIST
        assert designer.assessment_framework == "competency_based"
    
    def test_init_with_parameters(self, designer):
        """Test initialization with custom parameters."""
        assert "bok" in designer.standards
        assert "ngss" in designer.standards
        assert designer.pedagogical_approach == PedagogicalApproach.CONSTRUCTIVIST
    
    def test_design_curriculum(self, designer):
        """Test basic curriculum design."""
        curriculum = designer.design(
            topic="geospatial_analysis",
            level="undergraduate",
            duration="8_weeks",
            learning_objectives=None
        )
        
        assert isinstance(curriculum, Curriculum)
        assert curriculum.level == EducationLevel.UNDERGRADUATE
        assert curriculum.duration_weeks == 8
        assert len(curriculum.modules) > 0
        assert len(curriculum.target_competencies) > 0
    
    def test_design_with_custom_objectives(self, designer):
        """Test curriculum design with custom learning objectives."""
        objectives = [
            "Perform spatial analysis using H3 indexing",
            "Apply Active Inference to spatial problems"
        ]
        
        curriculum = designer.design(
            topic="spatial_modeling",
            level="graduate",
            duration="16_weeks",
            learning_objectives=objectives
        )
        
        assert curriculum.level == EducationLevel.GRADUATE
        assert curriculum.duration_weeks == 16
        # Check that modules contain objectives
        all_objectives = []
        for module in curriculum.modules:
            all_objectives.extend(module.learning_objectives)
        assert len(all_objectives) > 0
    
    def test_generate_modules(self, designer):
        """Test module generation."""
        objectives = [
            LearningObjective(
                id="lo_1",
                description="Test objective",
                bloom_level="apply",
                competency_area="spatial_analysis"
            )
        ]
        
        modules = designer.generate_modules(
            topic="test_topic",
            level=EducationLevel.UNDERGRADUATE,
            duration_weeks=4,
            objectives=objectives,
            hours_per_module=3.0
        )
        
        assert len(modules) == 4
        assert all(isinstance(m, CurriculumModule) for m in modules)
        assert all(m.duration_hours == 3.0 for m in modules)
    
    def test_module_content(self, designer):
        """Test that modules have proper content."""
        curriculum = designer.design(
            topic="cartography",
            level="professional",
            duration="4_weeks"
        )
        
        for module in curriculum.modules:
            assert module.id
            assert module.title
            assert module.description
            assert module.duration_hours > 0
            # Content sections, activities, assessments should be lists
            assert isinstance(module.content_sections, list)
            assert isinstance(module.activities, list)
            assert isinstance(module.assessments, list)
    
    def test_align_with_standards(self, designer):
        """Test standards alignment."""
        curriculum = designer.design(
            topic="gis_programming",
            level="undergraduate",
            duration="8_weeks"
        )
        
        alignment = designer.align_with_standards(
            curriculum=curriculum,
            target_standards=["bok_spatial_analysis"],
            coverage_report=True
        )
        
        assert "mappings" in alignment
        assert "coverage" in alignment
        assert isinstance(alignment["mappings"], dict)
    
    def test_create_learning_pathway(self, designer):
        """Test learning pathway creation."""
        learner_profile = {
            "id": "learner_001",
            "current_skills": ["data_management"]
        }
        
        pathway = designer.create_learning_pathway(
            learner_profile=learner_profile,
            target_competencies=["spatial_analysis", "geovisualization", "data_management"],
            available_time="10_hours_week",
            optimization="efficiency"
        )
        
        assert pathway["learner_id"] == "learner_001"
        assert "skill_gaps" in pathway
        assert "spatial_analysis" in pathway["skill_gaps"]
        assert "data_management" not in pathway["skill_gaps"]  # Already has this skill
        assert pathway["estimated_duration_weeks"] > 0
    
    def test_export_curriculum_yaml(self, designer):
        """Test curriculum export to YAML."""
        curriculum = designer.design(
            topic="remote_sensing",
            level="intermediate",
            duration="4_weeks"
        )
        
        exported = designer.export_curriculum(curriculum, format="yaml")
        
        assert isinstance(exported, str)
        assert "title" in exported
        assert "modules" in exported
    
    def test_export_curriculum_json(self, designer):
        """Test curriculum export to JSON."""
        curriculum = designer.design(
            topic="web_mapping",
            level="professional",
            duration="4_weeks"
        )
        
        exported = designer.export_curriculum(curriculum, format="json")
        
        assert isinstance(exported, str)
        import json
        data = json.loads(exported)
        assert "title" in data
        assert "modules" in data
    
    def test_export_invalid_format(self, designer):
        """Test that invalid export format raises error."""
        curriculum = designer.design(
            topic="test",
            level="undergraduate",
            duration="4_weeks"
        )
        
        with pytest.raises(ValueError):
            designer.export_curriculum(curriculum, format="invalid")
    
    def test_education_levels(self, designer):
        """Test all education levels are supported."""
        levels = ["elementary", "middle_school", "high_school", 
                  "undergraduate", "graduate", "professional"]
        
        for level in levels:
            curriculum = designer.design(
                topic="gis_basics",
                level=level,
                duration="2_weeks"
            )
            assert curriculum.level.value == level


class TestLearningObjective:
    """Test suite for LearningObjective dataclass."""
    
    def test_create_objective(self):
        """Test creating a learning objective."""
        objective = LearningObjective(
            id="lo_test",
            description="Test objective description",
            bloom_level="analyze",
            competency_area="spatial_thinking"
        )
        
        assert objective.id == "lo_test"
        assert objective.bloom_level == "analyze"
        assert objective.assessment_criteria == []
        assert objective.prerequisites == []
    
    def test_objective_with_all_fields(self):
        """Test objective with all optional fields."""
        objective = LearningObjective(
            id="lo_full",
            description="Full objective",
            bloom_level="create",
            competency_area="geospatial_programming",
            assessment_criteria=["Criterion 1", "Criterion 2"],
            prerequisites=["lo_prerequisite"]
        )
        
        assert len(objective.assessment_criteria) == 2
        assert len(objective.prerequisites) == 1


class TestCurriculum:
    """Test suite for Curriculum dataclass."""
    
    def test_create_curriculum(self):
        """Test creating a curriculum."""
        curriculum = Curriculum(
            id="test_curriculum",
            title="Test Curriculum",
            description="A test curriculum",
            level=EducationLevel.UNDERGRADUATE,
            duration_weeks=8
        )
        
        assert curriculum.id == "test_curriculum"
        assert curriculum.modules == []
        assert curriculum.standards_alignment == {}
    
    def test_curriculum_with_modules(self):
        """Test curriculum with modules."""
        module = CurriculumModule(
            id="module_1",
            title="Module 1",
            description="First module",
            learning_objectives=[],
            duration_hours=4.0
        )
        
        curriculum = Curriculum(
            id="test",
            title="Test",
            description="Test",
            level=EducationLevel.PROFESSIONAL,
            duration_weeks=4,
            modules=[module]
        )
        
        assert len(curriculum.modules) == 1
        assert curriculum.modules[0].id == "module_1"
