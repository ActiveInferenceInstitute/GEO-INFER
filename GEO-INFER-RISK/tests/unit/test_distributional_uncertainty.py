"""Contract tests for distributional uncertainty in damage and exposure.

Covers the mean-centred parametric Beta, the empirical bootstrap over stored
damage observations, the curve uncertainty band, and the bootstrap / parametric
sampling of aggregate exposure.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from geo_infer_risk.core.exposure_model import EnhancedExposureModel
from geo_infer_risk.core.vulnerability_model import EnhancedVulnerabilityModel


# The default model loads the HAZUS flood/residential curve, whose damage ratio
# at intensity 2.0 is exactly on the grid (0.7).
FLOOD_INTENSITY = 2.0
EXPECTED_BASE = 0.7


def _parametric_model(seed: object = 11) -> EnhancedVulnerabilityModel:
    return EnhancedVulnerabilityModel(
        vulnerability_type="building",
        params={"uncertainty_method": "parametric", "random_seed": seed},
    )


def _bootstrap_model(seed: object = 5) -> EnhancedVulnerabilityModel:
    return EnhancedVulnerabilityModel(
        vulnerability_type="building",
        params={"uncertainty_method": "bootstrap", "random_seed": seed},
    )


class TestParametricBetaUncertainty:
    def test_beta_is_centred_on_the_damage_ratio(self) -> None:
        # A large sample from the curve band should average near the fitted ratio.
        model = _parametric_model(21)
        band = model.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, num_samples=20_000
        )
        assert band["deterministic_damage"] == pytest.approx(EXPECTED_BASE)
        assert abs(band["mean"] - EXPECTED_BASE) < 0.01

    def test_band_contains_the_deterministic_value_within_the_tail(self) -> None:
        model = _parametric_model(7)
        band = model.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY
        )
        assert band["band"]["low"] < EXPECTED_BASE < band["band"]["high"]

    def test_higher_concentration_tightens_the_band(self) -> None:
        wide = EnhancedVulnerabilityModel(
            "building", {"uncertainty_method": "parametric", "random_seed": 1}
        )
        wide.uncertainty_parameters["concentration"] = 5.0
        tight = EnhancedVulnerabilityModel(
            "building", {"uncertainty_method": "parametric", "random_seed": 1}
        )
        tight.uncertainty_parameters["concentration"] = 200.0
        wide_band = wide.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, num_samples=4000
        )
        tight_band = tight.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, num_samples=4000
        )
        wide_spread = wide_band["band"]["high"] - wide_band["band"]["low"]
        tight_spread = tight_band["band"]["high"] - tight_band["band"]["low"]
        assert wide_spread > tight_spread

    def test_seeded_models_are_replayable(self) -> None:
        first = _parametric_model(9)
        second = _parametric_model(9)
        a = first.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, num_samples=500
        )
        b = second.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, num_samples=500
        )
        assert a["band"] == b["band"]

    def test_rejects_an_out_of_range_confidence(self) -> None:
        model = _parametric_model()
        with pytest.raises(ValueError, match="confidence_level"):
            model.estimate_curve_uncertainty_band(
                "flood", "residential", FLOOD_INTENSITY, confidence_level=1.5
            )


class TestEmpiricalBootstrap:
    def test_observations_are_registered_and_returned_count(self) -> None:
        model = _bootstrap_model()
        count = model.add_damage_observations(
            "flood", "residential", [0.5, 0.6, 0.7, 0.8, 0.9]
        )
        assert count == 5
        assert model.empirical_damage_observations[("flood", "residential")].size == 5

    def test_rejects_out_of_range_observations(self) -> None:
        model = _bootstrap_model()
        with pytest.raises(ValueError, match="in \\[0, 1\\]"):
            model.add_damage_observations("flood", "residential", [0.5, 1.5])

    def test_bootstrap_resamples_observations_around_the_curve(self) -> None:
        model = _bootstrap_model(3)
        observations = np.linspace(0.5, 0.9, 40)  # centred near the fitted 0.7
        model.add_damage_observations("flood", "residential", observations.tolist())
        band = model.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, method="bootstrap", num_samples=8000
        )
        assert 0.0 < band["band"]["low"] <= band["band"]["high"] < 1.0
        # The observed spread (sd ~0.12) should widen the band well beyond the
        # parametric default.
        assert band["band"]["high"] - band["band"]["low"] > 0.2

    def test_uncertain_draw_with_observations_stays_bounded(self) -> None:
        model = _bootstrap_model(2)
        model.add_damage_observations(
            "flood", "residential", [0.0, 1.0, 0.5, 0.25, 0.75]
        )
        for _ in range(50):
            draw = model._apply_uncertainty(
                0.7, "flood", "residential"
            )
            assert 0.0 <= draw <= 1.0

    def test_bootstrap_without_observations_falls_back_to_parametric(self) -> None:
        model = _bootstrap_model(4)
        band = model.estimate_curve_uncertainty_band(
            "flood", "residential", FLOOD_INTENSITY, method="bootstrap",
            num_samples=2000,
        )
        assert band["band"]["low"] < EXPECTED_BASE < band["band"]["high"]


def _write_exposure_csv(path: Path) -> Path:
    import pandas as pd

    frame = pd.DataFrame(
        {
            "id": ["a", "b", "c", "d"],
            "longitude": [-122.4, -122.41, -122.42, -122.43],
            "latitude": [37.77, 37.78, 37.79, 37.80],
            "value": [100.0, 200.0, 300.0, 400.0],
            "type": ["residential", "residential", "commercial", "commercial"],
            "year_built": [1990, 2000, 2010, 2020],
        }
    )
    frame.to_csv(path, index=False)
    return path


class TestDistributionalExposure:
    @pytest.fixture
    def exposure_model(self, tmp_path: Path) -> EnhancedExposureModel:
        csv_path = _write_exposure_csv(tmp_path / "exposure.csv")
        return EnhancedExposureModel(
            "property",
            {"data_sources": [f"file://{csv_path}"]},
        )

    def test_deterministic_total_matches_the_book(self, exposure_model: EnhancedExposureModel) -> None:
        result = exposure_model.sample_total_exposure(method="deterministic")
        assert result["deterministic_total"] == pytest.approx(1000.0)
        assert result["total"] == pytest.approx(1000.0)

    def test_bootstrap_mean_approaches_the_deterministic_total(
        self, exposure_model: EnhancedExposureModel
    ) -> None:
        result = exposure_model.sample_total_exposure(
            method="bootstrap", num_samples=3000, random_seed=11
        )
        assert abs(result["total"] - 1000.0) < 50.0
        assert result["percentile_5"] <= result["total_median"] <= result["percentile_95"]

    def test_parametric_mean_approaches_the_deterministic_total(
        self, exposure_model: EnhancedExposureModel
    ) -> None:
        result = exposure_model.sample_total_exposure(
            method="parametric", num_samples=3000, random_seed=7
        )
        assert abs(result["total"] - 1000.0) < 100.0

    def test_seeded_sampling_is_replayable(
        self, exposure_model: EnhancedExposureModel
    ) -> None:
        a = exposure_model.sample_total_exposure(
            "bootstrap", 200, random_seed=42
        )
        b = exposure_model.sample_total_exposure(
            "bootstrap", 200, random_seed=42
        )
        assert a["samples"] == b["samples"]

    def test_rejects_bad_method_and_size(self, exposure_model: EnhancedExposureModel) -> None:
        with pytest.raises(ValueError, match="method"):
            exposure_model.sample_total_exposure(method="uniform")
        with pytest.raises(ValueError, match="num_samples"):
            exposure_model.sample_total_exposure(num_samples=0)

    def test_rejects_a_model_without_data(self) -> None:
        model = EnhancedExposureModel("property", {"data_sources": []})
        with pytest.raises(ValueError, match="exposure data"):
            model.sample_total_exposure()