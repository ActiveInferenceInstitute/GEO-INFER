"""Regression tests for the risk-engine lifecycle and reproducibility contract."""

from pathlib import Path

import pandas as pd
import pytest

from geo_infer_risk.core.hazard_model import EnhancedHazardModel
from geo_infer_risk.core.risk_engine import EnhancedRiskEngine
from geo_infer_risk.utils.config_loader import load_config_with_defaults


def engine_config(tmp_path: Path) -> dict:
    config = load_config_with_defaults()
    config["general"]["output_directory"] = str(tmp_path / "outputs")
    config["general"]["cache_directory"] = str(tmp_path / "cache")
    config["general"]["num_workers"] = 1
    config["general"]["random_seed"] = 17
    config["risk_model"]["random_seed"] = 17
    return config


def configured_hazard() -> EnhancedHazardModel:
    model = EnhancedHazardModel("flood", {"random_seed": 17})
    model.historical_data = pd.DataFrame(
        {
            "event_id": ["a", "b", "c"],
            "intensity": [1.0, 2.0, 3.0],
        }
    )
    return model


def test_engine_context_closes_executor_and_rejects_new_work(tmp_path: Path) -> None:
    with EnhancedRiskEngine(engine_config(tmp_path)) as engine:
        assert engine.get_integration_status()["spatial_indexing"] is True
        assert engine._closed is False

    assert engine._closed is True
    with pytest.raises(RuntimeError, match="closed"):
        engine.run_monte_carlo_analysis(num_iterations=1)


def test_engine_event_sampling_is_reproducible_without_global_rng(
    tmp_path: Path,
) -> None:
    first_engine = EnhancedRiskEngine(engine_config(tmp_path / "first"))
    second_engine = EnhancedRiskEngine(engine_config(tmp_path / "second"))
    try:
        first_engine.hazard_models["flood"] = configured_hazard()
        second_engine.hazard_models["flood"] = configured_hazard()

        first_events = [first_engine._generate_random_event() for _ in range(5)]
        second_events = [second_engine._generate_random_event() for _ in range(5)]

        assert first_events == second_events
    finally:
        first_engine.close()
        second_engine.close()


def test_engine_rejects_underspecified_calibration(tmp_path: Path) -> None:
    with EnhancedRiskEngine(engine_config(tmp_path)) as engine:
        with pytest.raises(ValueError, match="at least two"):
            engine.calibrate_models({"samples": []})
        with pytest.raises(ValueError, match="BayesianModel adapter"):
            engine.calibrate_models(
                {"samples": [{"loss": 1.0}, {"loss": 2.0}]}, "bayesian"
            )
