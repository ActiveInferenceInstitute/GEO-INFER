"""Contract tests for the enhanced multi-hazard compound-exceedance surface.

Covers the directed interaction matrix ergonomics (``from_mapping``,
``set_interactions``), the union (``joint``) exceedance across several compound
paths, the enumeration of every non-repeating branch, and the dominant-path
ranking, plus their delegation through the risk engine.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from geo_infer_risk.core import MultiHazardInteractionMatrix
from geo_infer_risk.core.catastrophe_models import CatastropheModelManager
from geo_infer_risk.core.risk_engine import EnhancedRiskEngine
from geo_infer_risk.utils.config_loader import load_config_with_defaults


def _three_hazard_matrix(
    eq_fire: float, fire_flood: float
) -> MultiHazardInteractionMatrix:
    return MultiHazardInteractionMatrix.from_mapping(
        ["earthquake", "fire_following", "flood"],
        {
            ("earthquake", "fire_following"): eq_fire,
            ("fire_following", "flood"): fire_flood,
        },
    )


class TestInteractionMatrixConstruction:
    def test_from_mapping_builds_sparse_directed_matrix(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        assert matrix.get_interaction("earthquake", "fire_following") == 0.5
        assert matrix.get_interaction("fire_following", "flood") == 0.4
        # Unspecified off-diagonal pairs stay independent; diagonals are one.
        assert matrix.get_interaction("earthquake", "flood") == 0.0
        assert matrix.get_interaction("earthquake", "earthquake") == 1.0

    def test_set_interactions_updates_many_at_once(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        matrix.set_interactions(
            {
                ("earthquake", "flood"): 0.2,
                ("flood", "fire_following"): -0.1,
            }
        )
        assert matrix.get_interaction("earthquake", "flood") == 0.2
        assert matrix.get_interaction("flood", "fire_following") == -0.1

    def test_set_interactions_rejects_an_out_of_range_strength(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        with pytest.raises(ValueError, match="between -1 and 1"):
            matrix.set_interactions({("earthquake", "flood"): 1.5})


class TestJointExceedance:
    def test_union_of_two_singletons_matches_closed_form(self) -> None:
        matrix = MultiHazardInteractionMatrix(["feq", "fire"])
        probabilities = {"feq": 0.1, "fire": 0.2}
        expected = 1.0 - (1.0 - 0.1) * (1.0 - 0.2)
        assert matrix.joint_exceedance_probability(
            probabilities, [("feq",), ("fire",)]
        ) == pytest.approx(expected)

    def test_independent_joint_paths_are_products(self) -> None:
        matrix = MultiHazardInteractionMatrix(["a", "b"])
        probabilities = {"a": 0.3, "b": 0.4}
        # Independent compound single path: p_a * p_b.
        single = matrix.compound_exceedance_probability(
            probabilities, ["a", "b"]
        )
        assert single == pytest.approx(0.12)
        # The same 2-hazard ordering via the union API is also a single path.
        result = matrix.joint_exceedance_probability(
            probabilities, [("b", "a")]
        )
        assert result == pytest.approx(0.12)

    def test_interactions_raise_the_union_probability(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        probabilities = {
            "earthquake": 0.1,
            "fire_following": 0.2,
            "flood": 0.3,
        }
        coupling = matrix.compound_exceedance_probability(
            probabilities, ["earthquake", "fire_following", "flood"]
        )
        assert matrix.joint_exceedance_probability(
            probabilities, [("earthquake", "fire_following", "flood")]
        ) == pytest.approx(coupling)
        # Adding a second independent compound path raises the union.
        widened = matrix.joint_exceedance_probability(
            probabilities,
            [("earthquake", "fire_following", "flood"), ("flood",)],
        )
        assert widened >= coupling

    def test_rejects_a_repeating_path(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        probabilities = {"earthquake": 0.1, "fire_following": 0.2, "flood": 0.3}
        with pytest.raises(ValueError, match="repeat"):
            matrix.joint_exceedance_probability(
                probabilities, [("earthquake", "earthquake")]
            )

    def test_rejects_an_unknown_hazard(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        probabilities = {"earthquake": 0.1, "fire_following": 0.2, "flood": 0.3}
        with pytest.raises(KeyError, match="Unknown hazards"):
            matrix.joint_exceedance_probability(probabilities, [("tsunami",)])


class TestBranchEnumeration:
    def test_singletons_record_the_independent_baseline(self) -> None:
        matrix = MultiHazardInteractionMatrix(["a", "b", "c"])
        probabilities = {"a": 0.1, "b": 0.2, "c": 0.3}
        branches = matrix.branch_exceedance_probabilities(probabilities)
        assert branches[("a",)] == pytest.approx(0.1)
        assert branches[("c",)] == pytest.approx(0.3)

    def test_all_one_step_paths_are_enumerated(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        probabilities = {"earthquake": 0.1, "fire_following": 0.2, "flood": 0.3}
        branches = matrix.branch_exceedance_probabilities(probabilities)
        # Pairs count = 3P2 = 6, singles = 3, triples = 3P3 = 6 -> 15 total.
        assert len(branches) == 15
        two_step_pairs = [k for k in branches if len(k) == 2]
        assert len(two_step_pairs) == 6

    def test_max_path_length_bounds_enumeration(self) -> None:
        matrix = _three_hazard_matrix(0.5, 0.4)
        probabilities = {"earthquake": 0.1, "fire_following": 0.2, "flood": 0.3}
        branches = matrix.branch_exceedance_probabilities(
            probabilities, max_path_length=2
        )
        assert all(len(key) <= 2 for key in branches)
        assert len(branches) == 9  # 3 + 6

    def test_dominant_path_is_the_max(self) -> None:
        matrix = MultiHazardInteractionMatrix(["low", "high"])
        probabilities = {"low": 0.9, "high": 0.5}
        path, prob = matrix.dominant_exceedance_path(probabilities)
        assert path == ("low",)
        assert prob == pytest.approx(0.9)


class TestEngineDelegation:
    def test_engine_exposes_the_compound_surface(
        self, tmp_path: Path
    ) -> None:
        config = load_config_with_defaults()
        config["general"]["output_directory"] = str(tmp_path / "outputs")
        config["general"]["cache_directory"] = str(tmp_path / "cache")
        config["general"]["num_workers"] = 1
        probabilities = {
            "earthquake": 0.1,
            "fire_following": 0.2,
            "flood": 0.3,
        }
        hazards = ["earthquake", "fire_following", "flood"]
        interactions = np.array(
            [
                [1.0, 0.5, 0.0],
                [0.0, 1.0, 0.4],
                [0.0, 0.0, 1.0],
            ]
        )
        with EnhancedRiskEngine(config) as engine:
            engine.configure_hazard_interactions(hazards, interactions.tolist())
            single = engine.calculate_compound_exceedance_probability(
                probabilities, ("earthquake", "fire_following", "flood")
            )
            assert engine.calculate_joint_exceedance_probability(
                probabilities,
                [("earthquake", "fire_following", "flood")],
            ) == pytest.approx(single)
            branches = engine.get_branch_exceedance_probabilities(probabilities)
            assert branches[("earthquake",)] == pytest.approx(0.1)
            dominant, prob = engine.get_dominant_hazard_path(probabilities)
            assert probabilities[dominant[0]] == pytest.approx(prob)


class TestManagerDelegation:
    def test_manager_rows_match_the_matrix(self) -> None:
        manager = CatastropheModelManager()
        hazards = ["a", "b"]
        manager.configure_hazard_interactions(
            hazards, np.array([[1.0, 0.6], [0.2, 1.0]]).tolist()
        )
        probabilities = {"a": 0.2, "b": 0.5}
        path_prob = manager.branch_exceedance_probabilities(probabilities)[
            ("a", "b")
        ]
        assert path_prob == pytest.approx(0.2 * (0.5 + 0.6 * 0.5))
        assert manager.joint_exceedance_probability(
            probabilities, [("a",), ("b",)]
        ) == pytest.approx(1.0 - (1.0 - 0.2) * (1.0 - 0.5))
        dominant, prob = manager.dominant_exceedance_path(probabilities)
        assert dominant == ("b",)
        assert prob == pytest.approx(0.5)