"""
DOMAIN-01 Acceptance tests for GEO-INFER-COG documented features.

These tests exercise real implemented behavior for documented features that
previously lacked focused acceptance tests:

1. SpatialReasoningEngine.reason_about_space — the primary public reasoning
   pipeline (RCC-8 qualitative spatial reasoning, validation, alternatives).
2. UserCognitiveProfile adaptive methods — update_from_interaction,
   calculate_task_suitability, export_profile / import_profile round-trip.

No mocks, stubs, or placeholders: every assertion exercises actual code paths.
"""

import numpy as np
import pytest

from geo_infer_cog.core.spatial_reasoning import (
    SpatialReasoningEngine,
    SpatialRelation,
)
from geo_infer_cog.core.cognitive_engine import CognitiveProcessingEngine
from geo_infer_cog.models.user_profiles import UserCognitiveProfile


# ---------------------------------------------------------------------------
# SpatialReasoningEngine.reason_about_space
# ---------------------------------------------------------------------------

class TestReasonAboutSpace:
    """Acceptance: the public reasoning pipeline runs end-to-end."""

    @pytest.fixture
    def engine(self) -> SpatialReasoningEngine:
        return SpatialReasoningEngine(
            reasoning_type="qualitative_spatial",
            uncertainty_method="probabilistic",
        )

    @pytest.fixture
    def spatial_data(self) -> dict:
        return {
            "elements": [
                {"id": "region_a", "geometry": {"type": "Point", "coordinates": [0, 0]}},
                {"id": "region_b", "geometry": {"type": "Point", "coordinates": [10, 10]}},
            ]
        }

    @pytest.fixture
    def perception_result(self) -> dict:
        return {"attention_weights": {"region_a": 0.6, "region_b": 0.4}}

    def test_returns_required_keys(self, engine, spatial_data, perception_result):
        """The result dict must contain all documented output fields."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        expected_keys = {
            "reasoning_id",
            "timestamp",
            "processing_time",
            "reasoning_type",
            "premises",
            "conclusions",
            "validation_result",
            "spatial_alternatives",
            "reasoning_chain",
            "reasoning_metrics",
            "confidence_score",
        }
        assert expected_keys.issubset(result.keys())

    def test_reasoning_type_reflected(self, engine, spatial_data, perception_result):
        """The reasoning_type in the result matches the engine config."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        assert result["reasoning_type"] == "qualitative_spatial"

    def test_metrics_incremented(self, engine, spatial_data, perception_result):
        """Executing reasoning increments the chain counter."""
        before = engine.reasoning_metrics["reasoning_chains_executed"]
        engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        after = engine.reasoning_metrics["reasoning_chains_executed"]
        assert after == before + 1

    def test_processing_time_positive(self, engine, spatial_data, perception_result):
        """Processing time is a non-negative float."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        assert isinstance(result["processing_time"], float)
        assert result["processing_time"] >= 0.0

    def test_reasoning_chain_nonempty(self, engine, spatial_data, perception_result):
        """The reasoning chain must contain at least one step."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        assert len(result["reasoning_chain"]) >= 1

    def test_validation_result_has_valid_flag(self, engine, spatial_data, perception_result):
        """The validation result contains a 'valid' boolean."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        assert "valid" in result["validation_result"]
        assert isinstance(result["validation_result"]["valid"], bool)

    def test_confidence_score_bounded(self, engine, spatial_data, perception_result):
        """Confidence score is in [0, 1]."""
        result = engine.reason_about_space(spatial_data, perception_result, cognitive_state=None)
        assert 0.0 <= result["confidence_score"] <= 1.0


# ---------------------------------------------------------------------------
# CognitiveProcessingEngine.process_spatial_input (full pipeline)
# ---------------------------------------------------------------------------

class TestCognitivePipeline:
    """Acceptance: the full cognitive processing pipeline runs end-to-end."""

    def test_process_spatial_input_returns_result(self):
        """process_spatial_input produces a structured cognitive result."""
        engine = CognitiveProcessingEngine()
        spatial_data = {
            "elements": [
                {"id": "loc1", "geometry": {"type": "Point", "coordinates": [0, 0]}},
            ]
        }
        result = engine.process_spatial_input(spatial_data)
        assert "processing_id" in result
        assert "perception_result" in result
        assert "reasoning_result" in result
        assert "processing_time" in result

    def test_pipeline_increments_metrics(self):
        """Running the pipeline increments all performance counters."""
        engine = CognitiveProcessingEngine()
        spatial_data = {"elements": [{"id": "x", "geometry": {"type": "Point", "coordinates": [0, 0]}}]}
        before = engine.performance_metrics.copy()
        engine.process_spatial_input(spatial_data)
        after = engine.performance_metrics
        assert after["perception_updates"] == before["perception_updates"] + 1
        assert after["reasoning_chains"] == before["reasoning_chains"] + 1
        assert after["memory_operations"] == before["memory_operations"] + 1
        assert after["decisions_made"] == before["decisions_made"] + 1


# ---------------------------------------------------------------------------
# UserCognitiveProfile adaptive methods
# ---------------------------------------------------------------------------

class TestUserCognitiveProfileAdaptive:
    """Acceptance: profile adaptation and personalization methods."""

    @pytest.fixture
    def profile(self) -> UserCognitiveProfile:
        return UserCognitiveProfile(user_id="u1", spatial_expertise=0.5)

    def test_update_from_interaction_good_performance_increases_expertise(self, profile):
        """A good performance score on a complex task increases expertise."""
        original = profile.spatial_expertise
        profile.update_from_interaction(
            interaction_data={"task_complexity": 0.8, "interaction_type": "navigation"},
            outcome={"performance_score": 0.9, "cognitive_load": 0.3},
        )
        assert profile.spatial_expertise > original

    def test_update_from_interaction_poor_performance_decreases_expertise(self, profile):
        """A poor performance score decreases expertise."""
        original = profile.spatial_expertise
        profile.update_from_interaction(
            interaction_data={"task_complexity": 0.8, "interaction_type": "analysis"},
            outcome={"performance_score": 0.1, "cognitive_load": 0.8},
        )
        assert profile.spatial_expertise < original

    def test_update_from_interaction_records_history(self, profile):
        """Each interaction is appended to the performance history."""
        profile.update_from_interaction(
            interaction_data={"task_complexity": 0.5, "interaction_type": "search"},
            outcome={"performance_score": 0.7},
        )
        assert len(profile.task_performance_history) == 1
        entry = profile.task_performance_history[0]
        assert entry["interaction_type"] == "search"
        assert entry["performance_score"] == 0.7

    def test_calculate_task_suitability_returns_bounded_score(self, profile):
        """Task suitability is in [0, 1]."""
        score = profile.calculate_task_suitability(
            {"required_expertise": 0.5, "cognitive_style": "balanced", "cognitive_load": 0.5}
        )
        assert 0.0 <= score <= 1.0

    def test_calculate_task_suitability_higher_for_matching_expertise(self):
        """A user whose expertise matches the requirement scores higher."""
        expert = UserCognitiveProfile(user_id="e1", spatial_expertise=0.9)
        novice = UserCognitiveProfile(user_id="n1", spatial_expertise=0.1)
        reqs = {"required_expertise": 0.9, "cognitive_style": "balanced", "cognitive_load": 0.5}
        assert expert.calculate_task_suitability(reqs) > novice.calculate_task_suitability(reqs)

    def test_export_import_round_trip(self, profile):
        """export_profile → import_profile preserves key fields."""
        profile.update_from_interaction(
            interaction_data={"task_complexity": 0.6, "interaction_type": "planning"},
            outcome={"performance_score": 0.8},
        )
        exported = profile.export_profile()
        assert "user_id" in exported
        assert "spatial_expertise" in exported

        restored = UserCognitiveProfile.import_profile(exported)
        assert restored.user_id == profile.user_id
        assert abs(restored.spatial_expertise - profile.spatial_expertise) < 1e-9

    def test_get_profile_summary_has_required_fields(self, profile):
        """Profile summary contains essential fields."""
        summary = profile.get_profile_summary()
        assert "user_id" in summary
        assert "spatial_capabilities" in summary
        assert "cognitive_preferences" in summary
