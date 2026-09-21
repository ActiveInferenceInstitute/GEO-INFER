"""Unit tests for cognitive profile persistence helpers (M3-06).

Covers the exported helpers ``load_cognitive_profile`` and
``save_cognitive_model`` plus the exported ``ProfileManager`` class,
via real file round-trips in tmp_path.
"""

import json
from datetime import datetime

import pytest
import yaml

from geo_infer_cog import (
    ProfileManager,
    UserCognitiveProfile,
    load_cognitive_profile,
    save_cognitive_model,
)
from geo_infer_cog.utils.helpers import save_cognitive_profile


def _rich_profile(user_id: str) -> UserCognitiveProfile:
    """A profile with distinctive non-default field values."""
    return UserCognitiveProfile(
        user_id=user_id,
        spatial_expertise=0.75,
        cognitive_style="visualizer",
        learning_preference="fast",
        domain_experience={"gis": 0.8, "navigation": 0.6},
        navigation_preferences={"units": "metric"},
    )


class TestProfileFileRoundTrip:
    """save_cognitive_profile → load_cognitive_profile round-trips."""

    def test_round_trip_from_explicit_file(self, tmp_path) -> None:
        profile = _rich_profile("alice")
        path = tmp_path / "alice_profile.json"

        assert save_cognitive_profile(profile, path) is True
        assert path.is_file()

        loaded = load_cognitive_profile("alice", path)
        assert loaded is not None
        assert loaded.user_id == "alice"
        assert loaded.spatial_expertise == 0.75
        assert loaded.cognitive_style == "visualizer"
        assert loaded.learning_preference == "fast"
        assert loaded.domain_experience == {"gis": 0.8, "navigation": 0.6}
        assert loaded.navigation_preferences == {"units": "metric"}
        # Datetimes survive as datetime objects, not strings.
        assert isinstance(loaded.created_at, datetime)
        assert loaded.created_at == profile.created_at

    def test_round_trip_from_directory_lookup(self, tmp_path) -> None:
        """Passing a directory resolves ``<user_id>_profile.json`` inside it."""
        profile = _rich_profile("bob")
        profile_dir = tmp_path / "profiles"
        assert save_cognitive_profile(profile, profile_dir / "bob_profile.json") is True

        loaded = load_cognitive_profile("bob", profile_dir)
        assert loaded is not None
        assert loaded.user_id == "bob"
        assert loaded.spatial_expertise == 0.75

    def test_directory_lookup_for_other_user_returns_none(self, tmp_path) -> None:
        profile = _rich_profile("bob")
        profile_dir = tmp_path / "profiles"
        save_cognitive_profile(profile, profile_dir / "bob_profile.json")

        assert load_cognitive_profile("carol", profile_dir) is None

    def test_missing_profile_returns_none(self, tmp_path) -> None:
        assert load_cognitive_profile("nobody", tmp_path / "ghost.json") is None
        assert load_cognitive_profile("nobody", tmp_path / "missing_dir") is None


class TestSaveCognitiveModel:
    """save_cognitive_model writes parseable config files."""

    def test_json_round_trip(self, tmp_path) -> None:
        config = {
            "model_type": "reasoning",
            "parameters": {"depth": 3, "tolerance": 0.01},
            "layers": ["perception", "memory"],
        }
        path = tmp_path / "reasoning_model.json"

        assert save_cognitive_model(config, path) is True

        with open(path) as f:
            assert json.load(f) == config

    def test_yaml_round_trip(self, tmp_path) -> None:
        config = {
            "model_type": "perception",
            "parameters": {"scale": 2.5},
            "features": ["edges", "landmarks"],
        }
        path = tmp_path / "perception_model.yaml"

        assert save_cognitive_model(config, path) is True

        with open(path) as f:
            assert yaml.safe_load(f) == config

    def test_creates_missing_parent_directories(self, tmp_path) -> None:
        config = {"model_type": "memory"}
        path = tmp_path / "nested" / "deeper" / "memory_model.json"

        assert save_cognitive_model(config, path) is True
        assert path.is_file()


class TestProfileManager:
    """ProfileManager create/update/export/import behaviour."""

    def test_create_and_get_profile(self) -> None:
        manager = ProfileManager()
        profile = manager.create_profile("user-1", {"spatial_span": "large"})

        assert manager.get_profile("user-1") is profile
        # The initial assessment is recorded on the profile.
        assert profile.navigation_preferences["initial_assessment"] == {
            "spatial_span": "large"
        }
        assert manager.get_profile("unknown-user") is None

    def test_interaction_update_increases_expertise(self) -> None:
        """Strong performance on a hard task raises expertise deterministically.

        Base update: (1.0 - 0.5) * 1.0 * 0.1 = +0.05
        Learning: performance > 0.7 and difficulty > 0.5 → +0.1 * 0.8 = +0.08
        Total: 0.5 + 0.05 + 0.08 = 0.63 (adaptation is inert below 5 samples).
        """
        manager = ProfileManager()
        manager.create_profile("learner")

        manager.update_profile_from_interaction(
            "learner",
            interaction_data={
                "interaction_type": "map_reading",
                "task_complexity": 1.0,
                "task_difficulty": 0.8,
                "duration": 30,
            },
            outcome={"performance_score": 1.0, "cognitive_load": 0.6},
        )

        profile = manager.get_profile("learner")
        assert profile is not None
        assert profile.spatial_expertise == pytest.approx(0.63)
        assert profile.task_performance_history[-1]["performance_score"] == 1.0
        assert "map_reading" in profile.interaction_patterns

    def test_update_creates_missing_profile(self) -> None:
        manager = ProfileManager()
        manager.update_profile_from_interaction(
            "newcomer",
            interaction_data={"interaction_type": "wayfinding", "task_complexity": 0.5},
            outcome={"performance_score": 0.5},
        )
        assert manager.get_profile("newcomer") is not None

    def test_export_import_round_trip(self) -> None:
        source = ProfileManager()
        created = source.create_profile("drifter")
        created.spatial_expertise = 0.9
        created.domain_experience = {"cartography": 0.85}

        exported = source.export_all_profiles()
        assert exported["profile_count"] == 1
        assert "drifter" in exported["profiles"]

        target = ProfileManager()
        imported_count = target.import_profiles(exported)
        assert imported_count == 1

        restored = target.get_profile("drifter")
        assert restored is not None
        assert restored.spatial_expertise == 0.9
        assert restored.domain_experience == {"cartography": 0.85}
