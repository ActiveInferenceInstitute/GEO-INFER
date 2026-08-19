"""Contract test for directed multi-hazard compound exceedance analysis."""

from pathlib import Path

import numpy as np
import pytest

from geo_infer_risk import MultiHazardInteractionMatrix as PublicInteractionMatrix
from geo_infer_risk.core import (
    MultiHazardInteractionMatrix,
    calculate_compound_exceedance_probability,
)
from geo_infer_risk.core.risk_engine import EnhancedRiskEngine
from geo_infer_risk.utils.config_loader import load_config_with_defaults


def test_directed_interaction_matrix_and_risk_engine_compound_probability(
    tmp_path: Path,
) -> None:
    hazards = ["earthquake", "fire_following", "flood"]
    interactions = np.array(
        [
            [1.0, 0.5, 0.0],
            [0.0, 1.0, 0.4],
            [0.0, 0.0, 1.0],
        ]
    )
    probabilities = {
        "earthquake": 0.1,
        "fire_following": 0.2,
        "flood": 0.3,
    }
    expected = 0.1 * (0.2 + 0.5 * 0.8) * (0.3 + 0.4 * 0.7)

    matrix = MultiHazardInteractionMatrix(hazards, interactions)
    assert PublicInteractionMatrix is MultiHazardInteractionMatrix
    assert matrix.get_interaction("earthquake", "fire_following") == 0.5
    assert matrix.compound_exceedance_probability(probabilities) == pytest.approx(
        expected
    )
    assert calculate_compound_exceedance_probability(
        probabilities, interactions
    ) == pytest.approx(expected)

    independent = MultiHazardInteractionMatrix(hazards, np.eye(3))
    assert independent.compound_exceedance_probability(probabilities) == pytest.approx(
        0.1 * 0.2 * 0.3
    )
    matrix.set_interaction("earthquake", "fire_following", -0.5)
    assert matrix.conditional_exceedance_probability(
        "earthquake", "fire_following", 0.2
    ) == pytest.approx(0.1)

    config = load_config_with_defaults()
    config["general"]["output_directory"] = str(tmp_path / "outputs")
    config["general"]["cache_directory"] = str(tmp_path / "cache")
    config["general"]["num_workers"] = 1
    with EnhancedRiskEngine(config) as engine:
        engine.configure_hazard_interactions(hazards, interactions)
        assert engine.calculate_compound_exceedance_probability(
            probabilities
        ) == pytest.approx(expected)
        engine.set_hazard_interaction("fire_following", "flood", 0.0)
        assert engine.calculate_compound_exceedance_probability(
            probabilities
        ) == pytest.approx(0.1 * 0.6 * 0.3)

    with pytest.raises(ValueError, match="shape"):
        MultiHazardInteractionMatrix(hazards, np.eye(2))
    with pytest.raises(ValueError, match="between 0 and 1"):
        independent.compound_exceedance_probability(
            {**probabilities, "flood": 1.2}
        )
