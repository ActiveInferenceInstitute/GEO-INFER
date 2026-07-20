"""Tests for personalized learning module."""

from geo_infer_edu.core.personalization import (
    PersonalizedLearning,
    LearnerProfile,
    LearningResource,
    LearningPathway,
)


class TestPersonalizationDataclasses:
    """Tests for personalization dataclass creation."""

    def test_learner_profile_creation(self) -> None:
        profile = LearnerProfile(
            learner_id="l1",
            learning_style="visual",
            prior_knowledge=["python", "statistics"],
        )
        assert profile.learner_id == "l1"
        assert profile.preferred_pace == "moderate"

    def test_learning_resource_creation(self) -> None:
        resource = LearningResource(
            resource_id="r1",
            title="Intro to GIS",
            resource_type="video",
            topic="gis_basics",
            difficulty="beginner",
            duration_minutes=30,
            format="mp4",
        )
        assert resource.duration_minutes == 30


class TestPersonalizedLearningInit:
    """Tests for PersonalizedLearning initialization."""

    def test_default_initialization(self) -> None:
        pl = PersonalizedLearning()
        assert pl is not None
        assert pl.adaptation_method == "knowledge_tracing"
        assert "visual" in pl.learning_styles

    def test_custom_initialization(self) -> None:
        pl = PersonalizedLearning(
            adaptation_method="bayesian",
            recommendation_algorithm="content_based",
        )
        assert pl.adaptation_method == "bayesian"

    def test_register_learner(self) -> None:
        pl = PersonalizedLearning()
        profile = pl.register_learner(
            {
                "id": "l1",
                "learning_style": "kinesthetic",
                "prior_knowledge": ["python"],
                "interests": ["remote_sensing"],
                "pace": "fast",
                "hours_per_week": 15,
            }
        )
        assert profile.learner_id == "l1"
        assert profile.learning_style == "kinesthetic"
        assert profile.available_time_hours_week == 15


class TestLearningPathway:
    """Tests for learning pathway creation."""

    def test_create_pathway(self) -> None:
        pl = PersonalizedLearning()
        pathway = pl.create_pathway(
            learner_profile={
                "id": "l1",
                "prior_knowledge": ["python"],
                "hours_per_week": 10,
            },
            learning_goals=["spatial_analysis", "remote_sensing", "gis_mapping"],
            constraints={"time": "20_hours"},
            optimization="mastery",
        )
        assert isinstance(pathway, LearningPathway)
        assert pathway.learner_id == "l1"
        # Should have 2 skill gaps (spatial_analysis and remote_sensing, gis_mapping minus python)
        assert len(pathway.sequence) >= 2
        assert pathway.optimization_strategy == "mastery"

    def test_pathway_no_skill_gaps(self) -> None:
        pl = PersonalizedLearning()
        pathway = pl.create_pathway(
            learner_profile={
                "id": "l2",
                "prior_knowledge": ["spatial_analysis"],
                "hours_per_week": 5,
            },
            learning_goals=["spatial_analysis"],
            constraints={"time": "10_hours"},
        )
        assert len(pathway.sequence) == 0


class TestRecommendations:
    """Tests for resource recommendations."""

    def test_recommend_resources(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1", "learning_style": "visual"})
        pl.register_resource(
            LearningResource(
                resource_id="gis-video",
                title="GIS analysis video",
                resource_type="video",
                topic="spatial_analysis",
                difficulty="appropriate",
                duration_minutes=30,
                format="mp4",
            )
        )
        pl.register_resource(
            LearningResource(
                resource_id="gis-reading",
                title="GIS analysis reading",
                resource_type="reading",
                topic="spatial_analysis",
                difficulty="appropriate",
                duration_minutes=20,
                format="html",
            )
        )
        recs = pl.recommend_resources(
            learner_id="l1",
            current_topic="spatial_analysis",
        )
        assert len(recs) > 0
        # Should be sorted by relevance
        for i in range(len(recs) - 1):
            assert recs[i]["relevance_score"] >= recs[i + 1]["relevance_score"]

    def test_recommend_unknown_learner(self) -> None:
        pl = PersonalizedLearning()
        recs = pl.recommend_resources(
            learner_id="unknown",
            current_topic="gis",
        )
        assert recs == []


class TestAdaptiveContent:
    """Tests for adaptive content delivery."""

    def test_deliver_introductory_content(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1", "learning_style": "visual"})
        content = pl.deliver_adaptive_content(
            learner_id="l1",
            topic="gis_basics",
            mastery_level=0.1,
        )
        assert content["difficulty"] == "introductory"
        assert content["content_depth"] == "foundational"
        assert len(content["sections"]) >= 3

    def test_deliver_advanced_content(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1"})
        content = pl.deliver_adaptive_content(
            learner_id="l1",
            topic="spatial_statistics",
            mastery_level=0.75,
        )
        assert content["difficulty"] == "advanced"
        assert any(s["section_id"] == "advanced_topics" for s in content["sections"])

    def test_deliver_unknown_learner(self) -> None:
        pl = PersonalizedLearning()
        content = pl.deliver_adaptive_content(learner_id="unknown", topic="gis")
        assert "error" in content


class TestSpacedRepetition:
    """Tests for spaced repetition scheduling."""

    def test_schedule_review(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1"})
        schedule = pl.schedule_review(
            learner_id="l1",
            mastered_topics=["gis_basics", "coordinate_systems"],
        )
        assert len(schedule) > 0
        # Schedule should be sorted by date
        for i in range(len(schedule) - 1):
            assert schedule[i]["scheduled_date"] <= schedule[i + 1]["scheduled_date"]

    def test_high_mastery_skips_early_reviews(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1"})
        pl._mastery_data["l1"]["gis_basics"] = 0.95
        schedule = pl.schedule_review(
            learner_id="l1",
            mastered_topics=["gis_basics"],
        )
        # High mastery skips early intervals (1, 3 days), starts at 7
        if schedule:
            assert schedule[0]["interval_days"] >= 7


class TestMasteryUpdate:
    """Tests for mastery level updates."""

    def test_update_mastery(self) -> None:
        pl = PersonalizedLearning()
        pl.register_learner({"id": "l1"})
        new_mastery = pl.update_mastery("l1", "gis_basics", 0.8)
        assert 0 < new_mastery < 1
        assert new_mastery > 0  # Started at 0, should increase with 0.8 performance

    def test_mastery_clamped(self) -> None:
        pl = PersonalizedLearning()
        pl._mastery_data["l1"] = {"topic": 0.99}
        new_mastery = pl.update_mastery("l1", "topic", 1.0)
        assert new_mastery <= 1.0

    def test_mastery_creates_learner_data(self) -> None:
        pl = PersonalizedLearning()
        new_mastery = pl.update_mastery("new_learner", "topic", 0.5)
        assert "new_learner" in pl._mastery_data
